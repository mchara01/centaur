# An EVM Cross-chain Vulnerability Analysis

A study on two EVM-based blockchains, namely Ethereum (ETH) and BSC (BNB) to explore their 
states vulnerability wise using automated analysis tools. 

### Prerequisites

Before you begin, ensure you have met the following requirements:

* You have installed of all the required Python dependencies with:  `pip install -r requirements.txt`
* You are using Python >= 3.8
* You have created an account on Etherscan and BscScan and generated an API key
* You have installed [Docker](https://docs.docker.com/get-docker/)

### Running the scripts

* Prepare the local MariaDB database running over a Docker container;
  * Create the files *db_password.txt* and *db_root_password.txt* containing the passwords for a normal user 
and root respectively.
  * Then, start the container using: <br>
`docker-compose -f build/database/docker-compose.yaml up -d`  <br>
  * After, create the two tables in the database where the collected data will be inserted
with: <br>
`docker exec -it <CONTAINER_ID> mysql -u root -p'<ROOT_PASSWORD>' -P 3306 -h 127.0.0.1 < scripts/database/schema.sql`


* Perform random sampling on the blocks of the desired EVM chain (ETH, BNB). Block numbers
generated are stored in a file for the crawler to read from. Sampling size and output location are
passed as arguments: <br>
`python scripts/blockNumberGenerator.py --size 1000 --chain eth --output blockNumbersEth.txt`


* Run the blockchain crawling script that connects to the Ethereum and BSC archive nodes 
(their IP and ports are declared as constants in the scripts) and extracts the contract addresses
and bytecodes from the transactions of the blocks provided. Client (eth, bsc), input file and
whether to use the tracer or not are provided as arguments: <br>
`go run go-src/*.go --client eth --input data/block_samples/<latest_date>/blockNumbersEth.txt --tracer`  <br>
To check only the connection to the archive node and the local database execute:  <br>
`go run go-src/*.go --client eth --check`

  
* Crawl Etherscan or BscScan to gather any other missing data for given smart contract addresses.
An API key must be provided for this script to work: <br>
`python scripts/mainCrawl.py --chain eth --apikey <ENTER_API_KEY_HERE> --output data/logs/results_eth.json --invalid data/logs/exceptions_eth.json`


* Extract the bytecodes from the database and write them in files on the file system. The bytecodes
that are selected have either a balance > 0 or number of transactions > 0 or number of token transfers > 0.
Execute the script to do this with: <br>
`python scripts/bytecodeCreator.py --chain eth`