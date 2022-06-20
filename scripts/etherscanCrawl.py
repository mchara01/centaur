import argparse
import sys
import mysql.connector
import logging

from etherscan import Etherscan

ADDRESS_PRINT_INTERVAL = 3


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


def get_args():
    # Argument parsing
    args = argparse.ArgumentParser(
        prog="Crawler",
        description="Crawl the EtherScan.io blockchain explorer to get extra details about contracts."
    )
    args.add_argument("--apikey", dest="api_key",
                      help="API Key of blockchain explorer")
    #args.add_argument("output", help="JSON file path to save the results")
    return args.parse_args()


def main():
    args = get_args()
    #output = args.output

    # Addresses to crawl
    addresses = list()

    crawler = Crawler(args.api_key)
    crawler.cur.execute(f"SELECT address FROM eth")
    for address in crawler.cur:
        addresses.append(address[0])
    nr_contracts = len(addresses)

    # #results = read_json(output)

    print(f"Etherscan API Key       {crawler.api_key}")
    print(f"No. of contracts        {nr_contracts}")
    #print(f"Output file            {output}")
    print()

    eth = Etherscan(crawler.api_key)
    values = list()
    balances = eth.get_eth_balance_multiple(addresses)
    sql_stmt = f"UPDATE eth SET nr_transactions = %s, balance = %s, nr_token_transfers = %s WHERE address = %s"

    for index, address in enumerate(addresses):
        # Note : Some API endpoint returns a maximum of 10000 records only.
        # This is fine for us, as we only care if atleast one record exists.
        nr_transactions = 0
        erc20_tokens = 0
        erc721_tokens = 0

        if index % ADDRESS_PRINT_INTERVAL == 0:
            percent = index / len(addresses) * 100
            print("Processing address {} / {} ({:.2f}% complete)".format(index,
                  len(addresses), percent))

        try:
            nr_transactions = len(eth.get_normal_txs_by_address(
                address=address, startblock=0, endblock=99999999, sort="asc"))
        except Exception as e:
            logging.info(f"{address} | Normal txs -- {e}")

        try:
            erc20_tokens = len(eth.get_erc20_token_transfer_events_by_contract_address_paginated(
                contract_address=address, page=0, offset=0, sort="asc"))
        except Exception as e:
            logging.info(f"{address} | ERC20 -- {e}")

        try:
            erc721_tokens = len(eth.get_erc721_token_transfer_events_by_contract_address_paginated(
                contract_address=address, page=0, offset=0, sort="asc"))
        except Exception as e:
            logging.info(f"{address} | ERC721 -- {e}")

        nr_token_transfers = erc20_tokens + erc721_tokens
        values.append(
            (nr_transactions, balances[index]['balance'], nr_token_transfers, address))

    crawler.cur.executemany(sql_stmt, values)
    crawler.conn.commit()
    print("DONE")
    print(f"{crawler.cur.rowcount} record(s) affected.")


if __name__ == "__main__":
    main()
