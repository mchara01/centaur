import json
import os
import sys
import datetime

TOOL = sys.argv[1].split(".")[0]
DIRECTORY = sys.argv[1]
FULL_PATH = "../../smartbugs_bytecode/results/securify/" + DIRECTORY
total_contracts = 0
total_time = 0.0
output = dict()

print()
print('*' * 30)
print("Tool: Securify")

for filename in os.listdir(FULL_PATH):
    total_contracts += 1
    if os.path.exists(os.path.join(FULL_PATH, filename, "result.json")):
        with open(os.path.join(FULL_PATH, filename, "result.json"), 'r') as f:
            result = json.load(f)
            total_time += result['duration']
            if 'analysis' in result and type(result['analysis']) == dict and len(result['analysis']) > 0:
                for analysis in result['analysis']:
                    for tp in result['analysis'][analysis]["results"]:
                        if tp not in output:
                            output[tp] = len(result['analysis'][analysis]["results"][tp]['violations'])
                        else:
                            output[tp] = output[tp] + len(result['analysis'][analysis]["results"][tp]['violations'])

print(f"Total Contracts Analysed: {total_contracts}")
print(f"Total Execution Time: {str(datetime.timedelta(seconds=round(total_time)))}")
print(f"Average Time per Contract: {(total_time / total_contracts):.2f}")
for k, v in output.items():
    print(k + ": " + str(v))
print("*" * 30)
print()
