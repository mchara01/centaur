"""
A one-off script that merges all data to a single SQLite database.

Instructions:
    rm -rf database/analysis.db
    sqlite3 -init database/schema.sql database/analysis.db .quit
    rm -rf database/csvs
    python scripts/database/create_db.py csvs \
            smartbugs_bytecode/results \
            build/database/03_Jul_2022/sqlite/run1.sqlite3 \
            build/database/02_Aug_2022/sqlite/run2.sqlite3
    sqlite3 database/analysis.db < csvs/populate.sql
"""
import argparse
import sqlite3
import re
import hashlib
import os
import json
import csv

from collections import defaultdict
from scripts.utils.dasp10extended_map import VULNS_LOOKUP


def connect(db):
    return sqlite3.connect(db)


def run_query(con, query):
    cur = con.cursor()
    res = cur.execute(query)
    return res


def create_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def save_table_file(directory, name, rows):
    path = os.path.join(directory, f"{name}.csv")
    with open(path, 'w') as outfile:
        writer = csv.writer(outfile, quoting=csv.QUOTE_NONNUMERIC)
        writer.writerows(rows)


def create_populate_script(output, results):
    path = os.path.join(output, 'populate.sql')
    lines = [".mode csv\n"] + [
        f".import {path} {name}\n"
        for path, name in results
    ]
    with open(path, 'w') as f:
        f.writelines(lines)


def get_path_and_name_of_csv(directory, name):
    path = os.path.join(directory, f"{name}.csv")
    return [path, name]


def canonicalise(vuln):
    try:
        return VULNS_LOOKUP[vuln]
    except KeyError:
        print(f"Error: {vuln} does not exists in VULNS_LOOKUP")
        import sys; sys.exit()


def get_date_from_path(path):
    """Extract the date from a path.

    The path should be in the form of:
       build/database/03_Jul_2022/sqlite/run1.sqlite3     
    """
    regex = r"^(.*)/([0-9][0-9]_.*_[0-9][0-9][0-9][0-9])/(.*)/"
    return re.search(regex, path).groups()[1]


def get_addresses(databases):
    """Get a list with the rows of all addresses

    Args:
        databases: filepaths to the databases 
            (e.g., build/database/03_Jul_2022/sqlite/run1.sqlite3)

    Returns:
        List of lists containing rows of address table.
           [id, block_number, address, balance, nr_transactions, 
            nr_token_transfers, bytecode_hash, chain, run]
        A lookup from address hex to address id (addr -> chain -> id)
        A double lookup from hash to addresses and address to hash
            {'address': {'0x...': {'eth': 'hash_value'}}, 
             'hash': {'hash_value': [('eth', '0x...'), ('bsc', '0x...')]}}
    """
    qcolumns = ['block_number', 'address', 'balance', 'nr_transactions',
                'nr_token_transfers', 'bytecode']
    qstring = "SELECT {columns} FROM {table}"
    address_id_counter = 0
    addresses_ids = defaultdict(dict)
    hashes = {'address': defaultdict(dict), 'hash': defaultdict(list)}
    rows = []

    def query():
        nonlocal address_id_counter
        for chain in ('eth', 'bsc'):
            qset = run_query(db_con, qstring.format(
                columns=",".join(qcolumns), 
                table=chain))
            for row in qset:
                address = row[1]
                bytecode_hash = hashlib.sha256(row[-1].encode('utf-8')).hexdigest()
                rows.append(
                        [address_id_counter] + list(row)[:-1] + [
                            bytecode_hash,
                            # chain
                            chain,
                            # run date
                            run_date
                        ]
                )
                hashes['address'][address][chain] = bytecode_hash
                hashes['hash'][bytecode_hash].append((chain, address))
                addresses_ids[address][chain] = address_id_counter
                address_id_counter += 1

    for db in databases:
        print("Processing ", db)
        run_date = get_date_from_path(db)
        db_con = connect(db)
        query()

    return rows, addresses_ids, hashes


def process_results(path, addresses_ids, hashes):
    """Process result of analysis and return rows of Result and Finding tables.

    Args:
        path: Path of directory that contains the results
        addresses_ids: Lookup from address to id 
        hashes: A double lookup from hash to addresses and address to hash

    Returns:
        List of lists containing rows of result table.
           [id, tool, duration, exit_code, success, address_id]
        List of lists containing rows of finding table.
           [id, vulnerability, result_id]
    """
    print("Processing ", path)
    result_id_counter = 0
    finding_id_counter = 0
    result_rows = []
    finding_rows = []
    for dirpath, dirnames, filenames in os.walk(path):
        # Last directory that does not have any subdirectories.
        if len(dirnames) == 0:
            dirpath_minus_addr, address = os.path.split(dirpath)
            dirpath_minus_date, result_date = os.path.split(dirpath_minus_addr)
            _, tool_name = os.path.split(dirpath_minus_date)

            for filename in [f for f in filenames if f.endswith(".json")]:

                result_path = os.path.join(dirpath, filename)
                with open(result_path, 'r') as f:
                    results = json.load(f)
                    exit_code = results['exit_code']
                    duration = results['duration']
                    success = results['success']
                    vulns = [canonicalise(v) for v in results['findings']]
                    vulns = list(filter(lambda x: x is not None, vulns))
                    chain = 'eth' if 'eth' in results['contract'] else None
                    chain = 'bsc' if 'bsc' in results['contract'] else chain
                    try:
                        addr_hash = hashes['address'][address][chain]
                    except:
                        print(f"Warning: {address} does not exists to the provided tables")
                        continue

                for addr_chain, addr in hashes['hash'][addr_hash]:
                    result_rows.append([
                            result_id_counter, tool_name, duration, exit_code,
                            success, addresses_ids[addr][addr_chain]
                        ])
                    for vuln in vulns:
                        finding_rows.append([
                                finding_id_counter, vuln, result_id_counter
                            ])
                        finding_id_counter += 1
                    result_id_counter += 1
    return result_rows, finding_rows 


def get_args():
    parser = argparse.ArgumentParser(
        description='Merge all data to a single SQLite database')
    parser.add_argument(
        "output", 
        help="Directory to save the results"
    )
    parser.add_argument(
        "results", 
        help="Directory that contains the results of the analysis tools"
    )
    parser.add_argument(
        "databases", 
        nargs='+',
        help="Databases containing the addresses of analyzed contracts"
    )
    return parser.parse_args()


def main():
    args = get_args()
    addresses_rows, addresses_lookup, hashes = get_addresses(args.databases)
    result_rows, finding_rows = process_results(
            args.results, addresses_lookup, hashes) 
    print("Save results")
    create_dir(args.output)
    results = []
    save_table_file(args.output, 'Address', addresses_rows)
    results.append(get_path_and_name_of_csv(args.output, 'Address'))
    save_table_file(args.output, 'Result', result_rows)
    results.append(get_path_and_name_of_csv(args.output, 'Result'))
    save_table_file(args.output, 'Finding', finding_rows)
    results.append(get_path_and_name_of_csv(args.output, 'Finding'))
    create_dir(args.output)
    create_populate_script(args.output, results)


if __name__ == "__main__":
    main()
