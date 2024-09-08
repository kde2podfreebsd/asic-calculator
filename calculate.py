from bitinfo import get_stats
from gsheets import *

example = [{'algorithm': 'SHA-256', 'coin': 'BITCOIN', 'manufacturer': 'ANTMINER', 'model': 'S19jPro', 'ths': '117', 'number': '8'}, 0.051000000000000004]


async def calculate_income_for_asic_group(asic_group: dict, tariff: float) -> float:
    bitinfo_stats = await get_stats()
    total_ths = int(asic_group["ths"]) * int(asic_group["number"])
    ths_income = total_ths * bitinfo_stats[asic_group['coin'].upper()]

    asic_data = g.serialize()
    consumption = None
    for asic in asic_data:
        if asic.algorithm == asic_group['algorithm'] and \
                asic.coin == asic_group['coin'] and \
                asic.manufacturer == asic_group['manufacturer'] and \
                asic.model == asic_group['model'] and \
                asic.ths == asic_group['ths']:
            consumption = int(asic.consumption)

    if consumption is None:
        raise ValueError("ASIC data not found for the specified group")
    total_consumption_kwh = (consumption / 1000) * 24 * int(asic_group["number"])
    electricity_cost = total_consumption_kwh * tariff
    net_income = ths_income - electricity_cost

    return net_income

async def calculate_income(asics: list):
    incomes = dict()
    tariff = None

    for asic_group in asics:
        if isinstance(asic_group, float):
            tariff = asic_group

    tariff = round(tariff, 5)

    for asic_group in asics:
        if not isinstance(asic_group, float):
            incomes[f'{asic_group["algorithm"]}_{asic_group["coin"]}_{asic_group["manufacturer"]}_{asic_group["model"]}_{asic_group["ths"]}'] = await calculate_income_for_asic_group(asic_group=asic_group, tariff=tariff)

    return incomes

if __name__ == "__main__":
    import asyncio
    print(asyncio.run(calculate_income(example)))