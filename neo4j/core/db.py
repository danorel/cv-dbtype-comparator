import string
import random

from typing import List
from neo4j import GraphDatabase


def random_value(range_from: int = 0,
                 range_to: int = 1,
                 instance: str = "int",
                 **kwargs):
    if instance == "list":
        string_values = []
        count_from = kwargs.get('count_from', 0)
        count_to = kwargs.get('count_to', 0)
        for _ in range(count_from, count_to + 1):
            float_value = range_from + (random.random() * (range_to - range_from))
            string_value = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(round(float_value)))
            string_values.append(string_value)
        return string_values
    value = range_from + (random.random() * (range_to - range_from))
    if instance == "str":
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(round(value)))
    if instance == "int":
        return round(value)
    return value


class Neo4jGenerator:
    def __init__(self, N: int, cache_probability: float = .75):
        self.__N = N
        self.__cache_probability = cache_probability

    def random_data(self, properties: list) -> List[dict]:
        data = []
        cache = {}
        for _ in range(self.__N):
            record = {}
            for property in properties:
                name = property.get('name')
                value = random_value(**property)
                if property.get('cache'):
                    column_cache = cache.get(name)
                    active_cache = column_cache is not None and len(column_cache) > 0
                    if not active_cache:
                        record[name] = value
                        cache[name] = [value]
                    else:
                        if random.random() > self.__cache_probability:
                            column_cache_index = round(random.random() * (len(column_cache) - 1))
                            column_cache_value = column_cache[column_cache_index]
                            record[name] = column_cache_value
                        else:
                            record[name] = value
                            column_cache.append(value)
                else:
                    record[name] = value
            data.append(record)
        return data

    def __repr__(self):
        return f"Neo4j generator: {self.__N}"


class Neo4jConnection:
    def __init__(self, uri, user, pwd):
        self.__uri = uri
        self.__user = user
        self.__pwd = pwd
        self.__driver = None
        try:
            self.__driver = GraphDatabase.driver(self.__uri, auth=(self.__user, self.__pwd))
        except Exception as e:
            print("Failed to create the driver:", e)

    def close(self):
        if self.__driver is not None:
            self.__driver.close()

    def query(self, query, parameters=None, db=None):
        assert self.__driver is not None, "Driver not initialized!"
        session = None
        response = None
        try:
            session = self.__driver.session(database=db) if db is not None else self.__driver.session()
            response = list(session.run(query, parameters))
        except Exception as e:
            print("Query failed:", e)
        finally:
            if session is not None:
                session.close()
        return response
