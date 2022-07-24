import asyncio
import json
import logging
import os
import tempfile
import time
from pathlib import Path

import aiofiles
import aiomysql
from bscscan import BscScan

ADDRESS_PRINT_INTERVAL = 100


async def read_json(path):
    if os.path.isfile(path):
        async with aiofiles.open(path, mode='r') as f:
            contents = await f.read()
        return json.loads(contents)
    return {}


def save_json(path, res, safe_save=True):
    # First write to a temp file and then to the original
    if safe_save:
        temp = tempfile.NamedTemporaryFile(mode="w+")
        json.dump(res, temp)
        temp.flush()
        output_file = Path(path)
        output_file.parent.mkdir(exist_ok=True, parents=True)
        output_file.write_text(json.dumps(res))
        temp.close()  # Remove temporary file
    else:
        output_file = Path(path)
        output_file.parent.mkdir(exist_ok=True, parents=True)
        output_file.write_text(json.dumps(res))


async def select(loop, sql, pool):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(sql)
            response = await cur.fetchall()
            return response


async def update(loop, sql, pool, values):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.executemany(sql, values)
            await conn.commit()
            return cur.rowcount


async def async_requestor(loop, output, api_key, errors_src, debug, limit_checker):
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')

    addresses = list()  # Addresses to crawl

    start = time.time()

    pool = await aiomysql.create_pool(
        user="root",
        password="Fm)4dj",
        host="127.0.0.1",
        port=3333,
        db="db_blockchain",
        loop=loop)

    response = await select(loop=loop, sql="SELECT address "
                                           "FROM bsc",
                            pool=pool)

    for address in response:
        addresses.append(address[0])
    nr_contracts = len(addresses)

    # Divide addresses into lists of 20
    addresses_in_chunks = [addresses[i:i + 20] for i in range(0, len(addresses), 20)]

    results_old = await read_json(output)
    results_new = dict()
    exceptions_dict = dict()

    print(f"BscScan API Key         {api_key}")
    print(f"No. of contracts        {nr_contracts}")
    print(f"Output file             {output}")
    print(f"Errors file             {errors_src}")
    print()

    values = list()
    skipped_addresses = 0
    async with BscScan(api_key) as client:
        limit_checker.start()
        # The loop is needed as the method only returns the balance of only the first 20 addresses,
        # so we send them in batches of 20
        balances = list()
        for address_chunk in addresses_in_chunks:
            limit_checker.check()
            balances.append(await client.get_bnb_balance_multiple(addresses=address_chunk))

        for index, address in enumerate(addresses):
            if address in results_old:  # Info about address has already been crawled
                skipped_addresses += 1
                if debug:
                    logging.info(f"Skipping address {address}")
                continue

            address_result = {'balance': None,
                              'nr_transactions': None,
                              'nr_token_transfers': None}
            exceptions = list()
            nr_transactions = 0
            bep20_tokens = 0
            bep721_tokens = 0

            if index % ADDRESS_PRINT_INTERVAL == 0:
                percent = index / len(addresses) * 100
                print("Processing address {} / {} ({:.2f}%)".format(index, len(addresses), percent))

            limit_checker.check()
            try:
                # Note: The following API endpoint returns a maximum of 10000 records only.
                # This is fine for us, as we only care if at least one record exists.
                nr_transactions = len(await client.get_normal_txs_by_address(
                    address=address, startblock=0, endblock=99999999, sort="asc"))
            except Exception as e:
                exceptions.append("Normal txs -- " + str(e))
                if debug:
                    logging.info(f"{address} | Normal txs -- {e}")

            limit_checker.check()
            try:
                bep20_tokens = len(await client.get_bep20_token_transfer_events_by_contract_address_paginated(
                    contract_address=address, page=0, offset=0, sort="asc"))
            except Exception as e:
                exceptions.append("BEP20 -- " + str(e))
                if debug:
                    logging.info(f"{address} | BEP20 -- {e}")

            limit_checker.check()
            try:
                bep721_tokens = len(await client.get_bep721_token_transfer_events_by_contract_address_paginated(
                    contract_address=address, page=0, offset=0, sort="asc"))
            except Exception as e:
                exceptions.append("BEP721 -- " + str(e))
                if debug:
                    logging.info(f"{address} | BEP721 -- {e}")

            nr_token_transfers = bep20_tokens + bep721_tokens

            index_exists = False
            for balance_chunk in balances[int(index / 20)]:
                if balance_chunk['account'] == address:
                    values.append((nr_transactions, balance_chunk['balance'], nr_token_transfers, address))
                    address_result["balance"] = balance_chunk['balance']
                    index_exists = True
                    break

            if not index_exists:
                values.append((nr_transactions, 0, nr_token_transfers, address))
                address_result["balance"] = 0

            address_result["nr_transactions"] = nr_transactions
            address_result["nr_token_transfers"] = nr_token_transfers
            results_new[address] = address_result
            exceptions_dict[address] = exceptions

    row_count = await update(loop=loop, sql="UPDATE bsc "
                                            "SET nr_transactions = %s, balance = %s, nr_token_transfers = %s "
                                            "WHERE address = %s",
                             pool=pool, values=values)

    end = time.time()
    elapsed = end - start

    print()
    print("=" * 30)
    print("Finished crawling BscScan")
    print(f"{row_count} record(s) affected")
    print(f"Elapsed time: {elapsed:.2f} seconds")
    print(f"Smart contracts crawled: {nr_contracts - skipped_addresses}")
    print(f"Smart contracts skipped: {skipped_addresses}")
    print(f"Total requests to BscScan API: {limit_checker.total_requests}")
    print("=" * 30)
    print()

    output = "data/logs/" + time.strftime("%d%m%Y_%H%M%S") + "/" + output
    errors_src = "data/logs/" + time.strftime("%d%m%Y_%H%M%S") + "/" + errors_src
    save_json(output, {**results_old, **results_new}, safe_save=False)
    save_json(errors_src, exceptions_dict, safe_save=False)

    pool.close()
    await pool.wait_closed()


def run_async_requestor(output, api_key, errors_src, debug, limit_checker):
    cur_loop = asyncio.get_event_loop()
    cur_loop.run_until_complete(async_requestor(cur_loop, output, api_key, errors_src, debug, limit_checker))
    cur_loop.close()
