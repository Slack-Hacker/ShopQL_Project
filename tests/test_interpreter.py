"""
Tests for ShopQL Interpreter & Query Execution
"""

import unittest
from shopql.engine import ShopQLEngine
from shopql.database import Database
from shopql.errors import ExecutionError


class TestInterpreter(unittest.TestCase):
    def setUp(self):
        # Fresh in-memory database for each test
        self.db = Database(persistence_file=None)
        self.engine = ShopQLEngine(db=self.db)

    def test_example_1_prompt_query(self):
        query = """
        FIND PRODUCTS
        WHERE PRICE < 2000
        AND CATEGORY = "ELECTRONICS";
        """
        res = self.engine.execute(query)
        self.assertTrue(res.success, f"Query failed: {res.error}")
        rows = res.results[0].rows
        self.assertGreater(len(rows), 0)
        for r in rows:
            self.assertLess(r["price"], 2000)
            self.assertEqual(r["category"], "ELECTRONICS")

    def test_example_2_show_products_order_by(self):
        query = """
        SHOW PRODUCTS
        WHERE RATING >= 4.5
        ORDER BY PRICE ASC;
        """
        res = self.engine.execute(query)
        self.assertTrue(res.success, f"Query failed: {res.error}")
        rows = res.results[0].rows
        self.assertGreater(len(rows), 0)
        # Verify rating condition
        for r in rows:
            self.assertGreaterEqual(r["rating"], 4.5)
        # Verify sorted ascending by price
        prices = [r["price"] for r in rows]
        self.assertEqual(prices, sorted(prices))

    def test_example_3_add_product(self):
        query = 'ADD PRODUCT "Laptop" PRICE 55000;'
        res = self.engine.execute(query)
        self.assertTrue(res.success, f"Query failed: {res.error}")
        
        # Verify it can now be queried
        search = self.engine.execute('FIND PRODUCTS WHERE NAME = "Laptop";')
        self.assertTrue(search.success)
        self.assertEqual(len(search.results[0].rows), 1)
        prod = search.results[0].rows[0]
        self.assertEqual(prod["name"], "Laptop")
        self.assertEqual(prod["price"], 55000.0)
        self.assertEqual(prod["category"], "GENERAL")

    def test_inventory_management_restock_and_purchase(self):
        # 1. Add item with stock 5
        self.engine.execute('ADD PRODUCT "Tablet Pro" PRICE 800 CATEGORY "ELECTRONICS" STOCK 5;')
        
        # 2. Purchase 2 units
        buy_res = self.engine.execute('BUY PRODUCT "Tablet Pro" QUANTITY 2;')
        self.assertTrue(buy_res.success)
        self.assertEqual(buy_res.results[0].rows[0]["stock"], 3)

        # 3. Restock 10 units
        restock_res = self.engine.execute('RESTOCK PRODUCT "Tablet Pro" QUANTITY 10;')
        self.assertTrue(restock_res.success)
        self.assertEqual(restock_res.results[0].rows[0]["stock"], 13)

        # 4. Attempt to purchase more than available stock (13)
        fail_res = self.engine.execute('BUY PRODUCT "Tablet Pro" QUANTITY 20;')
        self.assertFalse(fail_res.success)
        self.assertIn("Insufficient stock", fail_res.error)

    def test_text_search_contains_and_like(self):
        # CONTAINS
        res1 = self.engine.execute('FIND PRODUCTS WHERE NAME CONTAINS "MacBook";')
        self.assertTrue(res1.success)
        self.assertEqual(len(res1.results[0].rows), 1)
        self.assertEqual(res1.results[0].rows[0]["name"], "MacBook Pro 16")

        # LIKE
        res2 = self.engine.execute('FIND PRODUCTS WHERE CATEGORY LIKE "ELEC%";')
        self.assertTrue(res2.success)
        for r in res2.results[0].rows:
            self.assertEqual(r["category"], "ELECTRONICS")

    def test_update_product(self):
        self.engine.execute('UPDATE PRODUCT "Clean Code" SET PRICE = 29.99, STOCK = 80;')
        check = self.engine.execute('FIND PRODUCTS WHERE NAME = "Clean Code";')
        self.assertEqual(check.results[0].rows[0]["price"], 29.99)
        self.assertEqual(check.results[0].rows[0]["stock"], 80)

    def test_delete_product(self):
        self.engine.execute('DELETE PRODUCT "Precision Wireless Mouse";')
        check = self.engine.execute('FIND PRODUCTS WHERE NAME = "Precision Wireless Mouse";')
        self.assertEqual(len(check.results[0].rows), 0)

    def test_count_products(self):
        res = self.engine.execute('COUNT PRODUCTS WHERE CATEGORY = "BOOKS";')
        self.assertTrue(res.success)
        self.assertEqual(res.results[0].count, 2)


if __name__ == "__main__":
    unittest.main()

