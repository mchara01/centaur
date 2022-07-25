# Scripts

## Crawl
The crawl directory is made up of the scripts required to crawl the blockchain explorers BscScan and Etherscan.
It is also includes a limit checker to circumvent and restrictions imposed by the blockchain explorers' API. The main
crawling script can be executed with: <br>
```bash
python scripts/crawl/mainCrawl.py --chain eth --apikey <ENTER_API_KEY_HERE> --output data/logs/results_eth.json
--invalid data/logs/exceptions_eth.json
```

## Database
The database directory contains the database schema (tables ***eth*** and ***bsc***) and  scripts to backup and restore the database. Other database related files (e.g. docker-compose, passwords) are kept in the build directory.
You can run the ***schema.sql*** file using: <br>
```bash
mysql --host="127.0.0.1" --user="root" --database="db_blockchain" --password="<ENTER_PASSWORD>" < "scripts/database/schema.sql"`
```

## Result parsers
This directory includes the modules for parsing the result.json files produced by each
tool after analysing an EVM bytecode file. The ***parser.py*** module is used as the main 
file to execute the other parsers. To execute ***parser.py*** you can use: <br>
```bash
python3 parser.py -<TOOL_OF_CHOICE> -d <RESULT_DIRECTORY>`
```

# Utils
Utils contains any other module that supplement the above processes.