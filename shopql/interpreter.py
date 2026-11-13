"""
ShopQL Interpreter & Execution Engine
Executes parsed AST statements against the product database.
"""

from typing import List, Dict, Any, Optional
import time
import re
from dataclasses import dataclass, field

from .ast_nodes import (
    Statement, FindStatement, CountStatement, AddStatement,
    UpdateStatement, DeleteStatement, RestockStatement, PurchaseStatement, DescribeStatement,
    Expression, Literal, Identifier, BinaryOp, UnaryOp, BetweenOp, InOp
)
from .database import Database
from .errors import ExecutionError


@dataclass
class QueryResult:
    statement_type: str
    columns: List[str] = field(default_factory=list)
    rows: List[Dict[str, Any]] = field(default_factory=list)
    count: int = 0
    message: str = ""
    execution_time_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "statement_type": self.statement_type,
            "columns": self.columns,
            "rows": self.rows,
            "count": self.count,
            "message": self.message,
            "execution_time_ms": self.execution_time_ms
        }


class Interpreter:
    def __init__(self, db: Database):
        self.db = db

    def execute(self, statement: Statement) -> QueryResult:
        start_t = time.perf_counter()

        if isinstance(statement, FindStatement):
            res = self._execute_find(statement)
        elif isinstance(statement, CountStatement):
            res = self._execute_count(statement)
        elif isinstance(statement, AddStatement):
            res = self._execute_add(statement)
        elif isinstance(statement, UpdateStatement):
            res = self._execute_update(statement)
        elif isinstance(statement, DeleteStatement):
            res = self._execute_delete(statement)
        elif isinstance(statement, RestockStatement):
            res = self._execute_restock(statement)
        elif isinstance(statement, PurchaseStatement):
            res = self._execute_purchase(statement)
        elif isinstance(statement, DescribeStatement):
            res = self._execute_describe(statement)
        else:
            raise ExecutionError(f"Unsupported statement type: {type(statement).__name__}")

        res.execution_time_ms = round((time.perf_counter() - start_t) * 1000, 3)
        return res

    def _execute_find(self, stmt: FindStatement) -> QueryResult:
        products = self.db.get_all()

        # 1. Text search if specified
        if stmt.search_query:
            q = stmt.search_query.strip().lower()
            products = [
                p for p in products
                if q in p["name"].lower() or q in p["category"].lower() or q in p.get("description", "").lower()
            ]

        # 2. WHERE filter condition
        if stmt.where_clause:
            products = [p for p in products if bool(self._eval_expr(stmt.where_clause, p))]

        # 3. ORDER BY
        if stmt.order_by:
            col = stmt.order_by.sort_field.lower()
            reverse = stmt.order_by.direction.upper() == "DESC"
            
            def sort_key(p):
                val = p.get(col, 0)
                if isinstance(val, str):
                    return val.lower()
                return val
            
            products.sort(key=sort_key, reverse=reverse)

        # 4. LIMIT
        if stmt.limit is not None:
            products = products[:stmt.limit]

        cols = ["id", "name", "category", "price", "stock", "rating", "description"]
        msg = f"Found {len(products)} product{'s' if len(products) != 1 else ''}."
        return QueryResult(
            statement_type="FIND",
            columns=cols,
            rows=products,
            count=len(products),
            message=msg
        )

    def _execute_count(self, stmt: CountStatement) -> QueryResult:
        products = self.db.get_all()
        if stmt.where_clause:
            products = [p for p in products if bool(self._eval_expr(stmt.where_clause, p))]
        count = len(products)
        return QueryResult(
            statement_type="COUNT",
            columns=["count"],
            rows=[{"count": count}],
            count=count,
            message=f"Total matching products: {count}"
        )

    def _execute_add(self, stmt: AddStatement) -> QueryResult:
        new_prod = self.db.add_product(
            name=stmt.name,
            price=stmt.price,
            category=stmt.category,
            stock=stmt.stock,
            rating=stmt.rating,
            description=stmt.description
        )
        cols = ["id", "name", "category", "price", "stock", "rating", "description"]
        return QueryResult(
            statement_type="ADD",
            columns=cols,
            rows=[new_prod],
            count=1,
            message=f"Successfully added product '{stmt.name}' (ID #{new_prod['id']})."
        )

    def _execute_update(self, stmt: UpdateStatement) -> QueryResult:
        products = self.db.get_all()
        matching = []

        if stmt.target_name:
            target_norm = stmt.target_name.strip().lower()
            matching = [p for p in products if p["name"].strip().lower() == target_norm]
        elif stmt.where_clause:
            matching = [p for p in products if bool(self._eval_expr(stmt.where_clause, p))]
        else:
            matching = products

        updated_rows = []
        for p in matching:
            updates = {}
            for field_name, expr in stmt.assignments.items():
                val = self._eval_expr(expr, p)
                updates[field_name.lower()] = val
            upd = self.db.update_product(p["id"], updates)
            if upd:
                updated_rows.append(upd)

        cols = ["id", "name", "category", "price", "stock", "rating", "description"]
        return QueryResult(
            statement_type="UPDATE",
            columns=cols,
            rows=updated_rows,
            count=len(updated_rows),
            message=f"Updated {len(updated_rows)} product{'s' if len(updated_rows) != 1 else ''}."
        )

    def _execute_delete(self, stmt: DeleteStatement) -> QueryResult:
        products = self.db.get_all()
        to_delete = []

        if stmt.target_name:
            target_norm = stmt.target_name.strip().lower()
            to_delete = [p for p in products if p["name"].strip().lower() == target_norm]
        elif stmt.where_clause:
            to_delete = [p for p in products if bool(self._eval_expr(stmt.where_clause, p))]
        else:
            raise ExecutionError("DELETE without WHERE or product name would delete all products. Use a specific condition.")

        deleted_count = 0
        deleted_names = []
        for p in to_delete:
            if self.db.delete_product(p["id"]):
                deleted_count += 1
                deleted_names.append(p["name"])

        cols = ["id", "name", "category", "price", "stock", "rating"]
        return QueryResult(
            statement_type="DELETE",
            columns=cols,
            rows=to_delete,
            count=deleted_count,
            message=f"Deleted {deleted_count} product(s): {', '.join(deleted_names) if deleted_names else 'None'}."
        )

    def _execute_restock(self, stmt: RestockStatement) -> QueryResult:
        prod = self.db.restock(stmt.target_name, stmt.quantity)
        cols = ["id", "name", "category", "price", "stock", "rating"]
        return QueryResult(
            statement_type="RESTOCK",
            columns=cols,
            rows=[prod],
            count=1,
            message=f"Restocked '{stmt.target_name}' by +{stmt.quantity}. New stock level: {prod['stock']} units."
        )

    def _execute_purchase(self, stmt: PurchaseStatement) -> QueryResult:
        prod = self.db.purchase(stmt.target_name, stmt.quantity)
        total_price = round(prod["price"] * stmt.quantity, 2)
        cols = ["id", "name", "category", "price", "stock", "rating"]
        return QueryResult(
            statement_type="PURCHASE",
            columns=cols,
            rows=[prod],
            count=1,
            message=f"Purchased {stmt.quantity}x '{stmt.target_name}' for ${total_price}. Remaining stock: {prod['stock']} units."
        )

    def _execute_describe(self, stmt: DescribeStatement) -> QueryResult:
        schema_rows = [
            {"column": "ID", "type": "INTEGER", "description": "Unique auto-generated product ID (Primary Key)"},
            {"column": "NAME", "type": "STRING", "description": "Title or model name of the product"},
            {"column": "PRICE", "type": "FLOAT", "description": "Unit price in dollars ($)"},
            {"column": "CATEGORY", "type": "STRING", "description": "Category (e.g. ELECTRONICS, BOOKS, HOME, ACCESSORIES)"},
            {"column": "STOCK", "type": "INTEGER", "description": "Current inventory units available in stock"},
            {"column": "RATING", "type": "FLOAT", "description": "Customer satisfaction score (0.0 - 5.0)"},
            {"column": "DESCRIPTION", "type": "STRING", "description": "Detailed product description and specs"},
        ]
        return QueryResult(
            statement_type="DESCRIBE",
            columns=["column", "type", "description"],
            rows=schema_rows,
            count=len(schema_rows),
            message="Product catalog schema."
        )

    # -------------------------------------------------------------
    # Expression Evaluator
    # -------------------------------------------------------------

    def _eval_expr(self, expr: Expression, product: Dict[str, Any]) -> Any:
        if isinstance(expr, Literal):
            return expr.value

        elif isinstance(expr, Identifier):
            key = expr.name.lower()
            return product.get(key, None)

        elif isinstance(expr, UnaryOp):
            if expr.op == "NOT":
                return not self._eval_expr(expr.operand, product)

        elif isinstance(expr, BinaryOp):
            # Short-circuit logical operators
            if expr.op == "AND":
                left_val = self._eval_expr(expr.left, product)
                if not left_val:
                    return False
                return bool(self._eval_expr(expr.right, product))

            if expr.op == "OR":
                left_val = self._eval_expr(expr.left, product)
                if left_val:
                    return True
                return bool(self._eval_expr(expr.right, product))

            left_val = self._eval_expr(expr.left, product)
            right_val = self._eval_expr(expr.right, product)

            if expr.op == "=":
                if isinstance(left_val, str) and isinstance(right_val, str):
                    return left_val.strip().lower() == right_val.strip().lower()
                return left_val == right_val

            elif expr.op == "!=":
                if isinstance(left_val, str) and isinstance(right_val, str):
                    return left_val.strip().lower() != right_val.strip().lower()
                return left_val != right_val

            elif expr.op == "<":
                return left_val < right_val

            elif expr.op == "<=":
                return left_val <= right_val

            elif expr.op == ">":
                return left_val > right_val

            elif expr.op == ">=":
                return left_val >= right_val

            elif expr.op == "CONTAINS":
                haystack = str(left_val or "").lower()
                needle = str(right_val or "").lower()
                return needle in haystack

            elif expr.op == "LIKE":
                # Convert SQL % wildcard to regex
                pattern = str(right_val or "")
                regex_pattern = "^" + re.escape(pattern).replace(r"\%", ".*").replace(r"\_", ".") + "$"
                val_str = str(left_val or "")
                return bool(re.match(regex_pattern, val_str, re.IGNORECASE))

        elif isinstance(expr, BetweenOp):
            val = self._eval_expr(expr.expr, product)
            low = self._eval_expr(expr.low, product)
            high = self._eval_expr(expr.high, product)
            return low <= val <= high

        elif isinstance(expr, InOp):
            val = self._eval_expr(expr.expr, product)
            list_vals = [self._eval_expr(v, product) for v in expr.values]
            if isinstance(val, str):
                list_lower = [str(x).strip().lower() for x in list_vals]
                contained = val.strip().lower() in list_lower
            else:
                contained = val in list_vals
            return not contained if expr.not_in else contained

        return None
