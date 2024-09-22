from typing import Optional, Any
import dataclasses

class ContextManager:
    _instance: Optional['ContextManager'] = None

    def __new__(cls, *args, **kwargs) -> 'ContextManager':
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self) -> None:
        self.storage = dict()
        self.current_asic = dict()
        self.previous_asic = dict()

    def fill_current_asic(self, user_id: int, **kwargs: Any) -> None:
        if user_id not in self.current_asic:
            self.current_asic[user_id] = {}
        self.current_asic[user_id].update(kwargs)

    def append(self, user_id: int):
        if user_id not in self.storage:
            self.storage[user_id] = []
            
        status = False
        for asic in self.storage[user_id]:
            if asic['algorithm'] == self.current_asic[user_id]['algorithm'] and \
            asic['coin'] == self.current_asic[user_id]['coin'] and \
            asic['manufacturer'] == self.current_asic[user_id]['manufacturer'] and \
            asic['model'] == self.current_asic[user_id]['model'] and \
            asic['ths'] == self.current_asic[user_id]['ths']:
                asic['number'] = int(asic['number'])
                asic['number'] += int(self.current_asic[user_id]['number'])
                status = True

        if not status:
            self.storage[user_id].append(self.current_asic[user_id])
        self.previous_asic[user_id] = self.current_asic[user_id].copy()
        self.current_asic[user_id] = {}

    def clear(self, user_id: int):
        self.storage[user_id] = []
        self.current_asic[user_id] = {}
        self.previous_asic[user_id] = {}