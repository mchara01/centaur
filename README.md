# An EVM-based Chain Vulnerability Analysis
<a href="https://github.com/mchara01/thesis_test#analysis-tools-used">
        <img alt="Analysis Tools" src="https://img.shields.io/badge/Analysis Tools-8-green">
</a>
<a href="https://github.com/mchara01/thesis_test/tree/main/data/dataset/eth">
        <img alt="ETH Smart Contracts" src="https://img.shields.io/badge/ETH Smart Contracts-123-green">
</a>
<a href="https://github.com/mchara01/thesis_test/tree/main/data/dataset/bsc">
        <img alt="BSC Smart Contracts" src="https://img.shields.io/badge/BSC Smart Contracts-111-green">
</a>
<a href="https://github.com/mchara01/thesis_test/">
        <img alt="Repository Size" src="https://img.shields.io/github/repo-size/mchara01/thesis_test">
</a>

A study on two EVM-based blockchains, namely Ethereum (ETH) and BSC (BNB). It explores their 
vulnerability using smart contract automated analysis tools for EVM bytecode. Our codebase 
artifact is encapsulated into the _**Centaur**_ framework. The
framework also uses [SmartBugs](https://github.com/smartbugs/smartbugs) for analysing the dataset of
smart contract bytecodes using multiple analysis tools and it is easy to extend it to support other
EVM chains.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Step-by-Step Analysis Procedure](#procedure)
   1. [Database Creation](#database)
   2. [Data Collection](#data-collection)
4. [Running the SmartBugs Framework](#smartbugs)
5. [Parsing the Analysis Tools Results](#parsing)
6. [Centaur Usage](#usage)
7. [Analysis Tools](#analysis-tools)
8. [Vulnerability Taxonomy](#taxonomy)
9. [License](#license)

## Prerequisites <a name="prerequisites"></a>

Before you begin, ensure you have met the following requirements:

* You have installed of all the required Python and Shell dependencies with: <br> 
`pip install -r requirements.txt` and <br>
`apt-get install -y cowsay figlet`
* You are using Python >= 3.8 and Golang == 1.17
* You have created an account on Etherscan and BscScan and generated an API key on both
* You have installed [Docker](https://docs.docker.com/get-docker/) and [docker-compose](https://docs.docker.com/compose/install/)
* You are using a UNIX-like OS

## Installation <a name="installation"></a>
> Note: We recommend using _Centaur_ via its Docker image (Option 2) as it encapsulates
all the required dependencies and allows running the framework without needing to install
anything on your system.


Option 1: Once all the above prerequisites are met, you can clone this repository with:
```bash
git clone https://github.com/mchara01/thesis_test.git
```

Option 2: Use our Docker image <a name="option2"></a>
```bash
docker pull mchara01/centaur
```

Once installed, the `Centaur` CLI framework will be available for usage.


## Step-by-Step Analysis Procedure <a name="procedure"></a>

The following sections constituted the steps required to replicate the process of analysing the EVM bytecode of smart contracts.

### Database Creation <a name="database"></a>

* Prepare the local MariaDB database running over a Docker container;
  * Create the files *db_password.txt* and *db_root_password.txt* containing the passwords for a normal user 
and root respectively.
  * Then, start the container using: <br>
`docker-compose -f build/database/docker-compose.yaml up -d`  <br>
  * After, create the two tables in the database where the collected data will be inserted
with: <br>
`docker exec -it <CONTAINER_ID> mysql -u root -p'<ROOT_PASSWORD>' -P 3306 -h 127.0.0.1 < scripts/database/schema.sql`

### Data Collection <a name="data-collection"></a>

* Perform random sampling on the blocks of the desired EVM chain (ETH, BNB). Block numbers
generated are stored in a file for the crawler to read from. Sampling size and output location are
passed as arguments: <br>
`python scripts/utils/blockNumberGenerator.py --size 1000 --chain eth --output blockNumbersEth.txt`


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
`python scripts/crawl/mainCrawl.py --chain eth --apikey <ENTER_API_KEY_HERE> --output data/logs/results_eth.json --invalid data/logs/exceptions_eth.json`


* At this point, the database is populated with all the required data. If you wish to perform a backup of
the database, execute the following command: (***mysqldump*** needs to be installed first )<br>
`bash scripts/database/backup/db_backup.sh` <br>
 If you need restore the backup use: <br>
`bash scripts/database/backup/db_restore.sh` <br>
 Before using the above two scripts, make sure first you change the ***DB_BACKUP_PATH***
variable to match the locations on your local file system.


* Extract the bytecodes from the database and write them in files on the file system. The smart contracts of the
respective bytecodes that are selected must pass one of the following conditions:
  * a balance > 0 **or** 
  * number of transactions > 0 **or** 
  * number of token transfers > 0 <br>

  Execute the script that does this with: <br>
`python scripts/utils/bytecodeToFileCreator.py --chain eth`


### Running the SmartBugs Framework <a name="smartbugs"></a>

After finishing successfully with the above steps, we have everything we need ready to run the [SmartBugs](https://github.com/smartbugs/smartbugs) framework and execute
the EVM bytecode analysis tools on the EVM bytecodes we have written on the local file system. We can do this using: <br>
```bash
python smartbugs_bytecode/smartBugs.py --tool all --dataset eth_bc --bytecode
```

Please check the official repository of SmartBugs for more details on how to run the framework.

**Note**: Bear in mind that SmartBugs will execute 9 tools on every single contract
from the corpus of contracts you will provide to it. Thus, this particular step may take a significant amount of time 
to complete (in our case it took approximately three days for _334_ contracts). We recommend 
using a tool such as [tmux](https://github.com/tmux/tmux/wiki) that enable keeping a session alive for long periods of time even when logging out of the machine running the framework.

### Parsing the Analysis Tools Results <a name="parsing"></a>

Once SmartBugs has finished, a _result.json_ is created for every contract at the 
***smartbugs_bytecode/results/<TOOL_NAME>*** directory. To parse these results, we use
**parser.py** file in the ***scripts*** directory. This file is used as the main
point to execute every tool result parsers that reside in the ***scripts/result_parsing*** directory.
To parse a tool's results use: <br>
`python3 scripts/parser.py -t <TOOL_OF_CHOICE> -d <RESULT_DIRECTORY>` <br>
You can replace the `<TOOL_OF_CHOICE>` placeholder with `all` if you want to parse the results of every
tool and print their results on the screen.
The amount of time taken to process all contracts by every tool can be found on the last line of `results/logs/SmartBugs_<DATE>.log`

## Centaur Usage <a name="usage"></a>
As an attempt to make the above [Step-by-Step Procedure](#procedure) easier, we created the Centaur framework which
executes all the above steps automatically, printing relevant messages. The easiest way to run Centaur is
with Docker. To do this, we must first make sure we have the respective image either by pulling it
(see [Option 2](#option2)) or by building it with:
```bash
docker build --no-cache -t centaur:1.0 -f Dockerfile .
```
Then, we can run the _Centaur_ script with:
```bash
docker run centaur ./run_tool.sh <API_KEY>
```
Before running the above command, make sure you have added the desired values for the constants
in the _**CONSTANTS DECLARATION**_ section in the _run_tool.sh_ script.

## Analysis Tools <a name="analysis-tools"></a>
We have gathered information about plenty of smart contract security analysis tools but only
 a subset of these can be included in our study as we want these tools to fulfil some criteria.
More specifically, we wanted tools that work on EVM bytecode (not source code only) and 
can execute without the need of human interaction (e.g. no GUI). The list of tools
that pass these requirements along with their open-source repository and paper link are the following:

|     | Analysis Tool                                                | Paper                                                                                                                                                                                                  |
|-----|--------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1   | [Conkas](https://github.com/nveloso/conkas)                  | [link](https://fenix.tecnico.ulisboa.pt/downloadFile/1689244997262417/94080-Nuno-Veloso_resumo.pdf)                                                                                                    |
| 2   | [HoneyBadger](https://github.com/christoftorres/HoneyBadger) | [link](https://www.usenix.org/system/files/sec19-torres.pdf)                                                                                                                                           |
| 3   | [MadMax](https://github.com/nevillegrech/MadMax)             | [link](https://dl.acm.org/doi/pdf/10.1145/3276486)                                                                                                                                                     |
| 4   | [Maian](https://github.com/MAIAN-tool/MAIAN)                 | [link](https://arxiv.org/pdf/1802.06038.pdf)                                                                                                                                                           |
| 5   | [Mythril](https://github.com/ConsenSys/mythril-classic)      | [link](https://conference.hitb.org/hitbsecconf2018ams/materials/WHITEPAPERS/WHITEPAPER%20-%20Bernhard%20Mueller%20-%20Smashing%20Ethereum%20Smart%20Contracts%20for%20Fun%20and%20ACTUAL%20Profit.pdf) |
| 6   | [Osiris](https://github.com/christoftorres/Osiris)           | [link](https://orbilu.uni.lu/bitstream/10993/36757/1/osiris.pdf)                                                                                                                                       |
| 7   | [Oyente](https://github.com/melonproject/oyente)             | [link](https://eprint.iacr.org/2016/633.pdf)                                                                                                                                                           |
| 8   | [Securify](https://github.com/eth-sri/securify2)             | [link](https://arxiv.org/pdf/1806.01143.pdf)                                                                                                                                                           |
| 9   | [Vandal](https://github.com/usyd-blockchain/vandal)          | [link](https://arxiv.org/pdf/1809.03981.pdf)                                                                                                                                                           |

## Vulnerability Taxonomy <a name="taxonomy"></a>
For categorising the vulnerabilities found by the smart contract analysis tools, we used the [DASP10](https://dasp.co/) 
taxonomy. The taxonomy is constituted by the most popular vulnerabilities currently in smart contracts.
Categories _Bad Randomness_ (6) and _Short Address Attack_ (9) are not discovered by any of the tools that where 
used in this study and category _Unknown Unknowns_ (10) includes any vulnerabilities that do not
fall in any other category.

## License <a name="license"></a>
This project is licensed under the terms of the MIT license, which can be found at the `LICENSE` file. 
This license applies to the whole codebase except for the SmartBugs framework and .hex and .sol files found
in the data directory, which are publicly available and retain their original licenses.
