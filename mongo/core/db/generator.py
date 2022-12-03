import string
import random

from typing import List


class MongoDBGenerator:
    def __init__(self):
        self.__global_cache = {}

    def _random_float(self,
                      range_from: int,
                      range_to: int) -> float:
        return range_from + (random.random() * (range_to - range_from))

    def _random_scalar(self,
                       instance: str,
                       range_from: int = 0,
                       range_to: int = 1,
                       **kwargs):
        if instance == "list":
            string_values = []
            count_from, count_to = kwargs.get('count_from', 0), kwargs.get('count_to', 0)
            for _ in range((count_to - count_from) + 1):
                float_value = self._random_float(range_from, range_to)
                string_value = ''.join(
                    random.choice(string.ascii_uppercase + string.digits) for _ in range(round(float_value)))
                string_values.append(string_value)
            return string_values
        value = self._random_float(range_from, range_to)
        if instance == "str":
            return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(round(value)))
        if instance == "int":
            return round(value)
        return value

    def _random_primitive(self,
                          record_name: str,
                          primitive_name: str,
                          cache: bool = False,
                          cache_probability: float = 0,
                          **kwargs):
        primitive_random = self._random_scalar(**kwargs)
        if cache:
            primitives_cache_key = f"{record_name}:{primitive_name}"
            primitives_cache_value = self.__global_cache.get(primitives_cache_key)
            is_cache_active = primitives_cache_value is not None and len(primitives_cache_value) > 0
            if not is_cache_active:
                self.__global_cache[primitives_cache_key] = [primitive_random]
            else:
                if random.random() <= cache_probability:
                    primitive_cache = primitives_cache_value[round(random.random() * (len(primitives_cache_value) - 1))]
                    return primitive_cache
                else:
                    self.__global_cache[primitives_cache_key].append(primitive_random)
        return primitive_random

    def _random_records(self,
                        name: str,
                        properties: List[dict],
                        min_items: int = 0,
                        max_items: int = 0,
                        **kwargs):
        records = []
        items = round(self._random_float(min_items, max_items))
        for _ in range(items):
            record = {}
            for property in properties:
                record_name = property.get('name')
                record_properties = property.get('properties')
                is_primitive = record_properties is None
                if is_primitive:
                    record[record_name] = self._random_primitive(
                        record_name=name,
                        primitive_name=record_name,
                        **property
                    )
                else:
                    record[record_name] = self._random_records(**property)
            records.append(record)
        return records

    def random(self, schema: dict) -> any:
        records = self._random_records(
            min_items=1,
            max_items=1,
            **schema
        )
        self.__global_cache = {}
        return records

    def __repr__(self):
        return f"Neo4j generator"
