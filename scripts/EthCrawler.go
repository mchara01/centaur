package main

import (
	"fmt" // implements formatted I/O
	"os"
//	"strings" // strings manipulation module
	"context" //
	"log"
	"math/big"
	"sync"
	"time"

	"github.com/ethereum/go-ethereum/ethclient"
	"github.com/ethereum/go-ethereum/rpc"
)

func CrawlTransactionsOverBlock(blockNum int64, client *ethclient.Client) ([]string, []string){
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
				if err != nil {
					log.Fatal(err)
				}
				contractAddr := receipt.ContractAddress.Hex()
				addresses = append(addresses, contractAddr)
				bytecodeAddr,_ := client.CodeAt(context.Background(), receipt.ContractAddress, newBlockNum).Hex()
				bytecodes = append(bytecodes, bytecodeAddr)
			} 
			// else {
            //     if useTracer {
            //         hash := tx.Hash().Hex()
            //         contractAddresses := tracer.TraceTransaction(hash, traceClient)
            //         addresses = append(addresses, contractAddresses...)
            //     }
			// }
		}
	}

	return addresses, bytecodes
}

func workerForCrawlTransactions(clientUrl string, inputChannel <-chan int64, wg *sync.WaitGroup) {
	defer wg.Done()
	var client = ConnectToArchive(clientUrl)
	//var traceClient = utils.ConnectToRpcClient(clientUrl)
	for block := range inputChannel {
        var results []string
		var res_bytecodes []string
		addresses, bytecodes := CrawlTransactionsOverBlock(block, client)
		results = append(results, addresses...)
		res_bytecodes = append(res_bytecodes, bytecodes...)
		fmt.Println(results)
		fmt.Println(res_bytecodes)
	}
	client.Close()
}

func GetContractAddresses(clientUrl string, blocksSample []int64, numWorkers int64) {
	timer := time.Now()

	blockChannel := make(chan int64, numWorkers)

	var workerWaitGroup sync.WaitGroup

	for _, block := range blocksSample {
		blockChannel <- block
	}

	var i int64
	for i = 0; i < numWorkers; i++ {
		workerWaitGroup.Add(1)
		go workerForCrawlTransactions(clientUrl, blockChannel, &workerWaitGroup)
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
	//  else {
	// 	fmt.Printf("Connected to %s successfully \n", strings.Split(ethClientUrl, "//")[1])
	// }
	return archiveNode
}

func ConnectToRpcClient(ethClientUrl string) *rpc.Client {
	traceClient, err := rpc.Dial(ethClientUrl)
	if err != nil {
		fmt.Println("error: ", err)
		os.Exit(1)
	} 
	// else {
	// 	fmt.Printf("Connected to %s successfully \n", strings.Split(ethClientUrl, "//")[1])
	// }
	return traceClient
}

func main() {
	blocksSample, _ := readFileLines("scripts/blockNumbers.txt")

	ethClientUrl := "ws://192.168.0.31:19545"
	//archiveNode := ConnectToArchive(ethClientUrl)
	GetContractAddresses(ethClientUrl, blocksSample, 10)

	// addresses := CrawlTransactionsOverBlock(11899002,archiveNode)
	// fmt.Println(addresses)
	os.Exit(0)
}