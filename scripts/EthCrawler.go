package main

import (
	"fmt" // implements formatted I/O
	"os"
	"strings" // strings manipulation module
	"context"
	"sync"
	"time"
	"encoding/hex"
	"math/big"
	"database/sql"

	arg "github.com/alexflint/go-arg"
	_ "github.com/go-sql-driver/mysql"
	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/ethclient"
	"github.com/ethereum/go-ethereum/rpc"
)

const (
	HOST = "tcp(127.0.0.1:3333)"
	NAME = "db_blockchain"
	USER = "root"
	PASS = "Fm)4dj"
)

func CrawlTransactionsOverBlock(blockNum int64, client *ethclient.Client, traceClient *rpc.Client, useTracer bool) ([]string, []string){
	fmt.Printf("Crawling block %d \n", blockNum)
	
	newBlockNum := big.NewInt(blockNum)
	// context.Background() passes an empty context
	block, _ := client.BlockByNumber(context.Background(), newBlockNum)

	var addresses []string
	var bytecodes []string
	//var balances  []big.Int
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
				// balance,err := client.BalanceAt(context.Background(), receipt.ContractAddress, newBlockNum)
				// check(err)
				// balances := append(balances, *balance)
				// fmt.Print(balances)
			} else {
                if useTracer {
                    hash := tx.Hash().Hex()
                    contractAddresses := TraceTransaction(hash, traceClient)
                    addresses = append(addresses, contractAddresses...)
					for _,addr := range contractAddresses {
						bytecodeAddr,err := client.CodeAt(context.Background(), common.HexToAddress(addr), newBlockNum)
						check(err)
						bytecodes = append(bytecodes, hex.EncodeToString(bytecodeAddr))
					}
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

func ConnectToArchive(ClientUrl string) *ethclient.Client {
	archiveNode, err := ethclient.Dial(ClientUrl)
	if err != nil {
		fmt.Println("Error detected: ", err)
		os.Exit(1)
	}
	return archiveNode
}

func ConnectToRpcClient(ClientUrl string) *rpc.Client {
	traceClient, err := rpc.Dial(ClientUrl)
	if err != nil {
		fmt.Println("Error detected: ", err)
		os.Exit(1)
	} 
	return traceClient
}

func checkDBConnection(db *sql.DB) {
	error := db.Ping()
	if error != nil {
		panic(error)
	} 
}

func check(e error) {
    if e != nil {
        panic(e)
    }
}

func main() {

	var args struct {
        Check        bool   `help:"Check connection to geth archive and exit"`
		ClientUrl	 string `default:"ws://192.168.0.31:19545"`
		Input		 string `default:"scripts/blockNumbers.txt"`
		Threads      int64  `default:"16"`
        Tracer       bool   
	}

    arg.MustParse(&args)
	
	// TODO
	conn := USER + ":" + PASS + "@" + HOST + "/" + NAME + "?charset=utf8"
	db, err := sql.Open("mysql", conn)
	if err != nil {
		panic(err)
	}
	defer db.Close()

	if args.Check {
		ConnectToArchive(args.ClientUrl)
        fmt.Printf("Connected to %s successfully \n", strings.Split(args.ClientUrl, "//")[1])
		checkDBConnection(db)
		fmt.Printf("Connected to %s successfully \n", HOST)
	} else {
		blocksSample, _ := readFileLines(args.Input)
		GetContractAddresses(args.ClientUrl, blocksSample, args.Threads, args.Tracer)
    }
	os.Exit(0)
}
