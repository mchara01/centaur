"""
This module is used to convert the results of the analysis tools into
a CSV format.

Modified version of https://github.com/smartbugs/smartbugs/blob/bytecode/results2csv.py
"""
import argparse
import csv
import json
import os
import sys
import traceback

CSV_COLUMNS = ["contract", "tool", "duration", "exit_code", "success", "findings", "errors",
               "messages", "dataset", "timeout", "out_of_memory", "error"]


def json_to_csv(data, dataset):
    csv_data = {
        "contract": os.path.basename(data["contract"]).split(".")[0],
        "dataset": dataset
    }
    for col in ("tool", "exit_code", "duration"):
        csv_data[col] = data[col]
    for col in ("findings", "messages", "errors"):
        if col not in data:
            csv_data[col] = []
        elif not data[col]:
            csv_data[col] = []
        else:
            csv_data[col] = ','.join(data[col])
    for col in ("timeout", "out_of_memory", "other_errors", "error", "success"):
        csv_data[col] = False
    if "errors" in data and data["errors"] and "DOCKER_TIMEOUT" in data["errors"]:
        csv_data["timeout"] = True
    elif data["errors"]:
        csv_data["error"] = True
    else:
        csv_data["success"] = True
    return [csv_data[col] for col in CSV_COLUMNS]


def generate_csv(csv_out, dataset, result_fn):
    with open(result_fn) as f:
        try:
            data = json.load(f)
        except Exception:
            print(result_fn)
            traceback.print_exc(file=sys.stdout)
            sys.stdout.flush()
            return 1
    csv_out.writerow(json_to_csv(data, dataset))


def get_args():
    # Argument parsing
    argparser = argparse.ArgumentParser(prog="python3 resultsToCSV.py", description="""
        Print essential information into a CSV file from the result.json files.
        """)
    argparser.add_argument("path_to_results", help="directory containing the result files")
    argparser.add_argument("dataset", help="label identifying the dataset/run")
    argparser.add_argument("-v", "--verbose", action='store_true', help="show progress")
    return argparser.parse_args()


def main():
    args = get_args()
    total_rows = 0
    with open("analysis_results.csv", mode='w') as csv_file:
        # csv_out = csv.writer(sys.stdout)
        csv_out = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_out.writerow(CSV_COLUMNS)

        results = []
        for path, _, files in os.walk(args.path_to_results):
            if "result.json" in files:
                results.append(os.path.join(path, "result.json"))

        for file_path in sorted(results):
            if args.verbose:
                print(file_path, file=sys.stderr)
            total_rows += 1
            generate_csv(csv_out, args.dataset, file_path)
    print(f"Total rows written to analysis_results.csv: {total_rows}")


if __name__ == '__main__':
    sys.exit(main())
