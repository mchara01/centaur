import datetime
import json
import os
import yaml

from scripts.utils.colours import ColoredText


class Honeybadger:

    def __init__(self, tool_directory):
        self.directory = tool_directory
        self.full_path = "../smartbugs_bytecode/results/honeybadger/" + self.directory

    def parse(self):
        total_contracts = 0
        total_time = 0
        money_flow = 0
        balance_disorder = 0
        hidden_transfer = 0
        inheritance_disorder = 0
        uninitialised_struct = 0
        type_overflow = 0
        skip_empty_string = 0
        hidden_state_update = 0
        straw_man_contract = 0

        print()
        print(f"Report for {self.directory}")
        print(ColoredText.info('*' * 30))

        print("Tool")
        print("====")
        print("Name: HoneyBadger")
        # Print information about tool from SmartBugs configurations
        try:
            with open("../smartbugs_bytecode/config/tools/honeybadger.yaml", "r") as stream:
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
                        if result['analysis'][0]["Money flow"]:
                            money_flow += 1
                        if result['analysis'][0]["Balance disorder"]:
                            balance_disorder += 1
                        if result['analysis'][0]["Hidden transfer"]:
                            hidden_transfer += 1
                        if result['analysis'][0]["Inheritance disorder"]:
                            inheritance_disorder += 1
                        if result['analysis'][0]["Uninitialised struct"]:
                            uninitialised_struct += 1
                        if result['analysis'][0]["Type overflow"]:
                            type_overflow += 1
                        if result['analysis'][0]["Skip empty string"]:
                            skip_empty_string += 1
                        if result['analysis'][0]["Hidden state update"]:
                            hidden_state_update += 1
                        if result['analysis'][0]["Straw man contract"]:
                            straw_man_contract += 1

        print("Smart Contract Bytecodes")
        print("========================")
        print(f"Total Contracts Analysed: {total_contracts}")
        print(f"Total Execution Time: {str(datetime.timedelta(seconds=round(total_time)))}")
        print(f"Average Time per Contract: {(total_time / total_contracts):.2f}")

        print()

        print("Vulnerabilities")
        print("===============")
        print(f"Money flow: {money_flow}")
        print(f"Balance disorder: {balance_disorder}")
        print(f"Hidden transfer: {hidden_transfer}")
        print(f"Inheritance disorder: {inheritance_disorder}")
        print(f"Uninitialised struct: {uninitialised_struct}")
        print(f"Type overflow: {type_overflow}")
        print(f"Skip empty string: {skip_empty_string}")
        print(f"Hidden state update: {hidden_state_update}")
        print(f"Straw man contract: {straw_man_contract}")

        print(ColoredText.info('*' * 30))
        print()
