"""
Tests for ShopQL Semantic Analysis and Type Checking
"""

import unittest
from shopql.lexer import Lexer
from shopql.parser import Parser
from shopql.semantic import SemanticAnalyzer
from shopql.errors import SemanticError


class TestSemantic(unittest.TestCase):
    def analyze_query(self, query: str):
        tokens = Lexer(query).tokenize()
        stmt = Parser(tokens, source=query).parse_single()
        SemanticAnalyzer(source=query).analyze(stmt)
        return stmt

    def test_valid_query(self):
        query = "FIND PRODUCTS WHERE PRICE < 2000 AND CATEGORY = 'ELECTRONICS' ORDER BY RATING DESC;"
        stmt = self.analyze_query(query)
        self.assertIsNotNone(stmt)

    def test_unknown_column_with_suggestion(self):
        query = "FIND PRODUCTS WHERE PRIC < 2000;"
        with self.assertRaises(SemanticError) as ctx:
            self.analyze_query(query)
        err = str(ctx.exception)
        self.assertIn("Unknown column or attribute 'PRIC'", err)
        self.assertIn("PRICE", err)

    def test_type_mismatch_numeric_and_string(self):
        query = "FIND PRODUCTS WHERE PRICE < 'cheap';"
        with self.assertRaises(SemanticError) as ctx:
            self.analyze_query(query)
        self.assertIn("Type mismatch in comparison", str(ctx.exception))

    def test_invalid_rating_range(self):
        query = 'ADD PRODUCT "Gadget" PRICE 100 RATING 8.5;'
        with self.assertRaises(SemanticError) as ctx:
            self.analyze_query(query)
        self.assertIn("RATING must be between 0.0 and 5.0", str(ctx.exception))

    def test_negative_price(self):
        query = 'ADD PRODUCT "Faulty" PRICE -50;'
        with self.assertRaises(SemanticError) as ctx:
            self.analyze_query(query)
        self.assertIn("PRICE must be positive", str(ctx.exception))

    def test_immutable_id_update(self):
        query = "UPDATE PRODUCTS SET ID = 99 WHERE NAME = 'Laptop';"
        with self.assertRaises(SemanticError) as ctx:
            self.analyze_query(query)
        self.assertIn("immutable", str(ctx.exception).lower())

    def test_contains_operator_type_check(self):
        # CONTAINS requires string
        query = "FIND PRODUCTS WHERE PRICE CONTAINS '100';"
        with self.assertRaises(SemanticError) as ctx:
            self.analyze_query(query)
        self.assertIn("requires a STRING attribute", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()

