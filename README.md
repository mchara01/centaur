## An EVM Cross-chain Vulnerability Analysis

A study on two EVM-based blockchains, namely Ethereum (ETH) and BSC (BNB) to explore their 
states vulnerability wise using automated analysis tools. 

### Prerequisites

Before you begin, ensure you have met the following requirements:

* You have installed of all the required Python modules with:  `pip install -r requirements.txt`
* You are using Python >= 3.8
* You have created an account on Etherscan and BscScan and generated an API key

### Running the scripts

* Perform random sampling on the blocks of the desired EVM chain (ETH, BNB). Block numbers
generated are stored in a file for the crawler to read from. Sampling size and output location are
passed as arguments: <br>
`python blockNumberGenerator.py --size 100 --output blockNumbersEth.txt`


* Run the blockchain crawling script that connects to the Ethereum and BSC archive nodes 
(their IP and ports are declared as constants in the scripts) and extracts the contract addresses
and bytecodes from the transactions of the blocks provided. Client (eth, bsc), input file and
whether to use the tracer or not are provided as arguments: <br>
`go run go-src/*.go --client eth --input scripts/blockNumbersEth.txt --tracer`


* Crawl Etherscan or BscScan to gather any other missing data for given smart contract addresses.
An API key must be provided for this script to work: <br>
`python etherscanCrawl.py --apikey <ENTER_API_KEY_HERE>`

All data collected is added into a local MariaDb database running over a Docker container.