import datetime
import json
import os
import sys

TOOL = sys.argv[1].split(".")[0]
DIRECTORY = sys.argv[1]
FULL_PATH = "../../smartbugs_bytecode/results/madmax/" + DIRECTORY

total_contracts = 0
total_time = 0
output = dict()

print()
print('*' * 30)
print("Tool: MadMax")

for filename in os.listdir(FULL_PATH):
    total_contracts += 1
    if os.path.exists(os.path.join(FULL_PATH, filename, "result.json")):
        with open(os.path.join(FULL_PATH, filename, "result.json"), 'r') as f:
            result = json.load(f)
            total_time += result['duration']
            print(result['findings'])
            #print(result['analysis'][0][2])

print(f"Total Contracts Analysed: {total_contracts}")
print(f"Total Execution Time: {str(datetime.timedelta(seconds=round(total_time)))}")
print(f"Average Time per Contract: {(total_time / total_contracts):.2f}")

print("*" * 30)
print()