package main

import (
	"fmt"
	"strconv"

	"github.com/ethereum/go-ethereum/rpc"
)

func ExtractCallsOfTransaction(res CallTracesOfTransaction) (calls []TransactionCall) {
	calls = []TransactionCall{}
	if len(res.Calls) > 0 {
		calls = append(calls, TransactionCall{
			Type:           res.Type,
			From:           res.From.Hex(),
			To:             res.To.Hex(),
			BytesSignature: res.Input.String(),
			Error:          res.Error,
			Index:          "root",
		})

		if res.Value != nil {
			calls[0].Value = res.Value.String()
		}
		parentIndex := ""
		for i, r := range res.Calls {
			calls = append(calls, ExtractSubCallsOfTransaction(r, i, parentIndex)...)
		}
	}
	return calls
}

func ExtractSubCallsOfTransaction(res CallTracesOfTransaction, i int, parentIndex string) (calls []TransactionCall) {
	calls = []TransactionCall{}
	calls = append(calls, TransactionCall{
		Type:           res.Type,
		From:           res.From.Hex(),
		To:             res.To.Hex(),
		BytesSignature: res.Input.String(),
		Error:          res.Error,
		Index:          parentIndex + "_" + strconv.Itoa(i),
	})

	if res.Value != nil {
		calls[0].Value = res.Value.String()
	}

	newParentIndex := parentIndex + "_" + strconv.Itoa(i)
	if len(res.Calls) > 0 {
		for i, r := range res.Calls {
			calls = append(calls, ExtractSubCallsOfTransaction(r, i, newParentIndex)...)
		}
	}
	return calls
}

func ProcessTraces(calls []TransactionCall) []string {
	var addresses []string
	for _, c := range calls {
		if c.Type == "CREATE" || c.Type == "CREATE2" {
			addresses = append(addresses, c.To)
		}
	}
	return addresses
}

func TraceTransaction(txHash string, traceClient *rpc.Client) []string {
	var res CallTracesOfTransaction

	var rpcParameters TraceConfig

	rpcParameters.Tracer = "callTracer"
	rpcParameters.Timeout = "20s"

	err := traceClient.Call(&res, "debug_traceTransaction", txHash, &rpcParameters)
	if err != nil {
		fmt.Println(err)
	}
	calls := ExtractCallsOfTransaction(res)
	addresses := ProcessTraces(calls)
	return addresses
}