from typing import Optional, Any
import dataclasses

class ContextManager:
    _instance: Optional['ContextManager'] = None

    def __new__(cls, *args, **kwargs) -> 'ContextManager':
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self) -> None:
        self._storage = dict() 
        self._current_asic = dict()

    def fill_current_asic(self, user_id: int, **kwargs: Any) -> None:
        if user_id not in self._current_asic:
            self._current_asic[user_id] = {}
        self._current_asic[user_id].update(kwargs)

    def append(self, user_id: int):
        if user_id not in self._storage:
            self._storage[user_id] = []
        self._storage[user_id].append(self._current_asic[user_id])
        self._current_asic[user_id] = {}

    def clear(self, user_id: int):
        self._storage[user_id] = []
        self._current_asic[user_id] = {}