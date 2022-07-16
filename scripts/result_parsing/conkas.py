import datetime
import json
import os

from scripts.colours import ColoredText


class Conkas:

    def __init__(self, tool_directory):
        self.directory = tool_directory
        self.full_path = "../smartbugs_bytecode/results/conkas/" + self.directory

    def parse(self):
        total_contracts = 0
        total_time = 0
        arithmetic = 0
        unchecked_low_level_calls = 0
        tod = 0
        time_manipulation = 0
        reentrancy_vulnerability = 0

        print()
        print(ColoredText.info('*' * 30))
        print("Tool: Conkas")

        for filename in os.listdir(self.full_path):
            total_contracts += 1
            if os.path.exists(os.path.join(self.full_path, filename, "result.json")):
                with open(os.path.join(self.full_path, filename, "result.json"), 'r') as f:
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
        print()
        print("DASP10\tVulnerability: #")
        print("="*24)
        print(f"1\tRe-Entrancy Vulnerability: {reentrancy_vulnerability}")
        print(f"3\tArithmetic: {arithmetic}")
        print(f"4\tUnchecked Low Level Call: {unchecked_low_level_calls}")
        print(f"7\tTransaction-Ordering Dependence (TOD): {tod}")
        print(f"8\tTime Manipulation: {time_manipulation}")
        print(ColoredText.info('*' * 30))
        print()
