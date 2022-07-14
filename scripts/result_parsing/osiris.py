import datetime
import json
import os


class Osiris:

    def __init__(self, tool_directory):
        self.directory = tool_directory
        self.full_path = "../smartbugs_bytecode/results/osiris/" + self.directory

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
        print('*' * 30)
        print("Tool: Osiris")

        for filename in os.listdir(self.full_path):
            total_contracts += 1
            if os.path.exists(os.path.join(self.full_path, filename, "result.json")):
                with open(os.path.join(self.full_path, filename, "result.json"), 'r') as f:
                    result = json.load(f)
                    total_time += result['duration']
                    if 'analysis' in result and type(result['analysis']) == list and len(result['analysis']) > 0:
                        if result['analysis'][0]['Arithmetic bugs']:
                            arithmetic += 1
                        if result['analysis'][0]['Overflow bugs']:
                            overflow += 1
                        if result['analysis'][0]['Underflow bugs']:
                            underflow += 1
                        if result['analysis'][0]['Division bugs']:
                            division += 1
                        if result['analysis'][0]['Modulo bugs']:
                            modulo += 1
                        if result['analysis'][0]['Truncation bugs']:
                            truncation += 1
                        if result['analysis'][0]['Signedness bugs']:
                            signedness += 1
                        if result['analysis'][0]['Callstack bug']:
                            callstack += 1
                        if result['analysis'][0]['Concurrency bug']:
                            concurrency += 1
                        if result['analysis'][0]['Timedependency bug']:
                            timedependency += 1
                        if result['analysis'][0]['Reentrancy bug']:
                            reentrancy += 1

        print(f"Total Contracts Analysed: {total_contracts}")
        print(f"Total Execution Time: {str(datetime.timedelta(seconds=round(total_time)))}")
        print(f"Average Time per Contract: {(total_time / total_contracts):.2f}")
        print(f"Arithmetic bugs: {arithmetic}")
        print(f"Overflow bugs: {overflow}")
        print(f"Underflow bugs: {underflow}")
        print(f"Division bugs: {division}")
        print(f"Modulo bugs: {modulo}")
        print(f"Truncation bugs: {truncation}")
        print(f"Signedness bugs: {signedness}")
        print(f"Callstack bug: {callstack}")
        print(f"Concurrency bug: {concurrency}")
        print(f"Timedependency bug: {timedependency}")
        print(f"Reentrancy bug: {reentrancy}")
        print("*" * 30)
        print()
