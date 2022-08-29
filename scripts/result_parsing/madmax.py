import datetime
import json
import os

import yaml

from utils.colours import ColoredText

from utils.swc_map import SWC_TO_TITLE


class Madmax:

    def __init__(self, tool_directory):
        self.directory = tool_directory
        self.full_path = "smartbugs_bytecode/results/madmax/" + self.directory

    def parse(self):
        total_contracts = 0
        total_time = 0
        OverflowLoopIterator = 0
        UnboundedMassOp = 0
        WalletGriefing = 0

        print()
        print(f"Report for {self.directory}")
        print(ColoredText.info('*' * 30))

        print("Tool")
        print("====")

        print("Name: MadMax")
        # Print information about tool from SmartBugs configurations
        try:
            with open("smartbugs_bytecode/config/tools/madmax.yaml", "r") as stream:
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
                    if 'OverflowLoopIterator' in result['findings']:
                        OverflowLoopIterator += 1
                    if 'UnboundedMassOp' in result['findings']:
                        UnboundedMassOp += 1
                    if 'WalletGriefing' in result['findings']:
                        WalletGriefing += 1

        print("Smart Contract Bytecodes")
        print("========================")
        print(f"Total Contracts Analysed: {total_contracts}")
        print(f"Total Execution Time: {str(datetime.timedelta(seconds=round(total_time)))}")
        print(f"Average Time per Contract: {(total_time / total_contracts):.2f} sec")

        print()

        print("DASP10+\tSWC_ID\tVulnerability: #")
        print("=" * 32)
        print(f"3\t101\tOverflowLoopIterator: {OverflowLoopIterator}")
        print(f"5\t113\tUnboundedMassOp: {UnboundedMassOp}")
        print(f"11\t126\tWalletGriefing: {WalletGriefing}")

        print()

        print("SWC_ID\tVulnerability_Description")
        print("="*34)
        swc_found = ('101', '113', '126')
        for swc_id in sorted(swc_found):
            if swc_id in SWC_TO_TITLE:
                print(str(swc_id) + "\t" + SWC_TO_TITLE[swc_id])

        print()
        total_vulnerabilities = OverflowLoopIterator + UnboundedMassOp + WalletGriefing
        print(f"Total potential vulnerabilities reported by MadMax: {total_vulnerabilities}")
        print(ColoredText.info('*' * 30))
        print()

