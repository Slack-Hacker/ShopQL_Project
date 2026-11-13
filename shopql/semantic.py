"""
ShopQL Semantic Analyzer
Performs type checking, attribute verification, and constraint validation on the AST.
"""

from typing import Dict, Any, Optional, Set
import difflib

from .ast_nodes import (
    Statement, FindStatement, CountStatement, AddStatement,
    UpdateStatement, DeleteStatement, RestockStatement, PurchaseStatement, DescribeStatement,
    Expression, Literal, Identifier, BinaryOp, UnaryOp, BetweenOp, InOp
)
from .errors import SemanticError


SCHEMA_TYPES = {
    "ID": "NUMBER",
    "NAME": "STRING",
    "PRICE": "NUMBER",
    "CATEGORY": "STRING",
    "STOCK": "NUMBER",
    "RATING": "NUMBER",
    "DESCRIPTION": "STRING",
}

VALID_COLUMNS = set(SCHEMA_TYPES.keys())


class SemanticAnalyzer:
    def __init__(self, source: str = ""):
        self.source = source

    def _error(self, message: str, node: Any, suggestion: Optional[str] = None) -> SemanticError:
        line = getattr(node, "line", 1)
        col = getattr(node, "column", 1)
        return SemanticError(message, line=line, column=col, source=self.source, suggestion=suggestion)

    def analyze(self, statement: Statement) -> None:
        if isinstance(statement, (FindStatement, CountStatement)):
            if statement.where_clause:
                self._check_expression(statement.where_clause)
            if isinstance(statement, FindStatement) and statement.order_by:
                col = statement.order_by.sort_field.upper()
                if col not in VALID_COLUMNS:
                    close = difflib.get_close_matches(col, list(VALID_COLUMNS), n=1, cutoff=0.6)
                    sug = f"Did you mean column '{close[0]}'?" if close else f"Valid columns: {', '.join(sorted(VALID_COLUMNS))}"
                    raise self._error(f"Cannot ORDER BY unknown column '{col}'", statement.order_by, sug)

        elif isinstance(statement, AddStatement):
            if statement.price < 0:
                raise self._error(f"PRICE must be positive, got {statement.price}", statement, "Set PRICE to a value >= 0.")
            if statement.stock < 0:
                raise self._error(f"STOCK cannot be negative, got {statement.stock}", statement, "Set STOCK to a value >= 0.")
            if not (0.0 <= statement.rating <= 5.0):
                raise self._error(f"RATING must be between 0.0 and 5.0, got {statement.rating}", statement, "Set RATING to a value from 0.0 to 5.0.")

        elif isinstance(statement, UpdateStatement):
            for field_name, expr in statement.assignments.items():
                fname = field_name.upper()
                if fname not in VALID_COLUMNS:
                    close = difflib.get_close_matches(fname, list(VALID_COLUMNS), n=1, cutoff=0.6)
                    sug = f"Did you mean '{close[0]}'?" if close else f"Valid columns: {', '.join(sorted(VALID_COLUMNS))}"
                    raise self._error(f"Cannot update unknown column '{fname}'", expr, sug)
                if fname == "ID":
                    raise self._error("Product 'ID' is immutable and cannot be updated", expr)
                expr_type = self._check_expression(expr)
                expected_type = SCHEMA_TYPES[fname]
                if expr_type and expr_type != expected_type:
                    raise self._error(f"Type mismatch for column '{fname}': expected {expected_type}, got {expr_type}", expr)

            if statement.where_clause:
                self._check_expression(statement.where_clause)

        elif isinstance(statement, DeleteStatement):
            if statement.where_clause:
                self._check_expression(statement.where_clause)

        elif isinstance(statement, RestockStatement):
            if statement.quantity <= 0:
                raise self._error(f"RESTOCK quantity must be greater than 0, got {statement.quantity}", statement, "Specify a positive restock quantity.")

        elif isinstance(statement, PurchaseStatement):
            if statement.quantity <= 0:
                raise self._error(f"Purchase quantity must be greater than 0, got {statement.quantity}", statement, "Specify a positive purchase quantity.")

        elif isinstance(statement, DescribeStatement):
            pass

    def _check_expression(self, expr: Expression) -> Optional[str]:
        """Validates expression and returns inferred type ('NUMBER', 'STRING', 'BOOLEAN', or None)."""
        if isinstance(expr, Literal):
            return expr.literal_type

        elif isinstance(expr, Identifier):
            name = expr.name.upper()
            if name not in VALID_COLUMNS:
                close = difflib.get_close_matches(name, list(VALID_COLUMNS), n=1, cutoff=0.6)
                sug = f"Did you mean column '{close[0]}'?" if close else f"Valid attributes: {', '.join(sorted(VALID_COLUMNS))}"
                raise self._error(f"Unknown column or attribute '{expr.name}'", expr, sug)
            return SCHEMA_TYPES[name]

        elif isinstance(expr, UnaryOp):
            if expr.op == "NOT":
                t = self._check_expression(expr.operand)
                if t and t != "BOOLEAN":
                    pass  # Python truthiness allows NOT on any expression, but logical NOT expects boolean
                return "BOOLEAN"

        elif isinstance(expr, BinaryOp):
            left_type = self._check_expression(expr.left)
            right_type = self._check_expression(expr.right)

            # Logical operators: AND, OR
            if expr.op in ("AND", "OR"):
                return "BOOLEAN"

            # String matching operators: CONTAINS, LIKE
            if expr.op in ("CONTAINS", "LIKE"):
                if left_type and left_type != "STRING":
                    raise self._error(f"Operator '{expr.op}' requires a STRING attribute, but left side has type {left_type}", expr)
                if right_type and right_type != "STRING":
                    raise self._error(f"Operator '{expr.op}' pattern must be a STRING literal, got {right_type}", expr)
                return "BOOLEAN"

            # Relational operators: =, !=, <, <=, >, >=
            if expr.op in ("=", "!=", "<", "<=", ">", ">="):
                if left_type and right_type and left_type != right_type:
                    raise self._error(
                        f"Type mismatch in comparison '{expr.op}': cannot compare {left_type} with {right_type}",
                        expr,
                        f"Ensure both sides of '{expr.op}' have matching types."
                    )
                return "BOOLEAN"

        elif isinstance(expr, BetweenOp):
            expr_type = self._check_expression(expr.expr)
            low_type = self._check_expression(expr.low)
            high_type = self._check_expression(expr.high)

            if expr_type and (expr_type != low_type or expr_type != high_type):
                raise self._error(
                    f"BETWEEN bounds must match expression type {expr_type}, got {low_type} and {high_type}",
                    expr
                )
            return "BOOLEAN"

        elif isinstance(expr, InOp):
            expr_type = self._check_expression(expr.expr)
            for v in expr.values:
                val_type = self._check_expression(v)
                if expr_type and val_type and expr_type != val_type:
                    raise self._error(f"IN list item type {val_type} does not match attribute type {expr_type}", v)
            return "BOOLEAN"

        return None
