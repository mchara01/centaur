import requests
import random
import argparse

# Argument parsing
args = argparse.ArgumentParser(
    description="Random block number generator."
)
args.add_argument("--size", dest="size", help="Block sample size", default=5)
args.add_argument("--output", dest="output",
                  help="Output file that will contain the generated block numbers", default="blockNumbers2.txt")
#args.add_argument("--chain", dest="chain", help="Name of EVM-based chain to crawl (eth, bsc)", default="eth",)

args = args.parse_args()

SAMPLE_FILE = args.output
BLOCK_SAMPLE_SIZE = int(args.size)
block_sample = list()

response = requests.get("https://api.blockcypher.com/v1/eth/main")
latest_block_eth = response.json()["height"]

block_range = range(1, latest_block_eth + 1)
block_sample = sorted(random.sample(block_range, BLOCK_SAMPLE_SIZE))

with open(SAMPLE_FILE, 'w') as f:
    for block in block_sample:
        f.write("%s\n" % str(block))
    print('Saved blocks sample of {} in file {} on disk.'.format(
        len(block_sample), SAMPLE_FILE))
    percentage = len(block_sample)/latest_block_eth
    print("Total number of blocks in blockchain: {}".format(latest_block_eth))
    print("Percentage: {:.5f}%".format(percentage))
