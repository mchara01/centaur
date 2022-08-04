import datetime
import json
import os

import yaml

from utils.colours import ColoredText
from utils.swc_map import SWC_TO_TITLE


class Osiris:

    def __init__(self, tool_directory):
        self.directory = tool_directory
        self.full_path = "smartbugs_bytecode/results/osiris/" + self.directory

    def parse(self):
        total_contracts = 0
        total_time = 0
        arithmetic = 0
        overflow = 0
        underflow = 0
        division = 0
        modulo = 0
        truncation = 0
        signedness = 0
        callstack = 0
        concurrency = 0
        timedependency = 0
        reentrancy = 0

        print()
        print(f"Report for {self.directory}")
        print(ColoredText.info('*' * 30))

        print("Tool")
        print("====")
        print("Name: Osiris")

        # Print information about tool from SmartBugs configurations
        try:
            with open("smartbugs_bytecode/config/tools/osiris.yaml", "r") as stream:
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
                    if 'analysis' in result and type(result['analysis']) == list and len(result['analysis']) > 0:
                        if 'Arithmetic bugs' in result['analysis'][0] and result['analysis'][0]['Arithmetic bugs']:
                            arithmetic += 1
                        if 'Overflow bugs' in result['analysis'][0] and result['analysis'][0]['Overflow bugs']:
                            overflow += 1
                        if 'Underflow bugs' in result['analysis'][0] and result['analysis'][0]['Underflow bugs']:
                            underflow += 1
                        if 'Division bugs' in result['analysis'][0] and result['analysis'][0]['Division bugs']:
                            division += 1
                        if 'Modulo bugs' in result['analysis'][0] and result['analysis'][0]['Modulo bugs']:
                            modulo += 1
                        if 'Truncation bugs' in result['analysis'][0] and result['analysis'][0]['Truncation bugs']:
                            truncation += 1
                        if 'Signedness bugs' in result['analysis'][0] and result['analysis'][0]['Signedness bugs']:
                            signedness += 1
                        if 'Callstack bugs' in result['analysis'][0] and result['analysis'][0]['Callstack bug']:
                            callstack += 1
                        if 'Concurrency bugs' in result['analysis'][0] and result['analysis'][0]['Concurrency bug']:
                            concurrency += 1
                        if 'Timedependency bugs' in result['analysis'][0] and result['analysis'][0]['Timedependency bug']:
                            timedependency += 1
                        if 'Reentrancy bugs' in result['analysis'][0] and result['analysis'][0]['Reentrancy bug']:
                            reentrancy += 1

        print("Smart Contract Bytecodes")
        print("========================")
        print(f"Total Contracts Analysed: {total_contracts}")
        print(f"Total Execution Time: {str(datetime.timedelta(seconds=round(total_time)))}")
        print(f"Average Time per Contract: {(total_time / total_contracts):.2f} sec")

        print()

        print("DASP10+\tSWC_ID\tVulnerability: #")
        print("=" * 32)
        print(f"3\t101\tArithmetic bugs: {arithmetic}")
        print(f"3\t101\tOverflow bugs: {overflow}")
        print(f"3\t101\tUnderflow bugs: {underflow}")
        print(f"3\t101\tDivision bugs: {division}")
        print(f"3\t101\tModulo bugs: {modulo}")
        print(f"3\t101\tTruncation bugs: {truncation}")
        print(f"3\t101\tSignedness bugs: {signedness}")
        print(f"3\t101\tCallstack bug: {callstack}")
        print(f"7\t114\tConcurrency bug: {concurrency}")
        print(f"8\t116\tTimedependency bug: {timedependency}")
        print(f"1\t107\tReentrancy bug: {reentrancy}")

        print()
        swc_found = ('101', '107', '114', '116')
        print("SWC_ID\tVulnerability_Description")
        print("=" * 34)
        swc_sorted = sorted(swc_found)
        for swc_id in swc_sorted:
            if swc_id in SWC_TO_TITLE:
                print(str(swc_id) + "\t" + SWC_TO_TITLE[swc_id])

        print(ColoredText.info('*' * 30))
        print()
