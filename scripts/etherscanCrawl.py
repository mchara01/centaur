import argparse
import sys
import mysql.connector
import logging

from etherscan import Etherscan

class Crawler:
    def __init__(self, api_key, chain):
        logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')
        self.api_key = api_key
        self.chain = chain
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
        description="Crawl blockchain explorer (EtherScan.io or BscScan.io) to get extra details about contracts."
    )
    args.add_argument("--apikey", dest="api_key", help="API Key of blockchain explorer")
    args.add_argument("--chain", dest="chain", help="Name of EVM-based chain to crawl (eth, bsc)", default="eth",)
    #args.add_argument("output", help="JSON file path to save the results")
    return args.parse_args()


def main():
    args = get_args()
    #output = args.output

    # Addresses to crawl
    addresses = list()

    crawler = Crawler(args.api_key, args.chain)
    crawler.cur.execute(f"SELECT address FROM {crawler.chain}")
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
    sql_stmt = f"UPDATE {crawler.chain} SET nr_transactions = %s, balance = %s WHERE address = %s"
    for index,address in enumerate(addresses):
        try:
            # Note : This API endpoint returns a maximum of 10000 records only.
            nr_transactions = len(eth.get_normal_txs_by_address(address=address, startblock=0, endblock=99999999, sort="asc"))
            values.append((nr_transactions, balances[index]['balance'], address))
        except Exception as e: # "No transactions for address "
            logging.info(f"No transactions for address {address}")

    crawler.cur.executemany(sql_stmt, values)
    crawler.conn.commit()
    logging.info(f"{crawler.cur.rowcount} record(s) affected.")

if __name__ == "__main__":
    main()