package main

import (
	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/common/hexutil"
)

type LogConfig struct {
	DisableMemory  bool // disable memory capture
	DisableStack   bool // disable stack capture
	DisableStorage bool // disable storage capture
	Debug          bool // print output during capture end
	Limit          int  // maximum length of output, but zero means unlimited
}

type TraceConfig struct {
	*LogConfig
	Tracer  string
	Timeout string
	Reexec  uint64
}

type TransactionCall struct {
	Type           string
	From           string
	To             string
	BytesSignature string
	//Input    string
	//Output   string
	//Gas      string
	//GasUsed  string
	Value string
	Error string
	Index string
}

type CallTracesOfTransaction struct {
	Type  string                    `json:"type"`
	From  common.Address            `json:"from"`
	To    common.Address            `json:"to"`
	Value *hexutil.Big              `json:"value,omitempty"`
	Error string                    `json:"error,omitempty"`
	Calls []CallTracesOfTransaction `json:"calls,omitempty"`
	Input hexutil.Bytes             `json:"input"`
	//Output  hexutil.Bytes             `json:"output"`
	//Gas     string                    `json:"gas,omitempty"`
	//GasUsed string                    `json:"gasUsed,omitempty"`
}
