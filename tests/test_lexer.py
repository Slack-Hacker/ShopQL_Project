"""
Tests for ShopQL Lexer
"""

import unittest
from shopql.lexer import Lexer
from shopql.tokens import TokenType
from shopql.errors import LexerError


class TestLexer(unittest.TestCase):
    def test_keywords(self):
        query = "FIND PRODUCTS WHERE PRICE < 2000 AND CATEGORY = 'ELECTRONICS' ORDER BY PRICE ASC LIMIT 5;"
        tokens = Lexer(query).tokenize()
        expected_types = [
            TokenType.FIND, TokenType.PRODUCTS, TokenType.WHERE,
            TokenType.PRICE, TokenType.LESS_THAN, TokenType.NUMBER,
            TokenType.AND, TokenType.CATEGORY, TokenType.EQUALS,
            TokenType.STRING, TokenType.ORDER, TokenType.BY,
            TokenType.PRICE, TokenType.ASC, TokenType.LIMIT,
            TokenType.NUMBER, TokenType.SEMICOLON, TokenType.EOF
        ]
        self.assertEqual([t.type for t in tokens], expected_types)

    def test_case_insensitivity_of_keywords(self):
        query = "find products where price < 1000;"
        tokens = Lexer(query).tokenize()
        self.assertEqual(tokens[0].type, TokenType.FIND)
        self.assertEqual(tokens[1].type, TokenType.PRODUCTS)
        self.assertEqual(tokens[2].type, TokenType.WHERE)

    def test_numbers_int_and_float(self):
        tokens = Lexer("123 45.67 0.99 55000").tokenize()
        self.assertEqual(tokens[0].value, 123)
        self.assertEqual(tokens[1].value, 45.67)
        self.assertEqual(tokens[2].value, 0.99)
        self.assertEqual(tokens[3].value, 55000)

    def test_strings_with_quotes_and_escapes(self):
        tokens = Lexer('"Hello World" \'Single Quotes\' "Quote: \\"test\\""').tokenize()
        self.assertEqual(tokens[0].value, "Hello World")
        self.assertEqual(tokens[1].value, "Single Quotes")
        self.assertEqual(tokens[2].value, 'Quote: "test"')

    def test_relational_operators(self):
        tokens = Lexer("= != <> < <= > >= == CONTAINS LIKE BETWEEN IN").tokenize()
        types = [t.type for t in tokens if t.type != TokenType.EOF]
        self.assertEqual(types, [
            TokenType.EQUALS, TokenType.NOT_EQUALS, TokenType.NOT_EQUALS,
            TokenType.LESS_THAN, TokenType.LESS_EQUALS,
            TokenType.GREATER_THAN, TokenType.GREATER_EQUALS,
            TokenType.EQUALS,
            TokenType.CONTAINS, TokenType.LIKE, TokenType.BETWEEN, TokenType.IN
        ])

    def test_comments(self):
        query = """
        -- Single line comment
        FIND PRODUCTS // Another comment
        /* Multi
           line
           comment */
        WHERE PRICE < 50;
        """
        tokens = Lexer(query).tokenize()
        types = [t.type for t in tokens if t.type != TokenType.EOF]
        self.assertEqual(types, [
            TokenType.FIND, TokenType.PRODUCTS, TokenType.WHERE,
            TokenType.PRICE, TokenType.LESS_THAN, TokenType.NUMBER, TokenType.SEMICOLON
        ])

    def test_unterminated_string_error(self):
        with self.assertRaises(LexerError) as ctx:
            Lexer('FIND PRODUCTS WHERE CATEGORY = "ELECTRONICS').tokenize()
        self.assertIn("Unterminated string literal", str(ctx.exception))

    def test_line_and_column_tracking(self):
        query = "FIND\n  PRODUCTS;"
        tokens = Lexer(query).tokenize()
        self.assertEqual(tokens[0].line, 1)
        self.assertEqual(tokens[0].column, 1)
        self.assertEqual(tokens[1].line, 2)
        self.assertEqual(tokens[1].column, 3)


if __name__ == "__main__":
    unittest.main()

