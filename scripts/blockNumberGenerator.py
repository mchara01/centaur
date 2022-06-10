import requests
import random

SAMPLE_FILE = "blockNumbers.txt"
BLOCK_SAMPLE_SIZE = 5
block_sample = list()

response = requests.get("https://api.blockcypher.com/v1/eth/main")
latest_block_eth = response.json()["height"]

block_range = range(1, latest_block_eth + 1)
block_sample = sorted(random.sample(block_range, BLOCK_SAMPLE_SIZE))

with open(SAMPLE_FILE, 'w') as f:
        for block in block_sample:
            f.write("%s\n" % str(block))
        print('Saved blocks sample of {} in file {} on disk.'.format(len(block_sample), SAMPLE_FILE))
        percentage = len(block_sample)/latest_block_eth
        print("Total number of blocks in blockchain: {}".format(latest_block_eth))
        print("Percentage: {:.5f}%".format(percentage))