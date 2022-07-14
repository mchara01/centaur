import json
import os
import sys
import datetime

TOOL = sys.argv[1].split(".")[0]
DIRECTORY = sys.argv[1]
FULL_PATH = "../../smartbugs_bytecode/results/conkas/" + DIRECTORY
total_contracts = 0
total_time = 0
arithmetic = 0
unchecked_low_level_calls = 0
tod = 0
time_manipulation = 0
reentrancy_vulnerability = 0

print()
print('*' * 30)
print("Tool: Conkas")

for filename in os.listdir(FULL_PATH):
    total_contracts += 1
    if os.path.exists(os.path.join(FULL_PATH, filename, "result.json")):
        with open(os.path.join(FULL_PATH, filename, "result.json"), 'r') as f:
            result = json.load(f)
            total_time += result['duration']
            if 'analysis' in result and type(result['analysis']) == list and len(result['analysis']) > 0:
                for vulnerability_dict in result['analysis']:
                    if vulnerability_dict['vuln_type'] in ('Integer Overflow', 'Integer Underflow'):
                        arithmetic += 1
                    if vulnerability_dict['vuln_type'] == 'Unchecked Low Level Call':
                        unchecked_low_level_calls += 1
                    if vulnerability_dict['vuln_type'] == 'Reentrancy':
                        reentrancy_vulnerability += 1
                    if vulnerability_dict['vuln_type'] == 'Transaction Ordering Dependence':
                        tod += 1
                    if vulnerability_dict['vuln_type'] == 'Time Manipulation':
                        time_manipulation += 1

print(f"Total Contracts Analysed: {total_contracts}")
print(f"Total Execution Time: {str(datetime.timedelta(seconds=round(total_time)))}")
print(f"Average Time per Contract: {(total_time / total_contracts):.2f}")
print(f"Arithmetic: {arithmetic}")
print(f"Unchecked Low Level Call: {unchecked_low_level_calls}")
print(f"Transaction-Ordering Dependence (TOD): {tod}")
print(f"Time Manipulation: {time_manipulation}")
print(f"Re-Entrancy Vulnerability: {reentrancy_vulnerability}")
print("*" * 30)
print()
