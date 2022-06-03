package main

import (
	"fmt" // implements formatted I/O
	"os"

	"github.com/ethereum/go-ethereum/ethclient"
	// "github.com/ethereum/go-ethereum/rpc"
)

func ConnectToArchive(ethClientUrl string) *ethclient.Client {
	archiveNode, err := ethclient.Dial(ethClientUrl)
	if err != nil {
		fmt.Println("Error detected: ", err)
		os.Exit(1)
	}
	return archiveNode
}

func main() {
	ethClientUrl := "ws://192.168.1.243:19546"
	ConnectToArchive(ethClientUrl)
	fmt.Printf("Connected to %s successfully", ethClientUrl)
	os.Exit(0)
}