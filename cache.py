import os
import aioredis
import pickle
from dotenv import load_dotenv

load_dotenv()

class RedisClient:
    def __init__(self):
        self.redis = aioredis.from_url(os.getenv("REDIS_URL"))

    async def update_values(self, key, values):
        await self.redis.set(key, df_pickle)

    async def load_dataframe(self, market=Markets, endpoint=Endpoints, trading_date=date) -> pd.DataFrame:
        key = f'{market.value}_{endpoint.value}_{trading_date.strftime("%Y-%m-%d")}'
        df_pickle = await self.redis.get(key)
        if df_pickle is None:
            return None
        df = pickle.loads(df_pickle)
        return df
    
    async def add_missing_days(self, market: Markets, endpoint: Endpoints, missing_date: date) -> bool:
        key = 'missed_days'
        try:
            missed_days = await self.redis.get(key)
            if missed_days is None:
                missed_days = {}
            else:
                missed_days = pickle.loads(missed_days)
            
            market_key = market.value
            endpoint_key = endpoint.value
            
            if market_key not in missed_days:
                missed_days[market_key] = {}
            
            if endpoint_key not in missed_days[market_key]:
                missed_days[market_key][endpoint_key] = []

            if missing_date not in missed_days[market_key][endpoint_key]:
                missed_days[market_key][endpoint_key].append(missing_date)

            missed_days_pickle = pickle.dumps(missed_days)
            await self.redis.set(key, missed_days_pickle)
            return True
        except Exception as e:
            print(f"Error adding missing day: {e}")
            return False

    async def get_missing_days(self) -> dict:
        key = 'missed_days'
        missed_days_pickle = await self.redis.get(key)
        if missed_days_pickle is None:
            return {}
        missed_days = pickle.loads(missed_days_pickle)
        return missed_days

    async def clear_all(self):
        keys = await self.redis.keys('*')
        if keys:
            await self.redis.delete(*keys)


if __name__ == "__main__":
    redis = RedisClient()
    import asyncio
    #asyncio.run(redis.add_missing_days(market=Markets.SHARES, endpoint=Endpoints.TRADESTATS, missing_date=date(2024, 6, 30)))
    #print(asyncio.run(redis.get_missing_days()))
    # asyncio.run(redis.clear_all())
    print(asyncio.run(redis.get_missing_days()))