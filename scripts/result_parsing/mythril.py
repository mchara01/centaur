import datetime
import json
import os

import yaml

from utils.colours import ColoredText
from utils.swc_map import SWC_TO_TITLE


class Mythril:

    def __init__(self, tool_directory):
        self.directory = tool_directory
        self.full_path = "smartbugs_bytecode/results/mythril/" + self.directory

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
        print("Name: Mythril")

        # Print information about tool from SmartBugs configurations
        try:
            with open("smartbugs_bytecode/config/tools/mythril.yaml", "r") as stream:
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
                    for finding in result['findings']:
                        if finding in output:
                            output[finding] = output[finding] + 1
                        else:
                            output[finding] = 1
                    # if 'analysis' in result and result['analysis']['issues']:
                    #     for issue in result['analysis']['issues']:
                    #         if issue['title'] in output:
                    #             output[issue['title']] = output[issue['title']] + 1
                    #         else:
                    #             output[issue['title']] = 1

        print("Smart Contract Bytecodes")
        print("========================")
        print(f"Total Contracts Analysed: {total_contracts}")
        print(f"Total Execution Time: {str(datetime.timedelta(seconds=round(total_time)))}")
        print(f"Average Time per Contract: {(total_time / total_contracts):.2f} sec")

        print()

        print("DASP10+\tSWC_ID\tVulnerability: #")
        print("=" * 32)
        swc_found = set()
        for k, v in output.items():
            if k == "Integer_Arithmetic_Bugs":
                swc_found.add('101')
                print("3\t101\t" + k + ": " + str(v))
            elif k == "Unprotected_Selfdestruct":
                swc_found.add('106')
                print("2\t106\t" + k + ": " + str(v))
            elif k == "Dependence_on_tx_origin":
                swc_found.add('115')
                print("2\t115\t" + k + ": " + str(v))
            elif k == "Unprotected_Ether_Withdrawal":
                swc_found.add('105')
                print("2\t105\t" + k + ": " + str(v))
            elif k == "Unchecked_return_value_from_external_call":
                swc_found.add('104')
                print("4\t104\t" + k + ": " + str(v))
            elif k in ["State_access_after_external_call", "External_Call_To_User_Supplied_Address"]:
                swc_found.add('107')
                print("1\t107\t" + k + ": " + str(v))
            elif k in ["Multiple_Calls_in_a_Single_Transaction"]:
                swc_found.add('113')
                print("5\t113\t" + k + ": " + str(v))
            elif k in ["Dependence_on_predictable_environment_variable"]:
                swc_found.add('116')
                swc_found.add('120')
                print("6|8\t120|116\t" + k + ": " + str(v))
            elif k in ["Exception_State"]:
                swc_found.add('110')
                print("13\t110\t" + k + ": " + str(v))
            elif k in ["Delegatecall_to_user_supplied_address"]:
                swc_found.add('112')
                print("14\t112\t" + k + ": " + str(v))
            elif k in ["Write_to_an_arbitrary_storage_location"]:
                swc_found.add('124')
                print("15\t124\t" + k + ": " + str(v))
            elif k in ["Jump_to_an_arbitrary_instruction"]:
                swc_found.add('127')
                print("17\t127\t" + k + ": " + str(v))
            else:
                print("NA\t" + "NA\t" + k + ": " + str(v))
            total_vulnerabilities += v

        print()
        print("SWC_ID\tVulnerability_Description")
        print("=" * 34)
        swc_sorted = sorted(swc_found)
        for swc_id in swc_sorted:
            if swc_id in SWC_TO_TITLE:
                print(str(swc_id) + "\t" + SWC_TO_TITLE[swc_id])

        print()
        print(f"Total potential vulnerabilities reported by Mythril: {total_vulnerabilities}")
        print(ColoredText.info('*' * 30))
        print()
