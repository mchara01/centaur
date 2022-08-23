"""
This file contains a dictionary with useful queries that can be used to view the data inside our database.
"""
QUERIES = {
    "total_eth_addr": "SELECT COUNT(*) FROM Address WHERE chain='eth';",
    "total_bsc_addr": "SELECT COUNT(*) FROM Address WHERE chain='bsc';",

    "filtered_records_eth": "SELECT address,balance,nr_token_transfers,nr_transactions FROM Address WHERE chain='eth' and (balance !='0' or nr_token_transfers > 0 or nr_transactions > 0);",
    "filtered_records_bsc": "SELECT address,balance,nr_token_transfers,nr_transactions FROM Address WHERE chain='bsc' and (balance !='0' or nr_token_transfers > 0 or nr_transactions > 0);",

    "find_unique_bytecodes_eth": "SELECT COUNT(DISTINCT(bytecode_hash)) FROM Address WHERE chain='eth';",
    "find_unique_bytecodes_bsc": "SELECT COUNT(DISTINCT(bytecode_hash)) FROM Address WHERE chain='bsc';",

    "find_unique_bytecodes_filtered_eth": "SELECT COUNT(DISTINCT(bytecode_hash)) FROM Address WHERE chain='eth' and (balance > 0 or nr_token_transfers > 0 or nr_transactions > 0);",
    "find_unique_bytecodes_filtered_bsc": "SELECT COUNT(DISTINCT(bytecode_hash)) FROM Address WHERE chain='bsc' and (balance > 0 or nr_token_transfers > 0 or nr_transactions > 0);",

    "contracts_with_balance_eth": "SELECT address,balance FROM Address WHERE chain='eth' and balance > 0;",
    "contracts_with_balance_bsc": "SELECT address,balance FROM Address WHERE chain='bsc' and balance > 0;",

    "top_balance_eth": "SELECT address, balance FROM Address WHERE chain='eth' and balance > 0 ORDER BY balance DESC LIMIT 10",
    "top_balance_bsc": "SELECT address, balance FROM Address WHERE chain='bsc' and balance > 0 ORDER BY balance DESC LIMIT 10",

    "total_vulnerable_contracts_with_reentrancy_eth": "SELECT COUNT(*) FROM (SELECT DISTINCT a.address FROM Address AS a JOIN Result AS r ON r.address_id = a.address_id JOIN Finding AS f ON f.result_id = r.result_id WHERE chain='eth' AND f.vulnerability='Reentrancy' GROUP BY a.address_id) as results;",  # including duplicates
    "total_vulnerable_contracts_with_reentrancy_bsc": "SELECT COUNT(*) FROM (SELECT DISTINCT a.address FROM Address AS a JOIN Result AS r ON r.address_id = a.address_id JOIN Finding AS f ON f.result_id = r.result_id WHERE chain='bsc' AND f.vulnerability='Reentrancy' GROUP BY a.address_id) as results;",

    "balance_above_zero_eth": "SELECT COUNT(address) FROM Address WHERE chain='eth' and balance != '0';",
    "balance_above_zero_bsc": "SELECT COUNT(address) FROM Address WHERE chain='bsc' and balance != '0';",

    "transactions_above_zero_eth": "SELECT COUNT(address) FROM Address WHERE chain='eth' and nr_transactions > 0;",
    "transactions_above_zero_bsc": "SELECT COUNT(address) FROM Address WHERE chain='bsc' and nr_transactions > 0;",

    "tokens_above_zero_eth": "SELECT COUNT(address) FROM Address WHERE chain='eth' and nr_token_transfers > 0;",
    "tokens_above_zero_bsc": "SELECT COUNT(address) FROM Address WHERE chain='bsc' and nr_token_transfers > 0;",

    "without_anything_eth": "SELECT COUNT(address) FROM Address WHERE chain='eth' and nr_token_transfers = 0 and nr_transactions=0 and balance='0';",
    "without_anything_bsc": "SELECT COUNT(address) FROM Address WHERE chain='bsc' and nr_token_transfers = 0 and nr_transactions=0 and balance='0'",

    "vulnerable_contract_balance_eth": """  SELECT DISTINCT a.address_id, a.balance
                                            FROM Address AS a
                                            JOIN Result R on a.address_id = R.address_id
                                            JOIN Finding F on R.result_id = F.result_id
                                            WHERE a.chain="eth";""",
    "vulnerable_contract_balance_bsc": """  SELECT DISTINCT a.address_id, a.balance
                                            FROM Address AS a
                                            JOIN Result R on a.address_id = R.address_id
                                            JOIN Finding F on R.result_id = F.result_id
                                            WHERE a.chain="bsc";""",

    "total_duplicates_between chains": """SELECT count(DISTINCT bytecode_hash)
                                            FROM(
                                            SELECT bytecode_hash, (sum(chain = 'eth') > 0) AS eth, (sum(chain = 'bsc') > 0) AS bsc
                                            FROM Address
                                            GROUP BY bytecode_hash)
                                            WHERE bsc = 1 AND eth = 1""",

    "duplicates_between_chains": """SELECT address, chain, bytecode_hash
                                    FROM Address
                                    WHERE bytecode_hash IN (
                                    SELECT bytecode_hash
                                    FROM(
                                    SELECT bytecode_hash, (sum(chain = 'eth') > 0) AS eth, (sum(chain = 'bsc') > 0) AS bsc
                                    FROM Address
                                    GROUP BY bytecode_hash)
                                    WHERE bsc = 1 AND eth = 1)
                                    GROUP BY chain, bytecode_hash"""
}
