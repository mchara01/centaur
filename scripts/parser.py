import argparse

from result_parsing.conkas import Conkas
from result_parsing.honeybadger import Honeybadger
from result_parsing.maian import Maian
from result_parsing.mythril import Mythril
from result_parsing.osiris import Osiris
from result_parsing.oyente import Oyente
from result_parsing.securify import Securify
from result_parsing.vandal import Vandal
from tools import TOOLS


def parse_results(tool_name, tool_directory):
    if tool_name == "conkas":
        Conkas(tool_directory).parse()
    elif tool_name == "honeybadger":
        Honeybadger(tool_directory).parse()
    elif tool_name == "maian":
        Maian(tool_directory).parse()
    elif tool_name == "mythril":
        Mythril(tool_directory).parse()
    elif tool_name == "osiris":
        Osiris(tool_directory).parse()
    elif tool_name == "oyente":
        Oyente(tool_directory).parse()
    elif tool_name == "securify":
        Securify(tool_directory).parse()
    elif tool_name == "vandal":
        Vandal(tool_directory).parse()


def get_args():
    # Argument parsing
    args = argparse.ArgumentParser(
        prog="result_parser",
        description="Parse the results of the analysis tools and print their findings"
    )
    args.add_argument('-t',
                      '--tool',
                      choices=TOOLS,
                      help="Choice of tool to parse its results.")
    args.add_argument('-d',
                      "--directory",
                      help="Location where the result.json files reside.")
    return args.parse_args()


def main():
    args = get_args()
    tool = args.tool
    directory = args.directory
    parse_results(tool, directory)


if __name__ == "__main__":
    main()
