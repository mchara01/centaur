import datetime
import json
import os

import yaml

from scripts.colours import ColoredText


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
        print(f"Report for {self.directory}")
        print(ColoredText.info('*' * 30))

        print("Tool")
        print("====")
        print("Name: Oyente")

        # Print information about tool from SmartBugs configurations
        try:
            with open("../smartbugs_bytecode/config/tools/oyente.yaml", "r") as stream:
                print(f"Information: {(yaml.safe_load(stream))['info']}")
        except Exception:
            print("Information: N/A")

        print()

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

        print("Smart Contract Bytecodes")
        print("========================")
        print(f"Total Contracts Analysed: {total_contracts}")
        print(f"Total Execution Time: {str(datetime.timedelta(seconds=round(total_time)))}")
        print(f"Average Time per Contract: {(total_time / total_contracts):.2f}")

        print()

        print("DASP10\tVulnerability: #")
        print("="*24)
        print(f"5\tCallstack Depth Attack Vulnerability: {callstack_dept_attack}")
        print(f"7\tTransaction-Ordering Dependence (TOD): {tod}")
        print(f"8\tTimestamp Dependency: {timestamp_dependency}")
        print(f"1\tRe-Entrancy Vulnerability: {reentrancy_vulnerability}")

        print(ColoredText.info('*' * 30))
        print()
