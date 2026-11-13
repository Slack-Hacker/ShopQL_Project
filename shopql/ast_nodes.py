"""
ShopQL Abstract Syntax Tree (AST) Nodes
Represents structured syntax tree produced by the parser.
"""

from dataclasses import dataclass, field
from typing import Any, List, Optional, Dict


@dataclass
class ASTNode:
    line: int = 1
    column: int = 1

    def to_dict(self) -> Dict[str, Any]:
        """Convert AST node to dictionary for JSON serialization & visual tree rendering."""
        res = {"_type": self.__class__.__name__}
        for k, v in self.__dict__.items():
            if isinstance(v, ASTNode):
                res[k] = v.to_dict()
            elif isinstance(v, list):
                res[k] = [item.to_dict() if isinstance(item, ASTNode) else item for item in v]
            else:
                res[k] = v
        return res


# -------------------------------------------------------------
# Expressions
# -------------------------------------------------------------

@dataclass
class Expression(ASTNode):
    pass


@dataclass
class Literal(Expression):
    value: Any = None
    literal_type: str = "STRING"  # STRING, NUMBER, BOOLEAN


@dataclass
class Identifier(Expression):
    name: str = ""


@dataclass
class BinaryOp(Expression):
    left: Expression = field(default_factory=Expression)
    op: str = ""  # '=', '!=', '<', '<=', '>', '>=', 'AND', 'OR', 'CONTAINS', 'LIKE'
    right: Expression = field(default_factory=Expression)


@dataclass
class UnaryOp(Expression):
    op: str = ""  # 'NOT'
    operand: Expression = field(default_factory=Expression)


@dataclass
class BetweenOp(Expression):
    expr: Expression = field(default_factory=Expression)
    low: Expression = field(default_factory=Expression)
    high: Expression = field(default_factory=Expression)


@dataclass
class InOp(Expression):
    expr: Expression = field(default_factory=Expression)
    values: List[Expression] = field(default_factory=list)
    not_in: bool = False


@dataclass
class OrderByClause(ASTNode):
    sort_field: str = "PRICE"
    direction: str = "ASC"  # 'ASC' or 'DESC'


# -------------------------------------------------------------
# Statements
# -------------------------------------------------------------

@dataclass
class Statement(ASTNode):
    pass


@dataclass
class FindStatement(Statement):
    verb: str = "FIND"  # "FIND" or "SHOW"
    search_query: Optional[str] = None
    where_clause: Optional[Expression] = None
    order_by: Optional[OrderByClause] = None
    limit: Optional[int] = None


@dataclass
class CountStatement(Statement):
    where_clause: Optional[Expression] = None


@dataclass
class AddStatement(Statement):
    name: str = ""
    price: float = 0.0
    category: str = "GENERAL"
    stock: int = 1
    rating: float = 5.0
    description: str = ""


@dataclass
class UpdateStatement(Statement):
    target_name: Optional[str] = None
    assignments: Dict[str, Expression] = field(default_factory=dict)
    where_clause: Optional[Expression] = None


@dataclass
class DeleteStatement(Statement):
    target_name: Optional[str] = None
    where_clause: Optional[Expression] = None


@dataclass
class RestockStatement(Statement):
    target_name: str = ""
    quantity: int = 1


@dataclass
class PurchaseStatement(Statement):
    target_name: str = ""
    quantity: int = 1


@dataclass
class DescribeStatement(Statement):
    pass
