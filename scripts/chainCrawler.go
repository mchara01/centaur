// Example run: go run *.go --client eth --input scripts/blockNumbersEth.txt --tracer
//				go run *.go --client bsc --input scripts/blockNumbersBsc.txt --tracer
package main

import (
	"context"
	"database/sql"
	"encoding/hex"
	"fmt"
	"math/big"
	"os"
	"strings"
	"sync"
	"time"

	arg "github.com/alexflint/go-arg"
	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/ethclient"
	"github.com/ethereum/go-ethereum/rpc"
	_ "github.com/go-sql-driver/mysql"
)

const (
	DbHost      = "tcp(127.0.0.1:3333)"
	DbName      = "db_blockchain"
	DbUser      = "root"
	DbPass      = "Fm)4dj"
	ETH         = "ws://192.168.0.31:19545"
	BSC         = "ws://192.168.0.31:19547"
	prnInterval = 10
)

type ConcurrentCounter struct {
	mx    sync.Mutex
	count int64
}

var (
	chain       string
	totalBlocks int
)

func CrawlTransactionsOverBlock(blockNum int64, client *ethclient.Client, traceClient *rpc.Client, useTracer bool, counter *ConcurrentCounter) ([]string, []string) {
	//Mutex used only for printing progress
	counter.mx.Lock()
	// Lock so only one goroutine at a time can access the counter
	counter.count++
	if counter.count%prnInterval == 0 {
		percentage := (float64(counter.count) / float64(totalBlocks)) * 100
		fmt.Printf("Crawled %d blocks - (%0.2f %%) \n", counter.count, percentage)
	}
	counter.mx.Unlock()

	var addresses []string
	var bytecodes []string

	newBlockNum := big.NewInt(blockNum)
	block, err := client.BlockByNumber(context.Background(), newBlockNum)
	if err != nil { // Check if archive node knows about block
		fmt.Printf("[Block %d does not exist] \n", blockNum)
		return addresses, bytecodes
	}

	if len(block.Transactions()) > 0 {
		for _, tx := range block.Transactions() {
			// Find the 'create contract' transactions
			if tx.To() == nil {
				receipt, err := client.TransactionReceipt(context.Background(), tx.Hash())
				check(err)
				contractAddr := receipt.ContractAddress.Hex()
				addresses = append(addresses, contractAddr)
				bytecodeAtAddress, err := client.CodeAt(context.Background(), receipt.ContractAddress, newBlockNum)
				check(err)
				bytecodes = append(bytecodes, hex.EncodeToString(bytecodeAtAddress))
			} else {
				if useTracer {
					hash := tx.Hash().Hex()
					contractAddresses := TraceTransaction(hash, traceClient)
					addresses = append(addresses, contractAddresses...)
					for _, addr := range contractAddresses {
						bytecodeAtAddress, err := client.CodeAt(context.Background(), common.HexToAddress(addr), newBlockNum)
						check(err)
						bytecodes = append(bytecodes, hex.EncodeToString(bytecodeAtAddress))
					}
				}
			}
		}
	}
	return addresses, bytecodes
}

func workerForCrawlTransactions(clientUrl string, inputChannel <-chan int64, wg *sync.WaitGroup, useTracer bool, db *sql.DB, counter *ConcurrentCounter) {
	defer wg.Done()
	var client = ConnectToArchive(clientUrl)
	defer client.Close()

	var traceClient *rpc.Client
	if useTracer {
		traceClient = ConnectToRpcClient(clientUrl)
		defer traceClient.Close()
	}

	transaction, txError := db.Begin()
	check(txError)

	for block := range inputChannel {
		//var resultsAddresses []string
		//var resultsBytecodes []string

		addresses, bytecodes := CrawlTransactionsOverBlock(block, client, traceClient, useTracer, counter)
		//resultsAddresses = append(resultsAddresses, addresses...)
		//resultsBytecodes = append(resultsBytecodes, bytecodes...)
		if addresses == nil || bytecodes == nil {
			continue
		}
		var sqlStr string
		if chain == "bsc" {
			sqlStr = "INSERT IGNORE INTO bsc (address, block_number, bytecode) VALUES "
		} else {
			sqlStr = "INSERT IGNORE INTO eth (address, block_number, bytecode) VALUES "
		}
		var values []interface{}

		for idx, address := range addresses {
			sqlStr += "(?, ?, ?),"
			values = append(values, address, block, bytecodes[idx])
		}

		sqlStr = strings.TrimSuffix(sqlStr, ",") // Remove suffix ,
		stmt, _ := transaction.Prepare(sqlStr)   // Prepare statement creation
		_, err := stmt.Exec(values...)           // Format all values at once and execute statement
		check(err)
		txCommitError := transaction.Commit()
		check(txCommitError)
		err = stmt.Close()
		check(err)
	}
}

func GetContractAddresses(clientUrl string, blocksSample []int64, numWorkers int, useTrace bool, db *sql.DB) {
	timer := time.Now()

	// Buffered channel that contains the block numbers.
	blockChannel := make(chan int64, numWorkers)
	counter := ConcurrentCounter{count: 0}
	var workerWaitGroup sync.WaitGroup

	workerWaitGroup.Add(numWorkers)
	for i := 0; i < numWorkers; i++ { // Goroutine creation, blockChannel passed to them for crawling
		go workerForCrawlTransactions(clientUrl, blockChannel, &workerWaitGroup, useTrace, db, &counter)
	}

	for _, block := range blocksSample {
		// Send to channel will block only if there's no available buffer to place the value being sent.
		blockChannel <- block
	}

	close(blockChannel)
	workerWaitGroup.Wait()

	elapsed := time.Since(timer).Seconds()

	fmt.Printf("Running time for crawling txs of %d blocks: %f seconds\n", len(blocksSample), elapsed)
}

func check(e error) {
	if e != nil {
		panic(e)
	}
}

func main() {
	// Argument parsing
	var args struct {
		Check   bool   `help:"Check connection to archive node and exit"`
		Client  string `default:"eth" help:"Choice of archive node to connect to (eth or bsc)"`
		Input   string `default:"scripts/blockNumbersEth.txt" help:"File that contains the block numbers to be read"`
		Threads int    `default:"16" help:"Number of workers (Goroutines)"`
		Tracer  bool   `help:"Usage of tracer (significantly slows down process)"`
	}

	arg.MustParse(&args)

	// Decide which client to connect to
	ClientUrl := ""
	chain = args.Client
	if args.Client == "eth" {
		ClientUrl = ETH
	} else if args.Client == "bsc" {
		ClientUrl = BSC
	} else {
		fmt.Println("Client value must be from range [eth, bsc].")
		os.Exit(0)
	}

	// Establish a connection to the database
	conn := DbUser + ":" + DbPass + "@" + DbHost + "/" + DbName + "?charset=utf8"
	db, err := sql.Open("mysql", conn)
	check(err)
	defer func(db *sql.DB) {
		err := db.Close()
		if err != nil {
			panic(err)
		}
	}(db)

	if args.Check { // Check connection to archive node of desired chain and local database
		ConnectToArchive(ClientUrl)
		fmt.Printf("Connected to %s archive node at %s successfully. \n", args.Client, strings.Split(ClientUrl, "//")[1])
		checkDBConnection(db)
		fmt.Printf("Connected to database at %s successfully. \n", DbHost)
	} else { // Main functionality - extract addresses
		blocksSample, err := readFileLines(args.Input)
		totalBlocks = len(blocksSample)
		fmt.Printf("Random sampling size: %d \n", totalBlocks)
		check(err)
		GetContractAddresses(ClientUrl, blocksSample, args.Threads, args.Tracer, db)
	}
	os.Exit(0)
}
