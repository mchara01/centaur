# Scripts

## Database
The database directory contains the database schema (tables ***eth*** and ***bsc***) and  scripts to backup and restore the database. Other database related files (e.g. docker-compose, passwords) are kept in the build directory.
You can run the ***schema.sql*** file using: <br>
`mysql --host="127.0.0.1" --user="root" --database="db_blockchain" --password="<ENTER_PASSWORD>" < "scripts/database/schema.sql"`

## Result parsers
This directory includes the modules for parsing the result.json files produced by each
tool after analysing an EVM bytecode file. The ***parser.py*** module is used as the main 
file to execute the other parsers. To execute ***parser.py*** you can use: <br>
`python3 parser.py -<TOOL_OF_CHOICE> -d <RESULT_DIRECTORY>`