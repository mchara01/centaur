import argparse
import asyncio
from pathlib import Path

import aiomysql


async def select(sql, pool):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(sql)
            response = await cur.fetchall()
            return response


async def file_writer(loop, chain):
    bytecodes = dict()
    avoid_duplicates = set()
    contracts = 0

    pool = await aiomysql.create_pool(
        user="root",
        password="Fm)4dj",
        host="127.0.0.1",
        port=3333,
        db="db_blockchain",
        loop=loop)

    sqlStmt = "SELECT address, bytecode FROM {} WHERE balance > 0 or nr_token_transfers > 0 or nr_transactions > 0;".format(
        chain)

    response = await select(sql=sqlStmt, pool=pool)

    # We store bytecodes in a set and check every new bytecode against the set to avoid duplicates
    for address in response:
        if address[1] not in avoid_duplicates:
            bytecodes[address[0]] = address[1]
            avoid_duplicates.add(address[1])
            contracts += 1

    # Store unique bytecodes to the file system
    for address in bytecodes:
        location = "data/dataset/" + chain + "/" + address + ".hex"
        output_file = Path(location)
        output_file.parent.mkdir(exist_ok=True, parents=True)
        output_file.write_text(bytecodes[address])

    print(f"Bytecodes written to the file system: {contracts}")


def get_args():
    # Argument parsing
    args = argparse.ArgumentParser(
        prog="file_writer",
        description="Write smart contracts' bytecode to files on the local filesystem."
    )
    args.add_argument("--chain", dest="chain", default="eth",
                      help="Choose chain from which the bytecodes will be extracted. Chain name matches db table name.")
    return args.parse_args()


def main():
    args = get_args()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(file_writer(loop, args.chain))
    loop.close()


if __name__ == "__main__":
    main()
