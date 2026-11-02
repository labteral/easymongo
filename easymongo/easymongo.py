#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pymongo import MongoClient, timeout
from .errors import ConnectionError
import time


class MongoDB:
    def __init__(
        self,
        host: str = None,
        port=None,
        default_database: str = None,
        default_collection: str = None,
        connect: bool = False,
        endpoint: str = None,
    ):

        if endpoint is not None:
            host, port = endpoint.split(":")
        self._config = {"host": host, "port": int(port)}

        if default_database != None:
            self._default_database = default_database

        if default_collection != None:
            self._default_collection = default_collection

        self._client = None
        self._health_client = None
        if connect:
            self.open_connection()

    @property
    def client(self):
        return self._client

    def _get_collection(self, database_name: str, collection_name: str):
        self.open_connection()
        database_name, collection_name = (
            self._get_database_and_collection_names(
                database_name, collection_name
            )
        )
        database = getattr(self._client, database_name)
        collection = getattr(database, collection_name)
        return collection

    def set_defaults(
        self, database_name: str, database_collection: str = None
    ):
        self._default_database = database_name
        if database_collection != None:
            self._default_collection = database_collection

    def open_connection(self, attempts: int = 10):
        if self._client is not None:
            return
        for attempt in range(attempts + 1):
            client = MongoClient(**self._config)
            try:
                client.server_info()
            except Exception as error:
                client.close()
                if attempt == attempts:
                    raise ConnectionError from error
                time.sleep(1)
            else:
                self._client = client
                return

    def close_connection(self):
        client, self._client = self._client, None
        if client is not None:
            client.close()
        health_client, self._health_client = self._health_client, None
        if health_client is not None:
            health_client.close()

    def health(self):
        """Use the same URI/credentials without entering application retries."""
        try:
            with timeout(0.5):
                client = self._client
                if client is None:
                    if self._health_client is None:
                        self._health_client = MongoClient(**self._config, serverSelectionTimeoutMS=500,
                                                         connectTimeoutMS=500, socketTimeoutMS=500)
                    client = self._health_client
                client.admin.command('ping')
            return True
        except Exception:
            return False

    def _get_database_and_collection_names(
        self,
        database_name: str,
        collection_name: str,
    ):
        if not database_name and hasattr(self, "_default_database"):
            database_name = self._default_database
        if not collection_name and hasattr(self, "_default_collection"):
            collection_name = self._default_collection
        return database_name, collection_name

    def get_and_close(
        self,
        query=None,
        database_name: str = None,
        collection_name: str = None,
    ):
        try:
            return iter(list(self.get(query, database_name, collection_name)))
        finally:
            self.close_connection()

    def exists(self, query, database_name=None, collection_name=None):
        collection = self._get_collection(database_name, collection_name)
        if not collection.find_one(query):
            return False
        return True

    def create_index(
        self,
        attribute: str = None,
        keys=None,
        database_name: str = None,
        collection_name: str = None,
        unique: bool = False,
        type_: str = None,
        background: bool = True,
    ):
        if type_ is None:
            type_ = "asc"
        if not keys and not attribute:
            raise TypeError
        if not keys:
            if type_ == "desc":
                type_ = -1
            else:
                type_ = 1
            keys = [(attribute, type_)]
        collection = self._get_collection(database_name, collection_name)
        collection.create_index(keys, unique=unique, background=background)

    def get(
        self,
        query=None,
        database_name: str = None,
        collection_name: str = None,
        sort: str = None,
        sort_attribute: str = None,
        sort_type: str = None,
        limit: int = None,
        index=None,
        index_attribute: str = None,
        index_type: str = None,
    ):
        collection = self._get_collection(database_name, collection_name)
        if sort_attribute and sort_type:
            if sort_type == "desc":
                sort_type = -1
            else:
                sort_type = 1
            sort = [(sort_attribute, sort_type)]
        if limit == 1:
            result = collection.find_one(query, sort=sort)
            if result:
                return iter([result])
            return iter([])
        result = collection.find(query, sort=sort)
        if index or (index_attribute and index_type):
            if index:
                result = result.hint(index)
            else:
                if index_type == "desc":
                    index_type = -1
                else:
                    index_type = 1
                result = result.hint([(index_attribute, index_type)])
        if limit:
            result = result.limit(limit)
        return result

    def get_random(
        self,
        query=None,
        database_name: str = None,
        collection_name: str = None,
        sort=None,
        sort_attribute: str = None,
        sort_type: str = None,
        limit: int = None,
    ):
        if limit is None:
            limit = 1
        collection = self._get_collection(database_name, collection_name)
        if sort_attribute and sort_type:
            if sort_type == "desc":
                sort_type = -1
            else:
                sort_type = 1
            sort = [(sort_attribute, sort_type)]
        operation = [{"$sample": {"size": limit}}]
        if query:
            operation = [{"$match": query}] + operation
        if sort:
            operation = operation + [{"$sort": sort}]
        result = collection.aggregate(operation)
        return result

    def update(
        self,
        query,
        value,
        database_name: str = None,
        collection_name: str = None,
    ):
        collection = self._get_collection(database_name, collection_name)
        collection.update_one(query, {"$set": value}, upsert=True)

    def push(
        self,
        query,
        key: str,
        value,
        database_name: str = None,
        collection_name: str = None,
    ):
        collection = self._get_collection(database_name, collection_name)
        collection.update_one(query, {"$push": {key: {"$each": value}}})

    def put(
        self,
        value,
        query=None,
        database_name: str = None,
        collection_name: str = None,
    ):
        if query:
            self.update(query, value, database_name, collection_name)
        else:
            self.insert(value, database_name, collection_name)

    def remove(
        self,
        query=None,
        database_name: str = None,
        collection_name: str = None,
    ):
        collection = self._get_collection(database_name, collection_name)
        collection.delete_many({} if query is None else query)

    def insert(
        self, value, database_name: str = None, collection_name: str = None
    ):
        collection = self._get_collection(database_name, collection_name)
        collection.insert_one(dict(value))

    def count(
        self,
        query=None,
        database_name: str = None,
        collection_name: str = None,
    ):
        collection = self._get_collection(database_name, collection_name)
        if not query:
            query = {}
        return collection.count_documents(filter=query)


# Backwards compatible
MongodbConnector = MongoDB
