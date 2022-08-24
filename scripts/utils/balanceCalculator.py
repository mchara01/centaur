import asyncio
import json

import aiohttp
import aiosqlite
from eth_utils import from_wei


async def balance_finder():
    total_balance_eth = 0
    total_balance_bsc = 0
    async with aiosqlite.connect("../../database/analysis.db") as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""SELECT DISTINCT a.address_id, a.balance
                                FROM Address AS a
                                JOIN Result R on a.address_id = R.address_id
                                JOIN Finding F on R.result_id = F.result_id
                                WHERE a.chain='eth';""") as cursor:
            async for row in cursor:
                total_balance_eth += int(row['balance'])
        print("Ethereum balance in wei: " + str(total_balance_eth))
        total_balance_eth = from_wei(total_balance_eth, 'ether')
        print("Ethereum balance in ether: " + str(total_balance_eth))
        async with aiohttp.ClientSession() as session:
            async with session.get('https://min-api.cryptocompare.com/data/price?fsym=ETH&tsyms=USD') as resp:
                result = json.loads(await resp.text())
                print("Ethereum balance in USD: " + str(float(total_balance_eth) * result["USD"]))

        async with db.execute("""SELECT DISTINCT A.address_id, A.balance
                                FROM Address AS A
                                JOIN Result R on A.address_id = R.address_id
                                JOIN Finding F on R.result_id = F.result_id
                                WHERE A.chain='bsc';""") as cursor:
            async for row in cursor:
                total_balance_bsc += int(row['balance'])
        print("BSC balance in jager: " + str(total_balance_bsc))
        total_balance_bsc = from_wei(total_balance_bsc, 'ether')
        print("BSC balance in BNB: " + str(total_balance_bsc))
        async with aiohttp.ClientSession() as session:
            async with session.get('https://min-api.cryptocompare.com/data/price?fsym=BNB&tsyms=USD') as resp:
                result = json.loads(await resp.text())
                print("BSC balance in USD: " + str(float(total_balance_bsc) * result["USD"]))


async def main():
    await balance_finder()


if __name__ == '__main__':
    cur_loop = asyncio.get_event_loop()
    cur_loop.run_until_complete(main())
    cur_loop.close()
