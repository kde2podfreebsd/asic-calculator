import httpx
from bs4 import BeautifulSoup
from datetime import timedelta
from dataclasses import dataclass, field
from typing import Dict, Union, Any


@dataclass
class Stats:
    data: Dict[str, Dict[str, timedelta]] = field(default_factory=dict)


crypto_map = [
    'btc', 'eth', 'xrp',
    'ltc', 'bch', 'doge',
    'xmr', 'bsv', 'dash',
    'zec', 'etc', 'btg', 'vtc'
    ]

crypto_full_names: dict[Union[str, Any], Union[str, Any]] = {
    'btc': 'Bitcoin',
    'eth': 'Ethereum',
    'xrp': 'Ripple',
    'ltc': 'Litecoin',
    'bch': 'Bitcoin Cash',
    'doge': 'Dogecoin',
    'xmr': 'Monero',
    'bsv': 'Bitcoin SV',
    'dash': 'Dash',
    'zec': 'Zcash',
    'etc': 'Ethereum Classic',
    'btg': 'Bitcoin Gold',
    'vtc': 'Vertcoin'
}

def convert_to_thash(price_data):
    conversion_factors = {
        'THash/s': 1,
        'GHash/s': 1e-3,
        'MHash/s': 1e-6,
        'KHash/s': 1e-9,
        'Hash/s': 1e-12
    }

    thash_prices = {}

    for coin, price in price_data.items():
        if price:
            parts = price.split(' ')
            value = float(parts[0])
            unit = parts[-1]

            if unit in conversion_factors:
                converted_value = value * conversion_factors[unit]
                thash_prices[coin] = float(f"{converted_value:.8f}")
            else:
                thash_prices[coin] = "Conversion not possible"

    return thash_prices


async def get_stats():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://bitinfocharts.com/")
        soup = BeautifulSoup(response.text, "lxml")

        t_emptys = soup.find_all('tr', attrs={'class': 't_empty'})
        res = dict()
        for idx, profit in enumerate(t_emptys[8].find_all('td')):
            if idx == 0:
                continue
            if idx == len(crypto_map):
                break
            res[crypto_full_names[crypto_map[idx-1]].upper()] = profit.text

        return convert_to_thash(price_data=res)


if __name__ == "__main__":
    import asyncio
    print(asyncio.run(get_stats()))
