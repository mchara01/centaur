CREATE TABLE db_blockchain.`eth` (
    `address_id`                  INTEGER NOT NULL AUTO_INCREMENT,
    `block_number`                INTEGER DEFAULT 0,
    `address`                     TEXT NOT NULL,
    `balance`                     TEXT DEFAULT '0',
    `nr_transactions`             INTEGER DEFAULT 0,
    `nr_token_transfers`          INTEGER DEFAULT 0,
    `bytecode`                    TEXT NOT NULL DEFAULT 0,
    PRIMARY KEY (`address_id`),
    CONSTRAINT UC_address UNIQUE (address),
    INDEX(address)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE db_blockchain.`bsc` (
    `address_id`                  INTEGER NOT NULL AUTO_INCREMENT,
    `block_number`                INTEGER DEFAULT 0,
    `address`                     TEXT NOT NULL,
    `balance`                     TEXT DEFAULT '0',
    `nr_transactions`             INTEGER DEFAULT 0,
    `nr_token_transfers`          INTEGER DEFAULT 0,
    `bytecode`                    TEXT NOT NULL DEFAULT 0,
    PRIMARY KEY (`address_id`),
    CONSTRAINT UC_address UNIQUE (address),
    INDEX(address)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
