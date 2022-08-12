"""
This file contains a dictionary with useful queries that can be used to view the data inside our database.
"""
QUERIES = {
    "total_eth_addr": "SELECT COUNT(*) FROM db_blockchain.eth",
    "total_bsc_addr": "SELECT COUNT(*) FROM db_blockchain.bsc",

    "filtered_records_eth": "SELECT address,balance,nr_token_transfers,nr_transactions FROM db_blockchain.eth WHERE balance > 0 or nr_token_transfers > 0 or nr_transactions > 0;",
    "filtered_records_bsc": "SELECT address,balance,nr_token_transfers,nr_transactions FROM db_blockchain.bsc WHERE balance > 0 or nr_token_transfers > 0 or nr_transactions > 0;",

    "find_unique_bytecodes_eth": "SELECT COUNT(DISTINCT(bytecode)) FROM eth;",
    "find_unique_bytecodes_bsc": "SELECT COUNT(DISTINCT(bytecode)) FROM bsc;",

    "find_unique_bytecodes_filtered_eth": "SELECT COUNT(DISTINCT(bytecode)) FROM eth WHERE balance > 0 or nr_token_transfers > 0 or nr_transactions > 0;",
    "find_unique_bytecodes_filtered_bsc": "SELECT COUNT(DISTINCT(bytecode)) FROM bsc WHERE balance > 0 or nr_token_transfers > 0 or nr_transactions > 0;",

    "contracts_with_balance_eth": "SELECT address,balance FROM eth WHERE balance > 0;",
    "contracts_with_balance_bsc": "SELECT address,balance FROM bsc WHERE balance > 0;",

    "top_balance_eth": "SELECT address, balance FROM eth WHERE balance > 0 ORDER BY balance DESC LIMIT 10",
    "top_balance_bsc": "SELECT address, balance FROM bsc WHERE balance > 0 ORDER BY balance DESC LIMIT 10",

    "total_vulnerable_contracts_with_reentrancy_eth": "SELECT COUNT(*) FROM (SELECT DISTINCT a.address FROM Address AS a JOIN Result AS r ON r.address_id = a.address_id JOIN Finding AS f ON f.result_id = r.result_id WHERE chain='eth' AND f.vulnerability='Reentrancy' GROUP BY a.address_id) as results;",  # including duplicates
    "total_vulnerable_contracts_with_reentrancy_bsc": "SELECT COUNT(*) FROM (SELECT DISTINCT a.address FROM Address AS a JOIN Result AS r ON r.address_id = a.address_id JOIN Finding AS f ON f.result_id = r.result_id WHERE chain='bsc' AND f.vulnerability='Reentrancy' GROUP BY a.address_id) as results;"
}
