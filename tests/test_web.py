"""
Tests for ShopQL Web Studio API Endpoints
"""

import unittest
import json
from web_app import app, db


class TestWebApp(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        db.reset_to_seed()

    def test_index_route(self):
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"ShopQL", resp.data)

    def test_get_catalog(self):
        resp = self.client.get("/api/catalog")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn("products", data)
        self.assertGreater(len(data["products"]), 0)

    def test_get_samples(self):
        resp = self.client.get("/api/samples")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)

    def test_query_endpoint_example1(self):
        query = 'FIND PRODUCTS WHERE PRICE < 2000 AND CATEGORY = "ELECTRONICS";'
        resp = self.client.post("/api/query", data=json.dumps({"query": query}), content_type="application/json")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data["success"])
        self.assertIn("ast", data)
        self.assertIn("tokens", data)
        self.assertIn("results", data)
        self.assertGreater(len(data["results"][0]["rows"]), 0)

    def test_query_endpoint_error_handling(self):
        query = 'FIND PRODUCTS WHERE UNKNOWN_COL < 100;'
        resp = self.client.post("/api/query", data=json.dumps({"query": query}), content_type="application/json")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertFalse(data["success"])
        self.assertIn("Unknown column or attribute", data["error"])

    def test_reset_catalog_endpoint(self):
        resp = self.client.post("/api/reset")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data["success"])


if __name__ == "__main__":
    unittest.main()

