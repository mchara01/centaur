package main

import (
	"os"
	"bufio"
)

func readFileLines(path string) ([]string, error) {
    file, err := os.Open(path)
    check(err)
    defer file.Close()

    var lines []string
    scanner := bufio.NewScanner(file)
    for scanner.Scan() {
        lines = append(lines, scanner.Text())
    }
    return lines, scanner.Err()
}

func check(e error) {
    if e != nil {
        panic(e)
    }
}