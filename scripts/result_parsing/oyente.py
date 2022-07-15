import datetime
import json
import os


class Oyente:

    def __init__(self, tool_directory):
        self.directory = tool_directory
        self.full_path = "../smartbugs_bytecode/results/oyente/" + self.directory

    def parse(self):
        total_contracts = 0
        total_time = 0.0
        callstack_dept_attack = 0
        tod = 0
        timestamp_dependency = 0
        reentrancy_vulnerability = 0

        print()
        print('*' * 30)
        print("Tool: Oyente")

        for filename in os.listdir(self.full_path):
            total_contracts += 1
            if os.path.exists(os.path.join(self.full_path, filename, "result.json")):
                with open(os.path.join(self.full_path, filename, "result.json"), 'r') as f:
                    result = json.load(f)
                    total_time += result['duration']
                    if 'analysis' in result and len(result['analysis']) > 0:
                        if result['analysis'][0]['Callstack Depth Attack Vulnerability']:
                            callstack_dept_attack += 1
                        if result['analysis'][0]['Transaction-Ordering Dependence (TOD)']:
                            tod += 1
                        if result['analysis'][0]['Timestamp Dependency']:
                            timestamp_dependency += 1
                        if result['analysis'][0]['Re-Entrancy Vulnerability']:
                            reentrancy_vulnerability += 1

        print(f"Total Contracts Analysed: {total_contracts}")
        print(f"Total Execution Time: {str(datetime.timedelta(seconds=round(total_time)))}")
        print(f"Average Time per Contract: {(total_time / total_contracts):.2f}")
        print(f"Callstack Depth Attack Vulnerability: {callstack_dept_attack}")
        print(f"Transaction-Ordering Dependence (TOD): {tod}")
        print(f"Timestamp Dependency: {timestamp_dependency}")
        print(f"Re-Entrancy Vulnerability: {reentrancy_vulnerability}")
        print("*" * 30)
        print()