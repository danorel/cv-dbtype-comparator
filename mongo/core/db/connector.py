from pymongo import MongoClient


class MongoDBConnection:
    def __init__(self, host, db):
        self.__uri = host
        self.__driver = None
        try:
            self.__driver = MongoClient(self.__uri)
            self.__db = self.__driver[db]
        except Exception as e:
            print("Failed to create the driver:", e)

    def close(self):
        if self.__driver is not None:
            self.__driver.close()

    def collection(self, collection_name: str):
        assert self.__driver is not None, "Driver not initialized!"
        assert self.__db is not None, "Database not initialized!"
        try:
            collection = self.__db.get_collection(collection_name)
            if collection is None:
                collection = self.__db.create_collection(collection_name, check_exists=False)
            return collection
        except Exception as e:
            print("Query failed:", e)
