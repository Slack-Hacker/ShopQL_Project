"""
ShopQL Recursive Descent Parser
Transforms a token stream into an Abstract Syntax Tree (AST) with detailed syntax error reporting.
"""

from typing import List, Optional, Dict, Any
import difflib

from .tokens import Token, TokenType, KEYWORDS
from .ast_nodes import (
    ASTNode, Statement, FindStatement, CountStatement, AddStatement,
    UpdateStatement, DeleteStatement, RestockStatement, PurchaseStatement, DescribeStatement,
    Expression, Literal, Identifier, BinaryOp, UnaryOp, BetweenOp, InOp, OrderByClause
)
from .errors import SyntaxError


class Parser:
    def __init__(self, tokens: List[Token], source: str = ""):
        self.tokens = tokens
        self.source = source
        self.current = 0

    def _peek(self, offset: int = 0) -> Token:
        idx = self.current + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return self.tokens[-1]  # Return EOF

    def _is_at_end(self) -> bool:
        return self._peek().type == TokenType.EOF

    def _check(self, token_type: TokenType) -> bool:
        if self._is_at_end():
            return False
        return self._peek().type == token_type

    def _advance(self) -> Token:
        if not self._is_at_end():
            self.current += 1
        return self.tokens[self.current - 1]

    def _match(self, *token_types: TokenType) -> bool:
        for t in token_types:
            if self._check(t):
                self._advance()
                return True
        return False

    def _error(self, message: str, token: Optional[Token] = None, suggestion: Optional[str] = None) -> SyntaxError:
        tok = token or self._peek()
        # If token is identifier, check if it's close to any keyword
        if not suggestion and tok.type == TokenType.IDENTIFIER:
            close = difflib.get_close_matches(tok.lexeme.upper(), list(KEYWORDS.keys()), n=1, cutoff=0.7)
            if close:
                suggestion = f"Did you mean keyword '{close[0]}'?"
        return SyntaxError(message, line=tok.line, column=tok.column, source=self.source, suggestion=suggestion)

    def _consume(self, token_type: TokenType, error_message: str, suggestion: Optional[str] = None) -> Token:
        if self._check(token_type):
            return self._advance()
        raise self._error(error_message, self._peek(), suggestion)

    # -----------------------------------------------------------------
    # Entry Point: Parse one or more statements
    # -----------------------------------------------------------------

    def parse(self) -> List[Statement]:
        statements: List[Statement] = []
        while not self._is_at_end():
            # Skip trailing stray semicolons
            if self._match(TokenType.SEMICOLON):
                continue
            stmt = self.parse_statement()
            statements.append(stmt)
            # Require or accept semicolon at the end of statement
            if self._check(TokenType.SEMICOLON):
                self._advance()
            elif not self._is_at_end():
                raise self._error(
                    f"Expected ';' to terminate statement, found '{self._peek().lexeme}'",
                    suggestion="Add a semicolon ';' at the end of your query."
                )
        return statements

    def parse_single(self) -> Statement:
        """Parse exactly one statement (convenience method)."""
        stmts = self.parse()
        if not stmts:
            raise self._error("Empty query", suggestion="Provide a ShopQL query like 'FIND PRODUCTS;'")
        return stmts[0]

    # -----------------------------------------------------------------
    # Statement Parsers
    # -----------------------------------------------------------------

    def parse_statement(self) -> Statement:
        tok = self._peek()

        if tok.type in (TokenType.FIND, TokenType.SHOW):
            return self.parse_find()
        elif tok.type == TokenType.COUNT:
            return self.parse_count()
        elif tok.type == TokenType.ADD:
            return self.parse_add()
        elif tok.type == TokenType.UPDATE:
            return self.parse_update()
        elif tok.type == TokenType.DELETE:
            return self.parse_delete()
        elif tok.type == TokenType.RESTOCK:
            return self.parse_restock()
        elif tok.type in (TokenType.BUY, TokenType.PURCHASE):
            return self.parse_purchase()
        elif tok.type in (TokenType.DESCRIBE, TokenType.SCHEMA):
            return self.parse_describe()
        else:
            commands = ["FIND", "SHOW", "ADD", "UPDATE", "DELETE", "RESTOCK", "BUY", "PURCHASE", "COUNT", "DESCRIBE", "SCHEMA"]
            close = difflib.get_close_matches(tok.lexeme.upper(), commands, n=1, cutoff=0.6)
            sug = f"Did you mean command '{close[0]}'?" if close else "Valid statements begin with FIND, SHOW, ADD, UPDATE, DELETE, RESTOCK, BUY, COUNT, or DESCRIBE."
            raise self._error(
                f"Unexpected token '{tok.lexeme}'. Expected query command (FIND, SHOW, ADD, UPDATE, DELETE, RESTOCK, BUY, COUNT, DESCRIBE)",
                tok,
                suggestion=sug
            )

    def parse_find(self) -> FindStatement:
        verb_tok = self._advance()
        verb = verb_tok.value

        self._consume(TokenType.PRODUCTS, f"Expected 'PRODUCTS' after '{verb}', found '{self._peek().lexeme}'",
                      suggestion=f"Use '{verb} PRODUCTS'")

        # Optional quick text search, e.g. FIND PRODUCTS "Laptop"
        search_query = None
        if self._check(TokenType.STRING):
            search_query = self._advance().value

        # Optional WHERE clause
        where_clause = None
        if self._match(TokenType.WHERE):
            where_clause = self.parse_expression()

        # Optional ORDER BY clause
        order_by = None
        if self._match(TokenType.ORDER):
            self._consume(TokenType.BY, "Expected 'BY' after 'ORDER'", suggestion="Use 'ORDER BY <column> [ASC|DESC]'")
            col_tok = self._advance()
            # The column could be an identifier or a keyword like PRICE, RATING, etc.
            col_name = col_tok.lexeme.upper()
            direction = "ASC"
            if self._match(TokenType.ASC):
                direction = "ASC"
            elif self._match(TokenType.DESC):
                direction = "DESC"
            order_by = OrderByClause(sort_field=col_name, direction=direction, line=col_tok.line, column=col_tok.column)

        # Optional LIMIT clause
        limit = None
        if self._match(TokenType.LIMIT):
            limit_tok = self._consume(TokenType.NUMBER, "Expected integer count after 'LIMIT'")
            if not isinstance(limit_tok.value, int) or limit_tok.value < 0:
                raise self._error("LIMIT must be a non-negative integer", limit_tok)
            limit = limit_tok.value

        return FindStatement(
            verb=verb,
            search_query=search_query,
            where_clause=where_clause,
            order_by=order_by,
            limit=limit,
            line=verb_tok.line,
            column=verb_tok.column
        )

    def parse_count(self) -> CountStatement:
        count_tok = self._advance()
        self._consume(TokenType.PRODUCTS, "Expected 'PRODUCTS' after 'COUNT'", suggestion="Use 'COUNT PRODUCTS'")
        where_clause = None
        if self._match(TokenType.WHERE):
            where_clause = self.parse_expression()
        return CountStatement(where_clause=where_clause, line=count_tok.line, column=count_tok.column)

    def parse_add(self) -> AddStatement:
        add_tok = self._advance()
        self._consume(TokenType.PRODUCT, "Expected 'PRODUCT' after 'ADD'", suggestion="Use 'ADD PRODUCT \"<name>\" ...'")

        name_tok = self._consume(TokenType.STRING, "Expected product name as a string literal, e.g. \"Laptop\"")
        name = name_tok.value

        price = 0.0
        category = "GENERAL"
        stock = 1
        rating = 5.0
        description = ""

        # Parse flexible attribute clauses: PRICE 55000 CATEGORY "ELECTRONICS" STOCK 10 RATING 4.8
        while not self._is_at_end() and self._peek().type != TokenType.SEMICOLON:
            curr = self._peek()
            curr_upper = curr.lexeme.upper()

            if curr.type == TokenType.PRICE or curr_upper == "PRICE":
                self._advance()
                price_tok = self._consume(TokenType.NUMBER, "Expected number after 'PRICE'")
                price = float(price_tok.value)
            elif curr.type == TokenType.CATEGORY or curr_upper == "CATEGORY":
                self._advance()
                cat_tok = self._consume(TokenType.STRING, "Expected category name as string literal, e.g. \"ELECTRONICS\"")
                category = cat_tok.value.upper()
            elif curr.type == TokenType.STOCK or curr_upper == "STOCK":
                self._advance()
                stock_tok = self._consume(TokenType.NUMBER, "Expected integer count after 'STOCK'")
                stock = int(stock_tok.value)
            elif curr.type == TokenType.RATING or curr_upper == "RATING":
                self._advance()
                rat_tok = self._consume(TokenType.NUMBER, "Expected rating number (0.0 - 5.0) after 'RATING'")
                rating = float(rat_tok.value)
            elif curr_upper == "DESCRIPTION":
                self._advance()
                desc_tok = self._consume(TokenType.STRING, "Expected description as string literal")
                description = desc_tok.value
            else:
                break

        return AddStatement(
            name=name,
            price=price,
            category=category,
            stock=stock,
            rating=rating,
            description=description,
            line=add_tok.line,
            column=add_tok.column
        )

    def parse_update(self) -> UpdateStatement:
        upd_tok = self._advance()
        target_name = None

        if self._match(TokenType.PRODUCTS):
            pass
        elif self._match(TokenType.PRODUCT):
            if self._check(TokenType.STRING):
                target_name = self._advance().value
        else:
            raise self._error("Expected 'PRODUCT' or 'PRODUCTS' after 'UPDATE'", suggestion="Use 'UPDATE PRODUCTS SET ...'")

        self._consume(TokenType.SET, "Expected 'SET' clause in UPDATE statement", suggestion="Use 'UPDATE ... SET col = val'")

        assignments: Dict[str, Expression] = {}
        while True:
            field_tok = self._advance()
            field_name = field_tok.lexeme.upper()
            self._consume(TokenType.EQUALS, f"Expected '=' after field '{field_name}' in SET clause")
            val_expr = self.parse_expression()
            assignments[field_name] = val_expr

            if not self._match(TokenType.COMMA):
                break

        where_clause = None
        if self._match(TokenType.WHERE):
            where_clause = self.parse_expression()

        return UpdateStatement(
            target_name=target_name,
            assignments=assignments,
            where_clause=where_clause,
            line=upd_tok.line,
            column=upd_tok.column
        )

    def parse_delete(self) -> DeleteStatement:
        del_tok = self._advance()
        target_name = None
        where_clause = None

        if self._match(TokenType.PRODUCTS):
            if self._match(TokenType.WHERE):
                where_clause = self.parse_expression()
        elif self._match(TokenType.PRODUCT):
            if self._check(TokenType.STRING):
                target_name = self._advance().value
            elif self._match(TokenType.WHERE):
                where_clause = self.parse_expression()
            else:
                raise self._error("Expected product name string or WHERE clause after 'DELETE PRODUCT'")
        else:
            raise self._error("Expected 'PRODUCT' or 'PRODUCTS' after 'DELETE'", suggestion="Use 'DELETE PRODUCT \"<name>\"' or 'DELETE PRODUCTS WHERE ...'")

        return DeleteStatement(
            target_name=target_name,
            where_clause=where_clause,
            line=del_tok.line,
            column=del_tok.column
        )

    def parse_restock(self) -> RestockStatement:
        restock_tok = self._advance()
        if self._match(TokenType.PRODUCT):
            pass  # Optional 'PRODUCT' keyword
        name_tok = self._consume(TokenType.STRING, "Expected product name as string literal in RESTOCK statement",
                                 suggestion='RESTOCK PRODUCT "Laptop" QUANTITY 10;')
        qty = 1
        curr = self._peek()
        curr_upper = curr.lexeme.upper()
        if curr.type == TokenType.QUANTITY or curr_upper in ("QUANTITY", "BY", "AMOUNT"):
            self._advance()
            qty_tok = self._consume(TokenType.NUMBER, "Expected restock quantity number")
            qty = int(qty_tok.value)

        return RestockStatement(target_name=name_tok.value, quantity=qty, line=restock_tok.line, column=restock_tok.column)

    def parse_purchase(self) -> PurchaseStatement:
        buy_tok = self._advance()
        if self._match(TokenType.PRODUCT):
            pass
        name_tok = self._consume(TokenType.STRING, "Expected product name as string literal in BUY/PURCHASE statement",
                                 suggestion='BUY PRODUCT "Laptop" QUANTITY 1;')
        qty = 1
        curr = self._peek()
        curr_upper = curr.lexeme.upper()
        if curr.type == TokenType.QUANTITY or curr_upper in ("QUANTITY", "AMOUNT"):
            self._advance()
            qty_tok = self._consume(TokenType.NUMBER, "Expected purchase quantity number")
            qty = int(qty_tok.value)

        return PurchaseStatement(target_name=name_tok.value, quantity=qty, line=buy_tok.line, column=buy_tok.column)

    def parse_describe(self) -> DescribeStatement:
        tok = self._advance()
        if tok.type == TokenType.DESCRIBE:
            self._consume(TokenType.PRODUCTS, "Expected 'PRODUCTS' after 'DESCRIBE'", suggestion="Use 'DESCRIBE PRODUCTS;'")
        return DescribeStatement(line=tok.line, column=tok.column)

    # -----------------------------------------------------------------
    # Expression Parsing with Operator Precedence
    # OR -> AND -> NOT -> RELATIONAL -> PRIMARY
    # -----------------------------------------------------------------

    def parse_expression(self) -> Expression:
        return self.parse_or()

    def parse_or(self) -> Expression:
        expr = self.parse_and()
        while self._match(TokenType.OR):
            op_tok = self.tokens[self.current - 1]
            right = self.parse_and()
            expr = BinaryOp(left=expr, op="OR", right=right, line=op_tok.line, column=op_tok.column)
        return expr

    def parse_and(self) -> Expression:
        expr = self.parse_not()
        while self._match(TokenType.AND):
            op_tok = self.tokens[self.current - 1]
            right = self.parse_not()
            expr = BinaryOp(left=expr, op="AND", right=right, line=op_tok.line, column=op_tok.column)
        return expr

    def parse_not(self) -> Expression:
        if self._match(TokenType.NOT):
            op_tok = self.tokens[self.current - 1]
            operand = self.parse_not()
            return UnaryOp(op="NOT", operand=operand, line=op_tok.line, column=op_tok.column)
        return self.parse_relational()

    def parse_relational(self) -> Expression:
        left = self.parse_primary()

        # Check for BETWEEN <low> AND <high>
        if self._match(TokenType.BETWEEN):
            bt_tok = self.tokens[self.current - 1]
            low = self.parse_primary()
            self._consume(TokenType.AND, "Expected 'AND' in BETWEEN expression", suggestion="Use 'expr BETWEEN min AND max'")
            high = self.parse_primary()
            return BetweenOp(expr=left, low=low, high=high, line=bt_tok.line, column=bt_tok.column)

        # Check for [NOT] IN ( ... )
        not_in = False
        if self._match(TokenType.NOT):
            if self._match(TokenType.IN):
                not_in = True
            else:
                # Put back NOT token
                self.current -= 1

        if not_in or self._match(TokenType.IN):
            in_tok = self.tokens[self.current - 1]
            self._consume(TokenType.LPAREN, "Expected '(' after IN")
            values: List[Expression] = []
            if not self._check(TokenType.RPAREN):
                while True:
                    values.append(self.parse_primary())
                    if not self._match(TokenType.COMMA):
                        break
            self._consume(TokenType.RPAREN, "Expected ')' closing IN list")
            return InOp(expr=left, values=values, not_in=not_in, line=in_tok.line, column=in_tok.column)

        # Standard relational operators: =, !=, <, <=, >, >=, CONTAINS, LIKE
        rel_ops = {
            TokenType.EQUALS: "=",
            TokenType.NOT_EQUALS: "!=",
            TokenType.LESS_THAN: "<",
            TokenType.LESS_EQUALS: "<=",
            TokenType.GREATER_THAN: ">",
            TokenType.GREATER_EQUALS: ">=",
            TokenType.CONTAINS: "CONTAINS",
            TokenType.LIKE: "LIKE",
        }

        for tok_type, op_str in rel_ops.items():
            if self._match(tok_type):
                op_tok = self.tokens[self.current - 1]
                right = self.parse_primary()
                return BinaryOp(left=left, op=op_str, right=right, line=op_tok.line, column=op_tok.column)

        return left

    def parse_primary(self) -> Expression:
        tok = self._peek()

        # Parenthesized expression
        if self._match(TokenType.LPAREN):
            expr = self.parse_expression()
            self._consume(TokenType.RPAREN, "Expected closing ')' after expression", suggestion="Add a matching ')'")
            return expr

        # Literals
        if self._match(TokenType.STRING):
            prev = self.tokens[self.current - 1]
            return Literal(value=prev.value, literal_type="STRING", line=prev.line, column=prev.column)

        if self._match(TokenType.NUMBER):
            prev = self.tokens[self.current - 1]
            return Literal(value=prev.value, literal_type="NUMBER", line=prev.line, column=prev.column)

        if self._match(TokenType.BOOLEAN):
            prev = self.tokens[self.current - 1]
            return Literal(value=prev.value, literal_type="BOOLEAN", line=prev.line, column=prev.column)

        # Identifier or Keyword acting as column name (e.g. PRICE, CATEGORY, STOCK, RATING, NAME, ID)
        if tok.type in (TokenType.IDENTIFIER, TokenType.PRICE, TokenType.CATEGORY, TokenType.STOCK, TokenType.RATING):
            self._advance()
            return Identifier(name=tok.lexeme.upper(), line=tok.line, column=tok.column)

        raise self._error(
            f"Expected expression, found '{tok.lexeme}'",
            tok,
            suggestion="Valid expressions include column names, string literals (\"text\"), or numbers (123)."
        )
