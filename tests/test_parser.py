"""
Tests for ShopQL Parser and AST Construction
"""

import unittest
from shopql.lexer import Lexer
from shopql.parser import Parser
from shopql.ast_nodes import (
    FindStatement, AddStatement, BinaryOp, Identifier, Literal, OrderByClause, BetweenOp, InOp
)
from shopql.errors import SyntaxError


class TestParser(unittest.TestCase):
    def parse_one(self, query: str):
        tokens = Lexer(query).tokenize()
        return Parser(tokens, source=query).parse_single()

    def test_example_1_find_products(self):
        query = """
        FIND PRODUCTS
        WHERE PRICE < 2000
        AND CATEGORY = "ELECTRONICS";
        """
        stmt = self.parse_one(query)
        self.assertIsInstance(stmt, FindStatement)
        self.assertEqual(stmt.verb, "FIND")
        self.assertIsNotNone(stmt.where_clause)
        self.assertIsInstance(stmt.where_clause, BinaryOp)
        self.assertEqual(stmt.where_clause.op, "AND")

        # Left of AND: PRICE < 2000
        left = stmt.where_clause.left
        self.assertIsInstance(left, BinaryOp)
        self.assertEqual(left.op, "<")
        self.assertEqual(left.left.name, "PRICE")
        self.assertEqual(left.right.value, 2000)

        # Right of AND: CATEGORY = "ELECTRONICS"
        right = stmt.where_clause.right
        self.assertIsInstance(right, BinaryOp)
        self.assertEqual(right.op, "=")
        self.assertEqual(right.left.name, "CATEGORY")
        self.assertEqual(right.right.value, "ELECTRONICS")

    def test_example_2_show_products_order_by(self):
        query = """
        SHOW PRODUCTS
        WHERE RATING >= 4.5
        ORDER BY PRICE ASC;
        """
        stmt = self.parse_one(query)
        self.assertIsInstance(stmt, FindStatement)
        self.assertEqual(stmt.verb, "SHOW")
        self.assertIsNotNone(stmt.where_clause)
        self.assertEqual(stmt.where_clause.op, ">=")
        self.assertIsNotNone(stmt.order_by)
        self.assertEqual(stmt.order_by.sort_field, "PRICE")
        self.assertEqual(stmt.order_by.direction, "ASC")

    def test_example_3_add_product(self):
        query = 'ADD PRODUCT "Laptop" PRICE 55000;'
        stmt = self.parse_one(query)
        self.assertIsInstance(stmt, AddStatement)
        self.assertEqual(stmt.name, "Laptop")
        self.assertEqual(stmt.price, 55000.0)

    def test_operator_precedence_and_over_or(self):
        # A OR B AND C  should parse as  A OR (B AND C)
        query = "FIND PRODUCTS WHERE PRICE < 100 OR CATEGORY = 'BOOKS' AND RATING > 4.0;"
        stmt = self.parse_one(query)
        self.assertIsInstance(stmt.where_clause, BinaryOp)
        self.assertEqual(stmt.where_clause.op, "OR")
        self.assertIsInstance(stmt.where_clause.right, BinaryOp)
        self.assertEqual(stmt.where_clause.right.op, "AND")

    def test_parentheses_override_precedence(self):
        # (A OR B) AND C  should parse as  (A OR B) AND C
        query = "FIND PRODUCTS WHERE (PRICE < 100 OR CATEGORY = 'BOOKS') AND RATING > 4.0;"
        stmt = self.parse_one(query)
        self.assertIsInstance(stmt.where_clause, BinaryOp)
        self.assertEqual(stmt.where_clause.op, "AND")
        self.assertIsInstance(stmt.where_clause.left, BinaryOp)
        self.assertEqual(stmt.where_clause.left.op, "OR")

    def test_between_and_in_clauses(self):
        query = "FIND PRODUCTS WHERE PRICE BETWEEN 50 AND 500 AND CATEGORY IN ('BOOKS', 'HOME');"
        stmt = self.parse_one(query)
        self.assertEqual(stmt.where_clause.op, "AND")
        self.assertIsInstance(stmt.where_clause.left, BetweenOp)
        self.assertIsInstance(stmt.where_clause.right, InOp)
        self.assertEqual(len(stmt.where_clause.right.values), 2)

    def test_syntax_error_missing_products(self):
        with self.assertRaises(SyntaxError) as ctx:
            self.parse_one("FIND WHERE PRICE < 100;")
        self.assertIn("Expected 'PRODUCTS' after 'FIND'", str(ctx.exception))

    def test_syntax_error_misspelled_keyword_suggestion(self):
        # Misspelled command like FND instead of FIND
        with self.assertRaises(SyntaxError) as ctx:
            self.parse_one("FND PRODUCTS;")
        err_str = str(ctx.exception)
        self.assertIn("Did you mean command 'FIND'?", err_str)


if __name__ == "__main__":
    unittest.main()
