"""
Tests for ShopQL Error Reporting & Visual Diagnostics
"""

import unittest
from shopql.engine import ShopQLEngine
from shopql.errors import format_error_snippet


class TestErrorReporting(unittest.TestCase):
    def setUp(self):
        self.engine = ShopQLEngine()

    def test_caret_pointer_formatting(self):
        source = "FIND PRODUCTS\nWHERE PRIC < 2000;"
        snippet = format_error_snippet(source, line=2, column=7, message="Unknown attribute 'PRIC'", suggestion="Did you mean 'PRICE'?")
        self.assertIn("ShopQL Error [Line 2, Column 7]:", snippet)
        self.assertIn("WHERE PRIC < 2000;", snippet)
        self.assertIn("^", snippet)
        self.assertIn("Unknown attribute 'PRIC'", snippet)
        self.assertIn("Did you mean 'PRICE'?", snippet)

    def test_syntax_error_caret_in_engine(self):
        query = "SHOW PRODUCTS WHERE RATING =="
        res = self.engine.execute(query)
        self.assertFalse(res.success)
        self.assertIn("ShopQL Error", res.error)
        self.assertIn("^", res.error)

    def test_unexpected_token_error(self):
        query = "ORDER PRODUCTS BY PRICE;"
        res = self.engine.execute(query)
        self.assertFalse(res.success)
        self.assertIn("Unexpected token 'ORDER'", res.error)


if __name__ == "__main__":
    unittest.main()

