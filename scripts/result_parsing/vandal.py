import datetime
import json
import os

import yaml

from scripts.utils.colours import ColoredText


class Vandal:

    def __init__(self, tool_directory):
        self.directory = tool_directory
        self.full_path = "../smartbugs_bytecode/results/vandal/" + self.directory

    def parse(self):
        total_contracts = 0
        total_time = 0
        output = dict()

        print()
        print(f"Report for {self.directory}")
        print(ColoredText.info('*' * 30))

        print("Tool")
        print("====")
        print("Name: Vandal")

        # Print information about tool from SmartBugs configurations
        try:
            with open("../smartbugs_bytecode/config/tools/vandal.yaml", "r") as stream:
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
                    if 'findings' in result and result['findings']:
                        for issue in result['findings']:
                            if issue in output:
                                output[issue] = output[issue] + 1
                            else:
                                output[issue] = 1

        print("Smart Contract Bytecodes")
        print("========================")
        print(f"Total Contracts Analysed: {total_contracts}")
        print(f"Total Execution Time: {str(datetime.timedelta(seconds=round(total_time)))}")
        print(f"Average Time per Contract: {(total_time / total_contracts):.2f}")

        print()

        print("DASP10\tVulnerability: #")
        print("="*24)
        for k, v in output.items():
            if k == "ReentrantCall":
                print("1\t" + k + ": " + str(v))
            elif k in ["Destroyable", "OriginUsed", "UnsecuredValueSend"]:
                print("2\t" + k + ": " + str(v))
            elif k == "UncheckedCall":
                print("4\t" + k + ": " + str(v))
            else:
                print("10\t" + k + ": " + str(v))

        print(ColoredText.info('*' * 30))
        print()
