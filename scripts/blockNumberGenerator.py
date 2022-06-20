# Example: python3 blockNumberGenerator.py --size 100 --chain bsc --output blockNumbersBsc.txt --apikey <API_KEY>
import requests
import random
import argparse
import time

# Argument parsing
args = argparse.ArgumentParser(
    description="Random block number generator."
)
args.add_argument("--size", dest="size", help="Block sample size", default=5)
args.add_argument("--output", dest="output",
                  help="Output file that will contain the generated block numbers", default="blockNumbersEth.txt")
args.add_argument("--chain", dest="chain", help="Name of EVM-based chain to crawl (eth, bsc)", default="eth")
args.add_argument("--apikey", dest="apikey", help="API key for BscScan only")

args = args.parse_args()

SAMPLE_FILE = args.output
BLOCK_SAMPLE_SIZE = int(args.size)
block_sample = list()

if args.chain == "eth":
    response = requests.get("https://api.blockcypher.com/v1/eth/main")
    latest_block = response.json()["height"]
elif args.chain == "bsc":
    timestamp = int(time.time()) 
    response = requests.get(f'https://api.bscscan.com/api?module=block&action=getblocknobytime&timestamp={timestamp}&closest=before&apikey={args.apikey}')
    if "Error" in response.text:
        print("Error in request to BscScan.")
        exit()
    latest_block = int(response.json()["result"])
else:
    print("Please enter a valid chain name from [eth, bsc].")
    exit()

block_range = range(1, latest_block + 1)
block_sample = sorted(random.sample(block_range, BLOCK_SAMPLE_SIZE))

with open(SAMPLE_FILE, 'w') as f:
    for block in block_sample:
        f.write("%s\n" % str(block))
    print('Saved blocks sample of {} in file {} on disk.'.format(
        len(block_sample), SAMPLE_FILE))
    percentage = len(block_sample)/latest_block
    print("Total number of blocks in blockchain: {}".format(latest_block))
    print("Percentage: {:.5f}%".format(percentage))