package main

import (
	"fmt" // implements formatted I/O
	"os"
	"strings" // strings manipulation module
	"context" //
	"log"
	"math/big"
	
	"github.com/ethereum/go-ethereum/ethclient"
	"github.com/ethereum/go-ethereum/rpc"
)

func CrawlTransactionsOverBlock(blockNum int64, client *ethclient.Client) []string {
	fmt.Printf("Crawling block %d \n", blockNum)
	
	newBlockNum := big.NewInt(blockNum)
	// context.Background() passes an empty context
	block, _ := client.BlockByNumber(context.Background(), newBlockNum) // returns a block from the current canonical chain

	var addresses []string

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

	return addresses
}

func ConnectToArchive(ethClientUrl string) *ethclient.Client {
	archiveNode, err := ethclient.Dial(ethClientUrl)
	if err != nil {
		fmt.Println("Error detected: ", err)
		os.Exit(1)
	} else {
		fmt.Printf("Connected to %s successfully \n", strings.Split(ethClientUrl, "//")[1])
	}
	return archiveNode
}

func ConnectToRpcClient(ethClientUrl string) *rpc.Client {
	traceClient, err := rpc.Dial(ethClientUrl)
	if err != nil {
		fmt.Println("error: ", err)
		os.Exit(1)
	} else {
		fmt.Printf("Connected to %s successfully \n", strings.Split(ethClientUrl, "//")[1])
	}
	return traceClient
}

func main() {
	blocksSample, _ := readFileLines("blockNumbers.txt")
	fmt.Println(blocksSample)
	os.Exit(0)

	ethClientUrl := "ws://192.168.0.31:19545"
	// fmt.Println(strings.Split(ethClientUrl, "//")[1])
	archiveNode := ConnectToArchive(ethClientUrl)

	addresses := CrawlTransactionsOverBlock(11899002,archiveNode)
	fmt.Println(addresses)
	os.Exit(0)
}