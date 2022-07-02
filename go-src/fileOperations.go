package main

import (
	"bufio"
	"os"
	"strconv" // converting strings
)

// ReadFileLines reads every line of a given file, creates an array of them and returns it.
func ReadFileLines(path string) ([]int64, error) {
	file, err := os.Open(path)
	check(err)
	defer func(file *os.File) {
		err := file.Close()
		if err != nil {

		}
	}(file)

	var lines []int64
	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		value, _ := strconv.ParseInt(scanner.Text(), 10, 64)
		if value == 0 { // Skip empty lines
			continue
		}
		lines = append(lines, value)
	}
	return lines, scanner.Err()
}
