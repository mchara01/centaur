import datetime
import json
import os


class Maian:

    def __init__(self, tool_directory):
        self.directory = tool_directory
        self.full_path = "../smartbugs_bytecode/results/maian/" + self.directory

    def parse(self):
        total_contracts = 0
        total_time = 0
        greedy = 0
        prodigal = 0
        suicidal = 0

        print()
        print('*' * 30)
        print("Tool: Maian")

        for filename in os.listdir(self.full_path):
            total_contracts += 1
            if os.path.exists(os.path.join(self.full_path, filename, "result.json")):
                with open(os.path.join(self.full_path, filename, "result.json"), 'r') as f:
                    result = json.load(f)
                    total_time += result['duration']
                    if 'analysis' in result and type(result['analysis']) == list and len(result['analysis']) > 0:
                        if "Ether leak" in result['analysis'][0]['findings'] or "Ether leak (verified)" in \
                                result['analysis'][0]['findings']:
                            prodigal += 1
                        if "Ether lock" in result['analysis'][0][
                            'findings'] or "Ether lock (Ether accepted without send)" in result['analysis'][0][
                            'findings']:
                            greedy += 1
                        if "Destructible" in result['analysis'][0]['findings'] or "Destructible (verified)" in \
                                result['analysis'][0]['findings']:
                            suicidal += 1

        print(f"Total Contracts Analysed: {total_contracts}")
        print(f"Total Execution Time: {str(datetime.timedelta(seconds=round(total_time)))}")
        print(f"Average Time per Contract: {(total_time / total_contracts):.2f}")
        print(f"Greedy: {greedy}")
        print(f"Prodigal: {prodigal}")
        print(f"Suicidal: {suicidal}")
        print("*" * 30)
        print()
