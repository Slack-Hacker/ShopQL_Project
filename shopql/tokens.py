"""
ShopQL Token Definitions
Defines token types and representation for lexical analysis.
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import Any, Optional


class TokenType(Enum):
    # End of Input
    EOF = auto()

    # Literals
    IDENTIFIER = auto()     # Column names, table names, general identifiers
    STRING = auto()         # "Laptop", "ELECTRONICS"
    NUMBER = auto()         # 2000, 4.5, 55000
    BOOLEAN = auto()        # TRUE, FALSE

    # Keywords - Commands
    FIND = auto()           # FIND
    SHOW = auto()           # SHOW
    PRODUCTS = auto()       # PRODUCTS
    PRODUCT = auto()        # PRODUCT
    ADD = auto()            # ADD
    UPDATE = auto()         # UPDATE
    DELETE = auto()         # DELETE
    RESTOCK = auto()        # RESTOCK
    BUY = auto()            # BUY
    PURCHASE = auto()       # PURCHASE
    COUNT = auto()          # COUNT
    DESCRIBE = auto()       # DESCRIBE
    SCHEMA = auto()         # SCHEMA

    # Keywords - Clauses & Modifiers
    WHERE = auto()          # WHERE
    SET = auto()            # SET
    ORDER = auto()          # ORDER
    BY = auto()             # BY
    ASC = auto()            # ASC
    DESC = auto()           # DESC
    LIMIT = auto()          # LIMIT
    QUANTITY = auto()       # QUANTITY
    PRICE = auto()          # PRICE (keyword in ADD clause: ADD PRODUCT "x" PRICE 500)
    CATEGORY = auto()       # CATEGORY (keyword in ADD clause)
    STOCK = auto()          # STOCK
    RATING = auto()         # RATING

    # Logical Operators
    AND = auto()            # AND
    OR = auto()             # OR
    NOT = auto()            # NOT

    # Relational Operators
    EQUALS = auto()         # =
    NOT_EQUALS = auto()     # != or <>
    LESS_THAN = auto()      # <
    LESS_EQUALS = auto()    # <=
    GREATER_THAN = auto()   # >
    GREATER_EQUALS = auto() # >=
    CONTAINS = auto()       # CONTAINS (substring matching)
    LIKE = auto()           # LIKE (pattern matching)
    IN = auto()             # IN (membership)
    BETWEEN = auto()        # BETWEEN

    # Punctuation
    SEMICOLON = auto()      # ;
    COMMA = auto()          # ,
    LPAREN = auto()         # (
    RPAREN = auto()         # )


# Keyword mapping (case-insensitive)
KEYWORDS = {
    "FIND": TokenType.FIND,
    "SHOW": TokenType.SHOW,
    "PRODUCTS": TokenType.PRODUCTS,
    "PRODUCT": TokenType.PRODUCT,
    "ADD": TokenType.ADD,
    "UPDATE": TokenType.UPDATE,
    "DELETE": TokenType.DELETE,
    "RESTOCK": TokenType.RESTOCK,
    "BUY": TokenType.BUY,
    "PURCHASE": TokenType.PURCHASE,
    "COUNT": TokenType.COUNT,
    "DESCRIBE": TokenType.DESCRIBE,
    "SCHEMA": TokenType.SCHEMA,
    "WHERE": TokenType.WHERE,
    "SET": TokenType.SET,
    "ORDER": TokenType.ORDER,
    "BY": TokenType.BY,
    "ASC": TokenType.ASC,
    "DESC": TokenType.DESC,
    "LIMIT": TokenType.LIMIT,
    "QUANTITY": TokenType.QUANTITY,
    "PRICE": TokenType.PRICE,
    "CATEGORY": TokenType.CATEGORY,
    "STOCK": TokenType.STOCK,
    "RATING": TokenType.RATING,
    "AND": TokenType.AND,
    "OR": TokenType.OR,
    "NOT": TokenType.NOT,
    "CONTAINS": TokenType.CONTAINS,
    "LIKE": TokenType.LIKE,
    "IN": TokenType.IN,
    "BETWEEN": TokenType.BETWEEN,
    "TRUE": TokenType.BOOLEAN,
    "FALSE": TokenType.BOOLEAN,
}


@dataclass
class Token:
    type: TokenType
    value: Any
    line: int
    column: int
    lexeme: str = ""

    def __repr__(self) -> str:
        return f"Token({self.type.name}, {repr(self.value)}, L{self.line}:C{self.column})"

    def to_dict(self) -> dict:
        return {
            "type": self.type.name,
            "value": self.value,
            "lexeme": self.lexeme or str(self.value),
            "line": self.line,
            "column": self.column,
        }

