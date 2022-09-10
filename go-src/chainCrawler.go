// Block Crawling script
// File is an extension of https://github.com/StefanosChaliasos/inline-assembly/blob/main/go-src/crawl/crawlTransactions.go
// Example run: go run go-src/*.go --client eth --check
//				go run go-src/*.go --client eth --input data/block_samples/<latest_date>/blockNumbersEth.txt --tracer
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

// Database and archive node constant declaration
const (
	DbHost      = "tcp(127.0.0.1:3333)"
	DbName      = "db_blockchain"
	DbUser      = "root"
	DbPass      = "Fm)4dj"
	ETH         = "ws://192.168.0.70:19545"
	BSC         = "ws://192.168.0.31:19547"
	prnInterval = 50
)

// ConcurrentCounter is counter that is goroutine safe
type ConcurrentCounter struct {
	mx    sync.Mutex
	count int64
}

var (
	chain       string
	totalBlocks int
)

// CrawlTransactionsOverBlock is a helper function that each goroutine calls to extract the contract addresses of a
// given block number. Using the block number, it accesses the transactions of the block and finds the transactions
// where the destination is empty. If desired, the tracer is used as well to re-execute transactions and collect
// smart contracts, however this is a time-consuming process.
func CrawlTransactionsOverBlock(blockNum int64, client *ethclient.Client, traceClient *rpc.Client, useTracer bool, counter *ConcurrentCounter) ([]string, []string) {
	// Mutex used only for printing progress
	counter.mx.Lock()
	// Lock so only one goroutine at a time can access the counter and increase it
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
			// Find the 'create contract' transactions (destination of transaction is null)
			if tx.To() == nil {
				receipt, err := client.TransactionReceipt(context.Background(), tx.Hash())
				check(err)
				// Get the contract address in hex
				contractAddr := receipt.ContractAddress.Hex()
				addresses = append(addresses, contractAddr)
				// Get the bytecode of the contract address
				bytecodeAtAddress, err := client.CodeAt(context.Background(), receipt.ContractAddress, newBlockNum)
				check(err)
				bytecodes = append(bytecodes, hex.EncodeToString(bytecodeAtAddress))
			} else {
				if useTracer { // use tracer to re-execute transactions and find contract addresses
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

// WorkerForCrawlTransactions is the code executed by every spawned goroutine. Each goroutine first
// connects to the archive node of choice and gets a client handler. Then, a transaction to the database
// is established. A prepared statement is created and the values that will be passed to it are collected
// by calling the CrawlTransactionsOverBlock() function. The inputChannel works as a queue where a goroutine
// gets a job (block number) from. After collecting the data to be added for every block that the respective
// goroutine handles, it proceeds to insert the new data into the database using a prepared statement.
func WorkerForCrawlTransactions(clientUrl string, inputChannel <-chan int64, wg *sync.WaitGroup, useTracer bool, db *sql.DB, counter *ConcurrentCounter) {
	defer wg.Done()
	// Connect to the archive node at the given client of choice
	// IP and port of client are declared as constants
	var client = ConnectToArchive(clientUrl)
	defer client.Close()

	var traceClient *rpc.Client
	if useTracer { // Check if user wants to use the tracer
		traceClient = ConnectToRpcClient(clientUrl)
		defer traceClient.Close()
	}

	// Start a transaction to the database
	transaction, err := db.Begin()
	check(err)
	defer func() {
		if err != nil {
			err = transaction.Rollback()
			if err != nil {
				return
			}
			return
		}
		err = transaction.Commit()
	}()

	// String to be used as a prepared statement
	var sqlStr string
	if chain == "bsc" {
		sqlStr = "INSERT IGNORE INTO bsc (address, block_number, bytecode) VALUES "
	} else {
		sqlStr = "INSERT IGNORE INTO eth (address, block_number, bytecode) VALUES "
	}
	var values []interface{}

	for block := range inputChannel { // Get an available block number from channel
		addresses, bytecodes := CrawlTransactionsOverBlock(block, client, traceClient, useTracer, counter)
		if addresses == nil || bytecodes == nil {
			continue
		}
		// Collect values to pass to the prepared statement
		for idx, address := range addresses {
			sqlStr += "(?, ?, ?),"
			values = append(values, address, block, bytecodes[idx])
		}
	}

	sqlStr = strings.TrimSuffix(sqlStr, ",") // Remove suffix ,
	// Prepare statement creation
	stmt, err := transaction.Prepare(sqlStr)
	check(err)
	// Format all values at once and execute statement
	_, err = stmt.Exec(values...)
	check(err)
	err = stmt.Close()
	check(err)
}

// GetContractAddresses creates a channel that contains the block numbers that will be crawled.
// The max amount of block numbers that is in the channel at any given time is equal to the
// number of goroutines. Then, goroutines are created and this channel is passed to them, so they
// can extract block numbers from it and crawl them. The workerWaitGroup waits for the collection of
// goroutines to finish, the channel is closed and the amount of time taken for the whole process
// is printed.
func GetContractAddresses(clientUrl string, blocksSample []int64, numWorkers int, useTrace bool, db *sql.DB) {
	timer := time.Now()

	// Buffered channel that contains the block numbers
	blockChannel := make(chan int64, numWorkers)
	counter := ConcurrentCounter{count: 0}
	var workerWaitGroup sync.WaitGroup

	// Add the number of goroutines we want in the wait group
	workerWaitGroup.Add(numWorkers)
	for i := 0; i < numWorkers; i++ {
		// Goroutine creation, blockChannel passed to them to extract blocks for crawling
		go WorkerForCrawlTransactions(clientUrl, blockChannel, &workerWaitGroup, useTrace, db, &counter)
	}

	for _, block := range blocksSample {
		// Send to channel will block only if there's no available buffer to place the value being sent
		blockChannel <- block
	}

	close(blockChannel)
	// Wait blocks until the workerWaitGroup counter is zero, signaling that all
	// goroutines are finished
	workerWaitGroup.Wait()

	elapsed := time.Since(timer).Seconds()

	fmt.Printf("Running time for crawling txs of %d blocks: %f seconds\n", len(blocksSample), elapsed)
}

// check function examines whether the error given as a parameter is nil (0) and
// stops normal execution otherwise. The function was created to avoid repeating
// the same error-checking code snippet after every function return.
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
		CheckDbConnection(db)
		fmt.Printf("Connected to database at %s successfully. \n", DbHost)
	} else { // Main functionality - extract smart contract addresses
		blocksSample, err := ReadFileLines(args.Input) // List of blocks to be crawled
		totalBlocks = len(blocksSample)
		fmt.Printf("Random sampling size: %d \n", totalBlocks)
		check(err)
		GetContractAddresses(ClientUrl, blocksSample, args.Threads, args.Tracer, db)
	}
	os.Exit(0)
}
