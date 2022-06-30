import json
import logging
import os
import sys
import tempfile
import time

import mysql.connector
from etherscan import Etherscan

ADDRESS_PRINT_INTERVAL = 5


class Crawler:
    def __init__(self, api_key):
        logging.basicConfig(level=logging.INFO,
                            format='[%(asctime)s] %(message)s')
        self.api_key = api_key
        try:
            # Connect to MariaDB Platform
            self.conn = mysql.connector.connect(
                user="root",
                password="Fm)4dj",
                host="127.0.0.1",
                port=3333,
                database="db_blockchain"
            )
            self.cur = self.conn.cursor()
        except mysql.connector.connect.Error as e:
            print(f"Error connecting to MariaDB: {e}")
            sys.exit(1)

    def __del__(self):
        self.cur.close()
        self.conn.close()


def read_results_json(path):
    if os.path.isfile(path):
        with open(path, 'r') as f:
            return json.load(f)
    return {}


def read_errors_json(errors_src):
    directory = os.path.dirname(errors_src)
    if os.path.exists(errors_src):
        with open(errors_src, 'r') as fd:
            return json.load(fd)
    os.makedirs(directory, exist_ok=True)
    return {}


def save_json(path, res, safe_save=True):
    # First write to a temp file and then to the original
    if safe_save:
        temp = tempfile.NamedTemporaryFile(mode="w+")
        json.dump(res, temp)
        temp.flush()
        with open(path, 'w') as f:
            json.dump(res, f)
        temp.close()  # Remove temporary file
    else:
        with open(path, 'w') as f:
            json.dump(res, f)


def requestor(output, api_key, errors_src, debug, limit_checker):
    start = time.time()

    # Addresses to crawl
    addresses = list()
    crawler = Crawler(api_key)
    crawler.cur.execute(f"SELECT address FROM eth")

    for address in crawler.cur:
        addresses.append(address[0])
    nr_contracts = len(addresses)

    # Divide addresses into lists of 20
    addresses_in_chunks = [addresses[i:i + 20] for i in range(0, len(addresses), 20)]

    print(f"Etherscan API Key       {api_key}")
    print(f"No. of contracts        {nr_contracts}")
    print(f"Results file            {output}")
    print(f"Errors file             {errors_src}")
    print()

    eth = Etherscan(crawler.api_key)
    limit_checker.start()
    skipped_addresses = 0
    results_old = read_results_json(output)
    results_new = dict()
    exceptions_dict = dict()
    values = list()

    # The loop is needed as the method only returns the balance of only the first 20 addresses,
    # so we send them in batches of 20
    balances = list()
    for address_chunk in addresses_in_chunks:
        limit_checker.check()
        balances.append(eth.get_eth_balance_multiple(addresses=address_chunk))

    sql_stmt = f"UPDATE eth SET nr_transactions = %s, balance = %s, nr_token_transfers = %s WHERE address = %s"

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
        erc20_tokens = 0
        erc721_tokens = 0

        if index % ADDRESS_PRINT_INTERVAL == 0:
            percent = index / len(addresses) * 100
            print("Processing address {} / {} ({:.2f}% complete)".format(index, len(addresses), percent))

        limit_checker.check()
        try:
            # Note: The following API endpoint returns a maximum of 10000 records only.
            # This is fine for us, as we only care if at least one record exists.
            nr_transactions = len(eth.get_normal_txs_by_address(
                address=address, startblock=0, endblock=99999999, sort="asc"))
        except Exception as e:
            exceptions.append("Normal txs -- " + str(e))
            if debug:
                logging.info(f"{address} | Normal txs -- {e}")

        limit_checker.check()
        try:
            erc20_tokens = len(eth.get_erc20_token_transfer_events_by_contract_address_paginated(
                contract_address=address, page=0, offset=0, sort="asc"))
        except Exception as e:
            exceptions.append("ERC20 -- " + str(e))
            if debug:
                logging.info(f"{address} | ERC20 -- {e}")

        limit_checker.check()
        try:
            erc721_tokens = len(eth.get_erc721_token_transfer_events_by_contract_address_paginated(
                contract_address=address, page=0, offset=0, sort="asc"))
        except Exception as e:
            exceptions.append("ERC721 -- " + str(e))
            if debug:
                logging.info(f"{address} | ERC721 -- {e}")

        nr_token_transfers = erc20_tokens + erc721_tokens

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

    crawler.cur.executemany(sql_stmt, values)
    crawler.conn.commit()

    end = time.time()
    elapsed = end - start

    print()
    print("=" * 30)
    print("Finished crawling Etherscan")
    print(f"{crawler.cur.rowcount} record(s) affected.")
    print(f"Elapsed time: {elapsed:.2f} seconds")
    print(f"Smart contracts crawled: {nr_contracts - skipped_addresses}")
    print(f"Smart contracts skipped: {skipped_addresses}")
    print(f"Total requests to Etherscan API: {limit_checker.total_requests}")
    print("=" * 30)
    print()

    save_json(output, {**results_old, **results_new})
    save_json(errors_src, exceptions_dict)
