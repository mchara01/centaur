package main

import (
	"context"
	"database/sql"
	"encoding/hex"
	"fmt"
	"log"
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
	HOST = "tcp(127.0.0.1:3333)"
	NAME = "db_blockchain"
	USER = "root"
	PASS = "Fm)4dj"
)

func CrawlTransactionsOverBlock(blockNum int64, client *ethclient.Client, traceClient *rpc.Client, useTracer bool, stmt *sql.Stmt) ([]string, []string) {
	fmt.Printf("Crawling block %d \n", blockNum)

	newBlockNum := big.NewInt(blockNum)
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
				bytecodeAtAddress, err := client.CodeAt(context.Background(), receipt.ContractAddress, newBlockNum)
				check(err)
				bytecodes = append(bytecodes, hex.EncodeToString(bytecodeAtAddress))
				_, err = stmt.Exec(contractAddr, blockNum, hex.EncodeToString(bytecodeAtAddress))
				check(err)
			} else {
				if useTracer {
					hash := tx.Hash().Hex()
					contractAddresses := TraceTransaction(hash, traceClient)
					addresses = append(addresses, contractAddresses...)
					for _, addr := range contractAddresses {
						bytecodeAtAddress, err := client.CodeAt(context.Background(), common.HexToAddress(addr), newBlockNum)
						check(err)
						bytecodes = append(bytecodes, hex.EncodeToString(bytecodeAtAddress))
						_, err = stmt.Exec(addr, blockNum, hex.EncodeToString(bytecodeAtAddress))
						check(err)
					}
				}
			}
		}
	}

	return addresses, bytecodes
}

func workerForCrawlTransactions(clientUrl string, inputChannel <-chan int64, wg *sync.WaitGroup, useTracer bool, db *sql.DB) {
	defer wg.Done()
	var client = ConnectToArchive(clientUrl)
	defer client.Close()
	var traceClient *rpc.Client
	if useTracer {
		traceClient = ConnectToRpcClient(clientUrl)
		defer traceClient.Close()
	}
	for block := range inputChannel {
		var resultsAddresses []string
		var resultsBytecodes []string

		tx, txError := db.Begin()
		check(txError)
		stmt, stmtError := tx.Prepare(`INSERT IGNORE INTO eth (address, block_number, bytecode) VALUES (?, ?, ?)`)
		if stmtError != nil {
			log.Fatal("Unable to prepare statement:", stmtError)
		}

		addresses, bytecodes := CrawlTransactionsOverBlock(block, client, traceClient, useTracer, stmt)
		resultsAddresses = append(resultsAddresses, addresses...)
		resultsBytecodes = append(resultsBytecodes, bytecodes...)
		txError = tx.Commit()
		check(txError)
		stmt.Close()
	}
}

func GetContractAddresses(clientUrl string, blocksSample []int64, numWorkers int, useTrace bool, db *sql.DB) {
	timer := time.Now()

	blockChannel := make(chan int64, numWorkers)

	var workerWaitGroup sync.WaitGroup

	for _, block := range blocksSample {
		blockChannel <- block
	}

	for i := 0; i < numWorkers; i++ {
		workerWaitGroup.Add(1)
		go workerForCrawlTransactions(clientUrl, blockChannel, &workerWaitGroup, useTrace, db)
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
		Check     bool   `help:"Check connection to geth archive and exit"`
		ClientUrl string `default:"ws://192.168.0.31:19545" help:"IP and port of geth archive node"`
		Input     string `default:"scripts/blockNumbers.txt" help:"File that contains the block nubmers to be read"`
		Threads   int    `default:"16" help:"Number of workers (Goroutines)"`
		Tracer    bool   `help:"Usage of tracer (significantly slows down process)"`
	}

	arg.MustParse(&args)

	conn := USER + ":" + PASS + "@" + HOST + "/" + NAME + "?charset=utf8"
	db, err := sql.Open("mysql", conn)
	check(err)
	defer db.Close()

	if args.Check {
		ConnectToArchive(args.ClientUrl)
		fmt.Printf("Connected to %s successfully \n", strings.Split(args.ClientUrl, "//")[1])
		checkDBConnection(db)
		fmt.Printf("Connected to %s successfully \n", HOST)
	} else {
		blocksSample, err := readFileLines(args.Input)
		check(err)
		GetContractAddresses(args.ClientUrl, blocksSample, args.Threads, args.Tracer, db)
	}
	os.Exit(0)
}
