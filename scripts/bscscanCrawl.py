import argparse
import asyncio
import logging
import time

import aiomysql
from bscscan import BscScan

ADDRESS_PRINT_INTERVAL = 5


def get_args():
    # Argument parsing
    args = argparse.ArgumentParser(
        prog="Crawler",
        description="Crawl the BscScan.io blockchain explorer to get extra details about contracts."
    )
    args.add_argument("--apikey", dest="api_key",
                      help="API Key of blockchain explorer")
    # args.add_argument("output", help="JSON file path to save the results")
    return args.parse_args()


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


async def main(loop):
    args = get_args()
    # output = args.output
    api_key = args.api_key
    # Addresses to crawl
    addresses = list()

    start = time.time()

    # crawler = Crawler(args.api_key)
    # crawler.cur.execute(f"SELECT address FROM bsc")

    pool = await aiomysql.create_pool(
        user="root",
        password="Fm)4dj",
        host="127.0.0.1",
        port=3333,
        db="db_blockchain",
        loop=loop)
    response = await select(loop=loop, sql="SELECT address FROM bsc", pool=pool)

    for address in response:
        addresses.append(address[0])
    nr_contracts = len(addresses)

    # #results = read_json(output)

    print(f"BscScan API Key         {api_key}")
    print(f"No. of contracts        {nr_contracts}")
    # print(f"Output file            {output}")
    print()

    values = list()
    # sql_stmt = f"UPDATE bsc SET nr_transactions = %s, balance = %s, nr_token_transfers = %s WHERE address = %s"

    async with BscScan(api_key) as client:
        balances = await client.get_bnb_balance_multiple(addresses=addresses)
        print(balances)
        for index, address in enumerate(addresses):
            # Note : Some API endpoint returns a maximum of 10000 records only.
            # This is fine for us, as we only care if at least one record exists.
            nr_transactions = 0
            bep20_tokens = 0
            bep721_tokens = 0

            if index % ADDRESS_PRINT_INTERVAL == 0:
                percent = index / len(addresses) * 100
                print("Processing address {} / {} ({:.2f}% complete)".format(index, len(addresses), percent))

            try:
                nr_transactions = len(await client.get_normal_txs_by_address(
                    address=address, startblock=0, endblock=99999999, sort="asc"))
            except Exception as e:
                logging.info(f"{address} | Normal txs -- {e}")

            try:
                bep20_tokens = len(await client.get_bep20_token_transfer_events_by_contract_address_paginated(
                    contract_address=address, page=0, offset=0, sort="asc"))
            except Exception as e:
                logging.info(f"{address} | BEP20 -- {e}")

            try:
                bep721_tokens = len(await client.get_bep721_token_transfer_events_by_contract_address_paginated(
                    contract_address=address, page=0, offset=0, sort="asc"))
            except Exception as e:
                logging.info(f"{address} | BEP721 -- {e}")

            nr_token_transfers = bep20_tokens + bep721_tokens

            index_exists = False
            for balance in balances:
                if balance['account'] == address:
                    values.append((nr_transactions, int(balance['balance']), nr_token_transfers, address))
                    index_exists = True
                    break

            if not index_exists:
                values.append((nr_transactions, 0, nr_token_transfers, address))

    row_count = await update(loop=loop, sql="UPDATE bsc "
                                            "SET nr_transactions = %s, balance = %s, nr_token_transfers = %s "
                                            "WHERE address = %s",
                             pool=pool, values=values)

    end = time.time()
    elapsed = end - start
    logging.info("Finished crawling bscscan")
    logging.info(f"{row_count} record(s) affected.")
    logging.info(f"Elapsed time: {elapsed} seconds")

    pool.close()
    await pool.wait_closed()


if __name__ == "__main__":
    cur_loop = asyncio.get_event_loop()
    cur_loop.run_until_complete(main(cur_loop))
    cur_loop.close()
    # asyncio.run(main())
