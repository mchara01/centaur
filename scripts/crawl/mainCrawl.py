""" Main Crawling Script

The entry point for executing the blockchain explorer crawling scripts for
Ethereum and BSC. Here the arguments the user provided are parsed and
passed to the appropriate script.

The two crawling scripts are imported as modules. An API key must be provided
and an errors and results file is optional.

Example usage: python scripts/crawl/mainCrawl.py --chain eth --apikey <ENTER_API_KEY_HERE> --output data/logs/results_eth.json
 --invalid data/logs/exceptions_eth.json
"""

import argparse

from limitChecker import LimitChecker
from etherscanCrawl import requestor
from bscscanCrawl import run_async_requestor

DEBUG = False
LIMIT_CHECKER = LimitChecker(debug=DEBUG)


def get_args():
    # Argument parsing
    args = argparse.ArgumentParser(
        prog="Crawler",
        description="Crawl the EtherScan.io or BscScan.io blockchain explorers to get extra details for smart "
                    "contracts"
    )
    args.add_argument("--chain", dest="chain", default="eth",
                      help="Choose chain to crawl between ETH and BSC")
    args.add_argument("--apikey", dest="api_key",
                      help="API Key of blockchain explorer")
    args.add_argument("--invalid", dest="invalid", default="data/logs/exceptions_eth.json",
                      help="Path to errors JSON file")
    args.add_argument("--output", dest="output", default="data/logs/results_eth.json",
                      help="JSON file path to save the results")
    return args.parse_args()


def main():
    args = get_args()
    output = args.output
    api_key = args.api_key
    errors_src = args.invalid

    if args.chain == "eth":
        requestor(output, api_key, errors_src, DEBUG, LIMIT_CHECKER)
    elif args.chain == "bsc":
        run_async_requestor(output, api_key, errors_src, DEBUG, LIMIT_CHECKER)
    else:
        print("Chain name given invalid. Choose between 'eth' and 'bsc'.")


if __name__ == "__main__":
    main()
