package main

import (
	"database/sql"
	"fmt"
	"os"

	"github.com/ethereum/go-ethereum/ethclient"
	"github.com/ethereum/go-ethereum/rpc"
)

// ConnectToArchive connects a client to the given URL and return a handler to it.
func ConnectToArchive(ClientUrl string) *ethclient.Client {
	archiveNode, err := ethclient.Dial(ClientUrl)
	if err != nil {
		fmt.Println("Error detected: ", err)
		os.Exit(1)
	}
	return archiveNode
}

// ConnectToRpcClient creates a new client for the given URL and return a handler to it.
// This client is used for tracing.
func ConnectToRpcClient(ClientUrl string) *rpc.Client {
	traceClient, err := rpc.Dial(ClientUrl)
	if err != nil {
		fmt.Println("Error detected: ", err)
		os.Exit(1)
	}
	return traceClient
}

// CheckDbConnection checks the connection to a given database.
func CheckDbConnection(db *sql.DB) {
	err := db.Ping()
	if err != nil {
		panic(err)
	}
}
