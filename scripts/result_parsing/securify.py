import datetime
import json
import os

import yaml

from utils.colours import ColoredText


class Securify:

    def __init__(self, tool_directory):
        self.directory = tool_directory
        self.full_path = "smartbugs_bytecode/results/securify/" + self.directory

    def parse(self):
        total_contracts = 0
        total_time = 0.0
        output = dict()

        print()
        print(f"Report for {self.directory}")
        print(ColoredText.info('*' * 30))

        print("Tool")
        print("====")
        print("Name: Securify")

        # Print information about tool from SmartBugs configurations
        try:
            with open("smartbugs_bytecode/config/tools/securify.yaml", "r") as stream:
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
                    if 'analysis' in result and type(result['analysis']) == dict and len(result['analysis']) > 0:
                        for analysis in result['analysis']:
                            for tp in result['analysis'][analysis]["results"]:
                                if tp not in output:
                                    output[tp] = len(result['analysis'][analysis]["results"][tp]['violations'])
                                else:
                                    output[tp] = output[tp] + len(
                                        result['analysis'][analysis]["results"][tp]['violations'])

        print("Smart Contract Bytecodes")
        print("========================")
        print(f"Total Contracts Analysed: {total_contracts}")
        print(f"Total Execution Time: {str(datetime.timedelta(seconds=round(total_time)))}")
        print(f"Average Time per Contract: {(total_time / total_contracts):.2f}")

        print()

        print("DASP10\tVulnerability: #")
        print("="*24)
        for k, v in output.items():
            if k == "DAO" or k == "DAOConstantGas":
                print("1\t" + k + ": " + str(v))
            elif k == "MissingInputValidation":
                print("2\t" + k + ": " + str(v))
            elif k in ["TODAmount", "TODReceiver", "TODTransfer"]:
                print("7\t" + k + ": " + str(v))
            elif k == "UnhandledException":
                print("4\t" + k + ": " + str(v))
            else:
                print("10\t" + k + ": " + str(v))

        print(ColoredText.info('*' * 30))
        print()
