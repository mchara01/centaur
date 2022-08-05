# SmartBugs: A Framework to Analyze Solidity Smart Contracts

![Smartbugs build](https://github.com/smartbugs/smartbugs/workflows/build/badge.svg)
 <a href="https://github.com/smartbugs/smartbugs/releases">
        <img alt="Smartbugs release" src="https://img.shields.io/github/release/smartbugs/smartbugs.svg">
</a>
<a href="https://github.com/smartbugs/smartbugs/blob/master/LICENSE">
        <img alt="Smartbugs license" src="https://img.shields.io/github/license/smartbugs/smartbugs.svg?color=blue">
</a>
<br />
<a href="#Supported-Tools">
        <img alt="Analysis tools" src="https://img.shields.io/badge/Analysis tools-10-blue">
</a>
<a href="https://github.com/smartbugs/smartbugs/blob/master/dataset">
        <img alt="SB Curated Smart Contracts" src="https://img.shields.io/badge/SB Curated Smart Contracts-143-blue">
</a>
<a href="https://github.com/smartbugs/smartbugs/blob/master/dataset">
        <img alt="SB Wild Smart Contracts" src="https://img.shields.io/badge/SB Wild Smart Contracts-47,398-blue">
</a>

SmartBugs is an execution framework aiming at simplifying the execution of analysis tools on datasets of smart contracts.

## Features

- A plugin system to easily add new analysis tools, based on Docker images;
- Parallel execution of the tools to speed up the execution time;
- An output mechanism that normalizes the way the tools are outputting the results, and simplifies the process of the output across tools.

## Supported Tools


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


## Requirements

- Unix-based system
- [Docker](https://docs.docker.com/install)
- [Python3](https://www.python.org)

## Installation

Once you have Docker and Python3 installed your system, follow the steps:

1. Clone [SmartBugs's repository](https://github.com/smartbugs/smartbugs):

```
git clone https://github.com/smartbugs/smartbugs.git
```

2. Install all the Python requirements:

```
pip3 install -r requirements.txt
```

## Alternative Installation Methods

- We provide a [Vagrant box that you can use to experiment with SmartBugs](https://github.com/smartbugs/smartbugs/tree/master/utils/vagrant)

## Usage

SmartBugs provides a command-line interface that can be used as follows:
```bash
smartBugs.py [-h, --help]
              --list tools          # list all the tools available
              --list datasets       # list all the datasets available
              --dataset DATASET     # the name of the dataset to analyze (e.g. reentrancy)
              --file FILES          # the paths to the folder(s) or the Solidity contract(s) to analyze
              --tool TOOLS          # the list of tools to use for the analysis (all to use all of them) 
              --info TOOL           # show information about tool
              --skip-existing       # skip the execution that already has results
              --processes PROCESSES # the number of process to use during the analysis (by default 1)
              --output-version      # specifies SmartBugs' output version {v1 (Json), v2 (SARIF), all}
              --aggregate-sarif     # aggregates SARIF output per analysed file
              --unique-sarif-output # aggregates all analysis in a single file
              --import-path PATH    # defines project's root directory so that analysis tools are able to import from other files
```

For example, we can analyse all contracts labelled with type `reentrancy` with the tool oyente by executing:

```bash
python3 smartBugs.py --tool oyente --dataset reentrancy
```

To analyze a specific file (or folder), we can use the option `--file`. For example, to run all the tools on the file `dataset/reentrancy/simple_dao.sol`, we can run:

```bash
python3 smartBugs.py --tool all --file dataset/reentrancy/simple_dao.sol
```

By default, results will be placed in the directory `results`. 

## Known Limitations

When running a tool the user must be aware of the solc compatibility. Due to the major changes introduced in solidity v0.5.0, we provide the option to pass another docker image to run contracts with solidity version below v0.5.0. However, please note that there may still be problems with the solidity compiler when compiling older versions of solidity code. 

## Smart Contracts Datasets

We make available three smart contract datasets with SmartBugs:

- **SB Curated**: a curated dataset that contains 143 annotated contracts with 208
  tagged vulnerabilities that can be used to evaluate the accuracy of analysis tools.
- **SB Wild**: a dataset with 47,398 unique contract from the Ethereum network (for details on how they were collected, see [the ICSE 2020 paper](https://arxiv.org/abs/1910.10601))
- **[SolidiFI Benchmark](https://github.com/smartbugs/SolidiFI-benchmark)**: a _remote dataset_ of contracts injected with 9369 bugs of 7 different types.

### SB Curated

[SB Curated](https://github.com/smartbugs/smartbugs/blob/master/dataset) provides a collection of vulnerable Solidity smart contracts organized according to the [DASP taxonomy](https://dasp.co). It is available in the `dataset` repository.

| Vulnerability | Description | Level |
| --- | --- | -- |
| [Reentrancy](https://github.com/smartbugs/smartbugs/blob/master/dataset/reentrancy) | Reentrant function calls make a contract to behave in an unexpected way | Solidity |
| [Access Control](https://github.com/smartbugs/smartbugs/blob/master/dataset/access_control) | Failure to use function modifiers or use of tx.origin | Solidity |
| [Arithmetic](https://github.com/smartbugs/smartbugs/blob/master/dataset/arithmetic) | Integer over/underflows | Solidity |
| [Unchecked Low Level Calls](https://github.com/smartbugs/smartbugs/blob/master/dataset/unchecked_low_level_calls) | call(), callcode(), delegatecall() or send() fails and it is not checked | Solidity |
| [Denial Of Service](https://github.com/smartbugs/smartbugs/blob/master/dataset/denial_of_service) | The contract is overwhelmed with time-consuming computations | Solidity |
| [Bad Randomness](https://github.com/smartbugs/smartbugs/blob/master/dataset/bad_randomness) | Malicious miner biases the outcome | Blockchain |
| [Front Running](https://github.com/smartbugs/smartbugs/blob/master/dataset/front_running) | Two dependent transactions that invoke the same contract are included in one block | Blockchain |
| [Time Manipulation](https://github.com/smartbugs/smartbugs/blob/master/dataset/time_manipulation) | The timestamp of the block is manipulated by the miner | Blockchain |
| [Short Addresses](https://github.com/smartbugs/smartbugs/blob/master/dataset/short_addresses) | EVM itself accepts incorrectly padded arguments | EVM |
| [Unknown Unknowns](https://github.com/smartbugs/smartbugs/blob/master/dataset/other) | Vulnerabilities not identified in DASP 10 | N.A |


### SB Wild

SB Wild is available in a separated repository due to its size: [https://github.com/smartbugs/smartbugs-wild](https://github.com/smartbugs/smartbugs-wild)


### Remote Datasets
You can set any git repository as a _remote dataset_. Smartbugs is distributed with Ghaleb and Pattabiraman's [SolidiFI Benchmark](https://github.com/smartbugs/SolidiFI-benchmark), a dataset of buggy contracts injected with 9369 bugs of 7 different types: reentrancy, timestamp dependency, unhandled exceptions, unchecked send, TOD, integer overflow/underflow, and use of tx.origin. 

To add new remote datasets, update the configuration file [dataset.yaml](config/dataset/dataset.yaml) with
the location of the dataset (`url`), the local directory where the dataset will be located (`local_dir`),
and any relevant `subsets` (if any). As an example, here's the configuration for SolidiFI:

```
solidiFI: 
    - url: git@github.com:smartbugs/SolidiFI-benchmark.git
    - local_dir: dataset/solidiFI
    - subsets: # Accessed as solidiFI/name 
        - overflow_underflow: buggy_contracts/Overflow-Underflow
        - reentrancy: buggy_contracts/Re-entrancy
        - tod: buggy_contracts/TOD
        - timestamp_dependency: buggy_contracts/Timestamp-Dependency
        - unchecked_send: buggy_contracts/Unchecked-Send
        - unhandled_exceptions: buggy_contracts/Unhandled-Exceptions
        - tx_origin: buggy_contracts/tx.origin
```

With this configuration, if we want to run slither in the remote sub-directory `buggy_contracts/tx.origin`,
we can run:

```bash
python3 smartBugs.py --tool slither --dataset solidiFI/tx_origin
```

To run it in the entire dataset, use `solidiFI` instead of `solidiFI/tx_origin`.

When we use a remote dataset for the first time, we are asked to confirm the creation of the local copy.

## Work that uses SmartBugs
- [SmartBugs was used to analyze 47,587 smart contracts](https://joaoff.com/publication/2020/icse) (work published at ICSE 2020). These contracts are available in a [separate repository](https://github.com/smartbugs/smartbugs-wild). The results are also in [their own repository](https://github.com/smartbugs/smartbugs-results).
- [SmartBugs was used to evaluate a simple extension of Smartcheck](https://joaoff.com/publication/2020/ase) (work published at ASE 2020, _Tool Demo Track_)
- ... you are more than welcome to add your own work here!


## License
The license in the file `LICENSE` applies to all the files in this repository,
except for all the smart contracts in the `dataset` folder. 
The smart contracts in this folder are
publicly available, were obtained using the Etherscan APIs, and retain their
original licenses. Please contact us for any additional questions.
