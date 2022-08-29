import datetime
import json
import os

import yaml

from utils.colours import ColoredText
from utils.swc_map import SWC_TO_TITLE


class Vandal:

    def __init__(self, tool_directory):
        self.directory = tool_directory
        self.full_path = "smartbugs_bytecode/results/vandal/" + self.directory

    def parse(self):
        total_contracts = 0
        total_vulnerabilities = 0
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
            with open("smartbugs_bytecode/config/tools/vandal.yaml", "r") as stream:
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
        print(f"Average Time per Contract: {(total_time / total_contracts):.2f} sec")

        print()

        print("DASP10+\tSWC_ID\tVulnerability: #")
        print("="*32)
        swc_found = set()
        for k, v in output.items():
            if k in ["ReentrantCall", "CheckedCallStateUpdate"]:
                swc_found.add('107')
                print("1\t" + "107\t" + k + ": " + str(v))
            elif k == "Destroyable":
                swc_found.add('106')
                print("2\t" + "106\t" + k + ": " + str(v))
            elif k == "UnsecuredValueSend":
                swc_found.add('105')
                print("2\t" + "105\t" + k + ": " + str(v))
            elif k == "OriginUsed":
                swc_found.add('115')
                print("2\t" + "115\t" + k + ": " + str(v))
            elif k == "UncheckedCall":
                swc_found.add('104')
                print("4\t" + "104\t" + k + ": " + str(v))
            else:
                print("NA\t" + "NA\t" + k + ": " + str(v))
            total_vulnerabilities += v
        print()

        print("SWC_ID\tVulnerability_Description")
        print("="*34)
        swc_sorted = sorted(swc_found)
        for swc_id in swc_sorted:
            print(str(swc_id) + "\t" + SWC_TO_TITLE[swc_id])

        print()
        print(f"Total potential vulnerabilities reported by Vandal: {total_vulnerabilities}")
        print(ColoredText.info('*' * 30))
        print()
