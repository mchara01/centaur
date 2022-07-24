""" Block Number Sample Generator

This script allows the user to generate a sample of random block numbers
for either Ethereum or BSC. It connects to the blockchain explorer API
of the two blockchains, finds which is the latest block and produces
a random sample of the blockchain which then proceeds to write it to
a file in a sorted fashion.

For executing the script on BSC chain, an API must be provided.

Example run: python3 blockNumberGenerator.py --size 100 --chain bsc --output blockNumbersBsc.txt --apikey <API_KEY>
"""

import argparse
import os
import random
import time

import requests

# Argument parsing
args = argparse.ArgumentParser(
    description="Random block number generator."
)
args.add_argument("--size", dest="size", help="Block sample size", default=5)
args.add_argument("--output", dest="output",
                  help="Output file that will contain the generated block numbers", default="blockNumbersEth.txt")
args.add_argument("--chain", dest="chain",
                  help="Name of EVM-based chain to crawl (eth, bsc)", default="eth")
args.add_argument("--apikey", dest="apikey", help="API key for BscScan only")

# Variable initialisation
args = args.parse_args()
sample_file = args.output
block_sample_size = int(args.size)
block_sample = list()
latest_block = 1

# Detect the latest block of the given blockchain
if args.chain == "eth":
    response = requests.get("https://api.blockcypher.com/v1/eth/main")
    latest_block = response.json()["height"]
elif args.chain == "bsc":
    if args.apikey is None:  # For Bsc, an API key is required
        print("Please provide an API key to generate block numbers for BSC.")
        exit()
    timestamp = int(time.time())
    response = requests.get(
        f'https://api.bscscan.com/api?module=block&action=getblocknobytime&timestamp={timestamp}&closest=before&apikey={args.apikey}')
    if "Error" in response.text:
        print("Error in request to BscScan.")
        exit()
    latest_block = int(response.json()["result"])
else:
    print("Please enter a valid chain name from [eth, bsc].")
    exit()

# Creation of random block number sample
block_range = range(1, latest_block + 1)
block_sample = sorted(random.sample(block_range, block_sample_size))

# Directory creation for saving the sample
# Directory name is current date and time
dirname = "data/block_samples/" + time.strftime("%d%m%Y_%H%M%S")
os.mkdir(dirname)

# Write block number sample to a file, in the data directory
with open(dirname + "/" + sample_file, 'w') as f:
    for block in block_sample:
        f.write("%s\n" % str(block))
    print('Saved blocks sample of {} in file {} on disk.'.format(
        len(block_sample), sample_file))
    percentage = len(block_sample) / latest_block
    print("Total number of blocks in blockchain: {}".format(latest_block))
    print("Percentage: {:.5f}%".format(percentage))
