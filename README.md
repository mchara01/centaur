# An EVM-based Chain Vulnerability Analysis

A study on two EVM-based blockchains, namely Ethereum (ETH) and BSC (BNB) to explore their 
states vulnerability wise using smart contract automated analysis tools for EVM bytecode. 

## Prerequisites

Before you begin, ensure you have met the following requirements:

* You have installed of all the required Python dependencies with: <br> 
`pip install -r requirements.txt`
* You are using Python >= 3.8
* You have created an account on Etherscan and BscScan and generated an API key on both
* You have installed [Docker](https://docs.docker.com/get-docker/)
* You are using a UNIX-like OS

## Installation

Once all the above prerequisites are met, you can clone this repository with: <br>
`git clone https://github.com/mchara01/thesis_test.git`

## Step-by-Step Analysis Procedure

The following are the steps required to replicate the process of analysing the EVM bytecode of smart contracts.

### Database Creation

* Prepare the local MariaDB database running over a Docker container;
  * Create the files *db_password.txt* and *db_root_password.txt* containing the passwords for a normal user 
and root respectively.
  * Then, start the container using: <br>
`docker-compose -f build/database/docker-compose.yaml up -d`  <br>
  * After, create the two tables in the database where the collected data will be inserted
with: <br>
`docker exec -it <CONTAINER_ID> mysql -u root -p'<ROOT_PASSWORD>' -P 3306 -h 127.0.0.1 < scripts/database/schema.sql`

### Data Collection

* Perform random sampling on the blocks of the desired EVM chain (ETH, BNB). Block numbers
generated are stored in a file for the crawler to read from. Sampling size and output location are
passed as arguments: <br>
`python scripts/blockNumberGenerator.py --size 1000 --chain eth --output blockNumbersEth.txt`


* Run the blockchain crawling script that connects to the Ethereum and BSC archive nodes 
(their IP and ports are declared as constants in the scripts) and extracts the contract addresses
and bytecodes from the transactions of the blocks provided. Client (eth, bsc), input file and
whether to use the tracer or not are provided as arguments: <br>
`go mod tidy` <br>
`go run go-src/*.go --client eth --input data/block_samples/<latest_date>/blockNumbersEth.txt --tracer`  <br>
To check only the connection to the archive node and the local database execute:  <br>
`go run go-src/*.go --client eth --check`

  
* Crawl Etherscan or BscScan to gather any other missing data for given smart contract addresses.
An API key must be provided for this script to work: <br>
`python scripts/mainCrawl.py --chain eth --apikey <ENTER_API_KEY_HERE> --output data/logs/results_eth.json --invalid data/logs/exceptions_eth.json`


* At this point, the database is populated with all the required data. If you wish to perform a backup of
the database, execute the following command: (***mysqldump*** needs to be installed first )<br>
`bash scripts/database/backup/db_backup.sh`


* Extract the bytecodes from the database and write them in files on the file system. The bytecodes
that are selected pass one of the following conditions:
  * a balance > 0 **or** 
  * number of transactions > 0 **or** 
  * number of token transfers > 0 <br>

  Execute the script to do this with: <br>
`python scripts/bytecodeToFileCreator.py --chain eth`


### Running the SmartBugs Framework

After finishing successfully with the above steps, we have everything we need ready to run the [SmartBugs](https://github.com/smartbugs/smartbugs) framework and execute
the EVM bytecode analysis tools on the EVM bytecodes we have written on the local file system. We can do this using: <br>
`python smartBugs.py --tool all --dataset ` <br>

**Note**: Bear in mind that SmartBugs will execute 9 tools on every single contract
from the corpus of contracts you will provide to it. Thus, this particular step may take a significant amount of time 
to complete (in our case it took approximately three days for _334_ contracts). We recommend 
using a tool such as [tmux](https://github.com/tmux/tmux/wiki) that enable keeping a session alive for long periods of time even when logging out of the machine running the framework.

### Parsing the Analysis Tools Results

Once SmartBugs has finished, a _result.json_ is created for every contract at the 
***smartbugs_bytecode/results/<TOOL_NAME>*** directory. To parse these results, we use
**parser.py** file in the ***scripts*** directory. This file is used as the main
point to execute every tool result parsers that reside in the ***scripts/result_parsing*** directory.
To parse a tool's results use: <br>
`python3 parser.py -t <TOOL_OF_CHOICE> -d <RESULT_DIRECTORY>` <br>
You can replace the `<TOOL_OF_CHOICE>` placeholder with ***all*** if you want to parse the results of every
tool and print their results on the screen.
The amount of time taken to process all contracts by every tool can be found on the last line of `results/logs/SmartBugs_<DATE>.log`

## Analysis Tools Used
We have gathered information about plenty of smart contract security analysis tools but only
 a subset of these can be included in our study as we want these tools to fulfil some criteria.
More specifically, we wanted tools that work on EVM bytecode (not source code only) and 
can execute without the need of human interaction (e.g. no GUI). The list of tools
that pass these requirements along with their open-source repository and paper link are the following:

|     | Analysis Tool                                                | Paper                                                                                                                                                                                                  |
|-----|--------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1   | [Conkas](https://github.com/nveloso/conkas)                  | [link](https://fenix.tecnico.ulisboa.pt/downloadFile/1689244997262417/94080-Nuno-Veloso_resumo.pdf)                                                                                                    |
| 2   | [HoneyBadger](https://github.com/christoftorres/HoneyBadger) | [link](https://www.usenix.org/system/files/sec19-torres.pdf)                                                                                                                                           |
| 3   | [Maian](https://github.com/MAIAN-tool/MAIAN)                 | [link](https://arxiv.org/pdf/1802.06038.pdf)                                                                                                                                                           |
| 4   | [Mythril](https://github.com/ConsenSys/mythril-classic)      | [link](https://conference.hitb.org/hitbsecconf2018ams/materials/WHITEPAPERS/WHITEPAPER%20-%20Bernhard%20Mueller%20-%20Smashing%20Ethereum%20Smart%20Contracts%20for%20Fun%20and%20ACTUAL%20Profit.pdf) |
| 5   | [Osiris](https://github.com/christoftorres/Osiris)           | [link](https://orbilu.uni.lu/bitstream/10993/36757/1/osiris.pdf)                                                                                                                                       |
| 6   | [Oyente](https://github.com/melonproject/oyente)             | [link](https://eprint.iacr.org/2016/633.pdf)                                                                                                                                                           |
| 7   | [Securify](https://github.com/eth-sri/securify2)             | [link](https://arxiv.org/pdf/1806.01143.pdf)                                                                                                                                                           |
| 8   | [Vandal](https://github.com/usyd-blockchain/vandal)          | [link](https://arxiv.org/pdf/1809.03981.pdf)                                                                                                                                                           |

