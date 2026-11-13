"""
ShopQL Error Handling & Diagnostics
Provides formatted error reporting with line/column pointers and suggestions.
"""

from typing import Optional, List


def format_error_snippet(source: str, line: int, column: int, message: str, suggestion: Optional[str] = None) -> str:
    """
    Formats a user-friendly compiler diagnostic pointing directly to the offending token:
    
    Syntax Error at line 2, column 15:
        WHERE PRIC < 2000
              ^^^^
    Unknown attribute 'PRIC'. Did you mean 'PRICE'?
    """
    lines = source.splitlines()
    if not lines:
        return f"Error at line {line}, column {column}: {message}"
    
    # Line numbers are 1-based
    line_idx = max(0, min(line - 1, len(lines) - 1))
    code_line = lines[line_idx]
    
    # Calculate caret pointer
    col_idx = max(1, column)
    caret_indent = " " * (col_idx - 1)
    pointer = f"{caret_indent}^"
    
    result = [
        f"ShopQL Error [Line {line}, Column {column}]:",
        f"    {code_line}",
        f"    {pointer}",
        f"  --> {message}"
    ]
    if suggestion:
        result.append(f"  Tip: {suggestion}")
        
    return "\n".join(result)


class ShopQLError(Exception):
    """Base class for all ShopQL exceptions."""
    def __init__(self, message: str, line: int = 1, column: int = 1, source: str = "", suggestion: Optional[str] = None):
        self.message = message
        self.line = line
        self.column = column
        self.source = source
        self.suggestion = suggestion
        formatted = format_error_snippet(source, line, column, message, suggestion) if source else message
        super().__init__(formatted)


class LexerError(ShopQLError):
    """Raised when an invalid character or unterminated token is encountered."""
    pass


class SyntaxError(ShopQLError):
    """Raised when query fails grammatical validation."""
    pass


class SemanticError(ShopQLError):
    """Raised when query is grammatically valid but semantically invalid (e.g. unknown column, type error)."""
    pass


class ExecutionError(ShopQLError):
    """Raised when runtime execution fails (e.g. insufficient stock)."""
    pass

