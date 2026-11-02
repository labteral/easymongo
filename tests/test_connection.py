import os
from unittest import TestCase, skipUnless
from unittest.mock import Mock, patch
from uuid import uuid4

from easymongo import MongoDB


class ConnectionTest(TestCase):
    @skipUnless(os.environ.get('EASYMONGO_TEST_HOST'), 'isolated Mongo required')
    def test_real_reopen_and_materialized_cursor(self):
        from pymongo import MongoClient
        host = os.environ['EASYMONGO_TEST_HOST']
        name = 'easymongo_test_' + uuid4().hex
        observer = MongoClient(host, 27017)
        self.addCleanup(observer.close)
        self.addCleanup(observer.drop_database, name)
        db = MongoDB(host=host, port=27017, default_database=name,
                     default_collection='items')
        self.addCleanup(db.close_connection)
        db.insert({'value': 1})
        self.assertEqual(db.count(), 1)
        db.close_connection()
        self.assertEqual(db.count(), 1)
        documents = db.get_and_close()
        self.assertIsNone(db.client)
        self.assertEqual(next(documents)['value'], 1)

    def test_reopen_constructs_a_new_client(self):
        clients = [Mock(), Mock()]
        with patch("easymongo.easymongo.MongoClient", side_effect=clients):
            db = MongoDB(host="localhost", port=27017)
            db.open_connection()
            db.close_connection()
            clients[0].close.assert_called_once()
            db.open_connection()
            self.assertIs(db.client, clients[1])

    def test_failed_connect_retries_and_closes_rejected_clients(self):
        failed, healthy = Mock(), Mock()
        failed.server_info.side_effect = OSError("unavailable")
        with patch(
            "easymongo.easymongo.MongoClient", side_effect=[failed, healthy]
        ), patch("time.sleep"):
            db = MongoDB(host="localhost", port=27017)
            db.open_connection(attempts=1)
        failed.close.assert_called_once()
        self.assertIs(db.client, healthy)

    def test_get_and_close_materializes_before_closing(self):
        db = MongoDB(host="localhost", port=27017)
        client = Mock()
        db._client = client

        def cursor():
            client.close.assert_not_called()
            yield {"value": 1}

        with patch.object(db, "get", return_value=cursor()):
            results = db.get_and_close()
        client.close.assert_called_once()
        self.assertEqual(list(results), [{"value": 1}])
        self.assertIsNone(db.client)
