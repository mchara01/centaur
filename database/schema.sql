CREATE TABLE Address (
    address_id                  INTEGER PRIMARY KEY,
    block_number                INTEGER NOT NULL,
    address                     TEXT NOT NULL,
    balance                     TEXT NOT NULL,
    nr_transactions             INTEGER NOT NULL,
    nr_token_transfers          INTEGER NOT NULL,
    bytecode_hash               TEXT NOT NULL,
    chain                       TEXT NOT NULL,
    run                         TEXT NOT NULL
);

CREATE TABLE Result (
    result_id                   INTEGER PRIMARY KEY,
    tool                        TEXT NOT NULL,
    duration                    REAL NOT NULL,
    exit_code                   INTEGER NOT NULL,
    success                     BOOLEAN NOT NULL,
    address_id                  INTEGER NOT NULL,
    FOREIGN KEY (address_id) REFERENCES Address (address_id)
);

CREATE TABLE Finding (
    finding_id                  INTEGER PRIMARY KEY,
    vulnerability               TEXT NOT NULL,
    result_id                   INTEGER NOT NULL,
    FOREIGN KEY (result_id) REFERENCES Result (result_id)
);
