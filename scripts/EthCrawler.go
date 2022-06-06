package main

import (
	"fmt" // implements formatted I/O
	"os"
//	"strings" // strings manipulation module
	"context"
//	"log"
	"math/big"
	"sync"
	"time"
	"encoding/hex"

	"github.com/ethereum/go-ethereum/ethclient"
	"github.com/ethereum/go-ethereum/rpc"
)

func CrawlTransactionsOverBlock(blockNum int64, client *ethclient.Client, traceClient *rpc.Client, useTracer bool) ([]string, []string){
	fmt.Printf("Crawling block %d \n", blockNum)
	
	newBlockNum := big.NewInt(blockNum)
	// context.Background() passes an empty context
	block, _ := client.BlockByNumber(context.Background(), newBlockNum)

	var addresses []string
	var bytecodes []string

	if len(block.Transactions()) > 0 {
		for _, tx := range block.Transactions() {
			// Find the Create contract transactions
			if tx.To() == nil {
				receipt, err := client.TransactionReceipt(context.Background(), tx.Hash())
				check(err)
				contractAddr := receipt.ContractAddress.Hex()
				addresses = append(addresses, contractAddr)
				bytecodeAddr,err := client.CodeAt(context.Background(), receipt.ContractAddress, newBlockNum)
				check(err)
				bytecodes = append(bytecodes, hex.EncodeToString(bytecodeAddr))
			} else {
                if useTracer {
                    hash := tx.Hash().Hex()
                    contractAddresses := TraceTransaction(hash, traceClient)
                    addresses = append(addresses, contractAddresses...)
                }
			}
		}
	}

	return addresses, bytecodes
}

func workerForCrawlTransactions(clientUrl string, inputChannel <-chan int64, wg *sync.WaitGroup, useTracer bool) {
	defer wg.Done()
	var client = ConnectToArchive(clientUrl)
	var traceClient = ConnectToRpcClient(clientUrl)
	for block := range inputChannel {
        var results []string
		var res_bytecodes []string
		addresses, bytecodes := CrawlTransactionsOverBlock(block, client, traceClient, useTracer)
		results = append(results, addresses...)
		res_bytecodes = append(res_bytecodes, bytecodes...)
		fmt.Println(results)
		fmt.Println(res_bytecodes)
	}
	client.Close()
}

func GetContractAddresses(clientUrl string, blocksSample []int64, numWorkers int64, useTrace bool) {
	timer := time.Now()

	blockChannel := make(chan int64, numWorkers)

	var workerWaitGroup sync.WaitGroup

	for _, block := range blocksSample {
		blockChannel <- block
	}

	var i int64
	for i = 0; i < numWorkers; i++ {
		workerWaitGroup.Add(1)
		go workerForCrawlTransactions(clientUrl, blockChannel, &workerWaitGroup, useTrace)
	}

	close(blockChannel)
	workerWaitGroup.Wait()

	elapsed := time.Since(timer).Seconds()

	fmt.Printf("Running time for crawling txs of %d blocks: %f seconds\n", len(blocksSample), elapsed)
}


func ConnectToArchive(ethClientUrl string) *ethclient.Client {
	archiveNode, err := ethclient.Dial(ethClientUrl)
	if err != nil {
		fmt.Println("Error detected: ", err)
		os.Exit(1)
	}
	return archiveNode
}

func ConnectToRpcClient(ethClientUrl string) *rpc.Client {
	traceClient, err := rpc.Dial(ethClientUrl)
	if err != nil {
		fmt.Println("Error detected: ", err)
		os.Exit(1)
	} 
	return traceClient
}


func check(e error) {
    if e != nil {
        panic(e)
    }
}

func main() {
	blocksSample, _ := readFileLines("scripts/blockNumbers.txt")

	ethClientUrl := "ws://192.168.0.31:19545"
	GetContractAddresses(ethClientUrl, blocksSample, 10, true)

	// fmt.Println(addresses)
	os.Exit(0)
}