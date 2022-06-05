package main

import (
	"os"
	"bufio"
    "strconv" // convertings strings

)

func readFileLines(path string) ([]int64, error) {
    file, err := os.Open(path)
    check(err)
    defer file.Close()

    var lines []int64
    scanner := bufio.NewScanner(file)
    for scanner.Scan() {
        value, _ := strconv.ParseInt(scanner.Text(), 10, 64)
        lines = append(lines, value)
    }
    return lines, scanner.Err()
}

func check(e error) {
    if e != nil {
        panic(e)
    }
}