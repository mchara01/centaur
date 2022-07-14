import datetime
import json
import os


class Mythril:

    def __init__(self, tool_directory):
        self.directory = tool_directory
        self.full_path = "../smartbugs_bytecode/results/mythril/" + self.directory

    def parse(self):
        total_contracts = 0
        total_time = 0
        output = dict()

        print()
        print('*' * 30)
        print("Tool: Mythril")

        for filename in os.listdir(self.full_path):
            total_contracts += 1
            if os.path.exists(os.path.join(self.full_path, filename, "result.json")):
                with open(os.path.join(self.full_path, filename, "result.json"), 'r') as f:
                    result = json.load(f)
                    total_time += result['duration']
                    if 'analysis' in result and result['analysis']['issues']:
                        for issue in result['analysis']['issues']:
                            if issue['title'] in output:
                                output[issue['title']] = output[issue['title']] + 1
                            else:
                                output[issue['title']] = 1

        print(f"Total Contracts Analysed: {total_contracts}")
        print(f"Total Execution Time: {str(datetime.timedelta(seconds=round(total_time)))}")
        print(f"Average Time per Contract: {(total_time / total_contracts):.2f}")
        for k, v in output.items():
            print(k + ": " + str(v))
        print("*" * 30)
        print()
