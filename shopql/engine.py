"""
ShopQL Engine
High-level compiler facade unifying Lexer, Parser, Semantic Analyzer, and Interpreter.
"""

from typing import List, Dict, Any, Optional
import time

from .tokens import Token
from .ast_nodes import Statement
from .lexer import Lexer
from .parser import Parser
from .semantic import SemanticAnalyzer
from .database import Database
from .interpreter import Interpreter, QueryResult
from .errors import ShopQLError


class EngineResult:
    def __init__(self, query: str):
        self.query = query
        self.tokens: List[Token] = []
        self.ast: List[Statement] = []
        self.results: List[QueryResult] = []
        self.compile_time_ms: float = 0.0
        self.total_time_ms: float = 0.0
        self.error: Optional[str] = None
        self.success: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "success": self.success,
            "error": self.error,
            "compile_time_ms": self.compile_time_ms,
            "total_time_ms": self.total_time_ms,
            "tokens": [t.to_dict() for t in self.tokens if t.type.name != "EOF"],
            "ast": [s.to_dict() for s in self.ast],
            "results": [r.to_dict() for r in self.results]
        }


class ShopQLEngine:
    def __init__(self, db: Optional[Database] = None, persistence_file: Optional[str] = None):
        self.db = db or Database(persistence_file=persistence_file)
        self.interpreter = Interpreter(self.db)

    def execute(self, query: str) -> EngineResult:
        res = EngineResult(query)
        total_start = time.perf_counter()

        try:
            # Phase 1: Lexical Analysis (Scanning)
            compile_start = time.perf_counter()
            lexer = Lexer(query)
            res.tokens = lexer.tokenize()

            # Phase 2: Syntactic Analysis (Parsing)
            parser = Parser(res.tokens, source=query)
            res.ast = parser.parse()

            # Phase 3: Semantic Analysis (Type Checking & Validation)
            semantic = SemanticAnalyzer(source=query)
            for stmt in res.ast:
                semantic.analyze(stmt)
            res.compile_time_ms = round((time.perf_counter() - compile_start) * 1000, 3)

            # Phase 4: Execution / Interpretation
            for stmt in res.ast:
                qr = self.interpreter.execute(stmt)
                res.results.append(qr)

            res.success = True

        except ShopQLError as e:
            res.success = False
            res.error = str(e)
        except Exception as e:
            res.success = False
            res.error = f"Internal Execution Error: {str(e)}"

        res.total_time_ms = round((time.perf_counter() - total_start) * 1000, 3)
        return res

