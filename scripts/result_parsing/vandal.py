import datetime
import json
import os


class Vandal:

    def __init__(self, tool_directory):
        self.directory = tool_directory
        self.full_path = "../smartbugs_bytecode/results/vandal/" + self.directory

    def parse(self):
        total_contracts = 0
        total_time = 0
        output = dict()

        print()
        print('*' * 30)
        print("Tool: Vandal")

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

        print(f"Total Contracts Analysed: {total_contracts}")
        print(f"Total Execution Time: {str(datetime.timedelta(seconds=round(total_time)))}")
        print(f"Average Time per Contract: {(total_time / total_contracts):.2f}")
        for k, v in output.items():
            print(k + ": " + str(v))
        print("*" * 30)
        print()
