import httpx
from bs4 import BeautifulSoup
from datetime import timedelta
from dataclasses import dataclass, field
from typing import Dict

@dataclass
class Stats:
    data: Dict[str, Dict[str, timedelta]] = field(default_factory=dict)

def convert_to_timedelta(time_str) -> timedelta:
    parts = time_str.split()
    time_dict = {
        'm': next((int(part[:-1]) for part in parts if part.endswith('m')), 0),
        's': next((int(part[:-1]) for part in parts if part.endswith('s')), 0)
    }
    return timedelta(minutes=time_dict['m'], seconds=time_dict['s'])

async def get_stats():
    crypto_map = {
        'btc': 'coin c_btc',
        'eth': 'coin c_eth',
        'xrp': 'coin c_xrp',
        'ltc': 'coin c_ltc',
        'bch': 'coin c_bch',
        'doge': 'coin c_doge',
        'xmr': 'coin c_xmr',
        'bsv': 'coin c_bsv',
        'dash': 'coin c_dash',
        'zec': 'coin c_zec',
        'etc': 'coin c_etc',
        'btg': 'coin c_btg',
        'vtc': 'coin c_vtc'
    }

    rows_map = {
        't_total': 'Total',
        't_price': 'Price',
        't_cap': 'Market Cap',
        't_time': 'Block Time',
        't_blocks': 'Blocks',
        't_blocks24': 'Blocks 24h',
        't_blocksPerH': 'Blocks per Hour',
        't_diff': 'Difficulty',
        't_hash': 'Hashrate'
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get("https://bitinfocharts.com/")
        soup = BeautifulSoup(response.text, "lxml")

        stats = Stats()
        
        for row_id, row_name in rows_map.items():
            row = soup.find('tr', attrs={'id': row_id})
            if row:
                for crypto, class_name in crypto_map.items():
                    cell = row.find_all('td')[list(crypto_map.keys()).index(crypto) + 1]
                    #time_value = convert_to_timedelta(cell.text)
                    if crypto not in stats.data:
                        stats.data[crypto] = {}
                    stats.data[crypto][row_name] = cell.text
        
        print(stats)

if __name__ == "__main__":
    import asyncio
    asyncio.run(get_stats())
