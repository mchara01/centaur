package main

import (
	"database/sql"
	"fmt"
	"os"

	"github.com/ethereum/go-ethereum/ethclient"
	"github.com/ethereum/go-ethereum/rpc"
)

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
	err := db.Ping()
	if err != nil {
		panic(err)
	}
}
