

from typing import Optional
import dataclasses


@dataclasses.dataclass 
class SelectedAsic:
    manufacturer: str
    model: str
    ths: int
    algorithm: str
    coin: str


class ContextManager:
    _instance: Optional['ContextManager'] = None

    def __new__(cls, *args, **kwargs) -> 'ContextManager':
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self) -> None:
        self._storage = dict() 

    def add_asic(self,*, user_id: int):
        if self._storage.get(user_id) is None:
            self._storage[user_id] = list()
        self._storage