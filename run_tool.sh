#!/bin/sh

# Colour constant declaration
RED=$(tput setaf 1)
GREEN=$(tput setaf 2)
YELLOW=$(tput setaf 3)
CYAN=$(tput setaf 6)
ENDCOLOR=$(tput sgr0)

if [ "$#" -ne 1 ]; then
    printf "%sIllegal number of parameters. Please pass an API_KEY.%s\n" "$RED" "$ENDCOLOR" >&2
    exit 2
fi

################################################################
################## CONSTANTS DECLARATION  ######################

# Constant declaration
SAMPLE_SIZE=1000
CHAIN=eth
OUTPUT_FILE_NAME=blockNumbersEth.txt
TIMESTAMP_DIR=data/block_samples/01072022_161632/blockNumbersEth.txt
API_KEY="$1"
CRAWL_OUTPUT=data/logs/results_eth.json
CRAWL_INVALID=data/logs/exceptions_eth.json
DATASET=eth_bc
RESULTS_DIRECTORY=20220710_2258

#################################################################

figlet "Centaur"
echo "************************************"
echo ""

START=$(date +%s.%N)


printf "%sDatabase Creation%s\n" "$CYAN" "$ENDCOLOR"
printf "=================\n"

printf "%s[+] Deploying a MariaDB database instance with name db_blockchain...%s\n" "$GREEN" "$ENDCOLOR"


# Check if container is not running or has exited
if [ ! "$(docker ps -q -f name=db_blockchain)" ]; then
    if [ "$(docker ps -aq -f status=exited -f name=db_blockchain)" ]; then
        # Remove exited container
        docker rm db_blockchain
    fi

    # Deploy container
    if docker-compose -f build/database/docker-compose.yaml up -d ; then
        printf "Successfully deployed!\n"
    else
        printf "%s[-] Failure to Deploy Database%s\n" "$RED" "$ENDCOLOR"
        printf "%s[-] Exiting...%s\n" "$RED" "$ENDCOLOR"
    fi
else
  printf "%sWarning:%s db_blockchain database is already running!\n" "$YELLOW" "$ENDCOLOR"
fi

echo ""
printf "%s[+] Creation of ETH and BSC tables in db_blockchain...%s\n" "$GREEN" "$ENDCOLOR"

docker exec "$(docker ps -q -f name=db_blockchain)" mysql -u root -p'Fm)4dj' -P 3306 -h 127.0.0.1 < scripts/database/schema.sql

echo ""
printf "%sData Collection%s\n" "$CYAN" "$ENDCOLOR"
printf "===============\n"

printf "%s[+] Generating random sample of block numbers...%s\n" "$GREEN" "$ENDCOLOR"
python scripts/utils/blockNumberGenerator.py --size $SAMPLE_SIZE --chain $CHAIN --output $OUTPUT_FILE_NAME
printf "%sDone%s -> You can find the sample at: data/block_samples/<timestamp>/%s \n" "$GREEN" "$ENDCOLOR" "$OUTPUT_FILE_NAME"

echo ""
printf "%s[+] Checking the connection to the archive node...%s\n" "$GREEN" "$ENDCOLOR"
go mod tidy
go run go-src/*.go --client $CHAIN --check
if [ $? != 0 ]; then
  printf "%s[-] Error connecting to archive node\nExiting...%s\n" "$RED" "$ENDCOLOR"
  exit
fi

echo ""
printf "%s[+] Collecting data from the archive node...%s\n" "$GREEN" "$ENDCOLOR"
go run go-src/*.go --client $CHAIN --input $TIMESTAMP_DIR --tracer

echo ""
printf "%s[+] Crawling blockchain explorer to gather extra data for the collected smart contract addresses...%s\n" "$GREEN" "$ENDCOLOR"
python scripts/crawl/mainCrawl.py --chain $CHAIN --apikey "$API_KEY" --output $CRAWL_OUTPUT --invalid $CRAWL_INVALID

echo ""
printf "%s[+] Extract the bytecodes from the database and write them in files on the file system...%s\n" "$GREEN" "$ENDCOLOR"
python scripts/utils/bytecodeToFileCreator.py --chain eth

echo ""
printf "%sRunning the SmartBugs Framework%s\n" "$CYAN" "$ENDCOLOR"
printf "===============================\n"
python smartbugs_bytecode/smartBugs.py --tool all --dataset $DATASET --bytecode

echo ""
printf "%sParsing the Analysis Tools Results%s\n" "$CYAN" "$ENDCOLOR"
printf "==================================\n"
python3 parser.py -t all -d $RESULTS_DIRECTORY

END=$(date +%s.%N)
DIFF=$(echo "$END - $START" | bc)
echo "Time taken: " "$DIFF"