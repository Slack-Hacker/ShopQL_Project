"""
ShopQL Lexer (Lexical Analyzer)
Converts raw ShopQL query string into a stream of tokens with accurate line & column positions.
"""

from typing import List, Optional
import difflib
from .tokens import Token, TokenType, KEYWORDS
from .errors import LexerError


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.length = len(source)
        self.position = 0
        self.line = 1
        self.column = 1

    def _peek(self, offset: int = 0) -> Optional[str]:
        idx = self.position + offset
        if idx < self.length:
            return self.source[idx]
        return None

    def _advance(self) -> Optional[str]:
        ch = self._peek()
        if ch is not None:
            self.position += 1
            if ch == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
        return ch

    def _match(self, expected: str) -> bool:
        if self._peek() == expected:
            self._advance()
            return True
        return False

    def _skip_whitespace_and_comments(self):
        while self.position < self.length:
            ch = self._peek()
            if ch in (' ', '\t', '\r', '\n'):
                self._advance()
            # Single-line comment: -- or //
            elif ch == '-' and self._peek(1) == '-':
                self._advance()
                self._advance()
                while self._peek() and self._peek() != '\n':
                    self._advance()
            elif ch == '/' and self._peek(1) == '/':
                self._advance()
                self._advance()
                while self._peek() and self._peek() != '\n':
                    self._advance()
            # Multi-line comment: /* ... */
            elif ch == '/' and self._peek(1) == '*':
                start_line = self.line
                start_col = self.column
                self._advance()
                self._advance()
                closed = False
                while self.position < self.length:
                    if self._peek() == '*' and self._peek(1) == '/':
                        self._advance()
                        self._advance()
                        closed = True
                        break
                    self._advance()
                if not closed:
                    raise LexerError(
                        "Unterminated block comment (missing '*/')",
                        line=start_line,
                        column=start_col,
                        source=self.source,
                        suggestion="Close the comment with '*/'"
                    )
            else:
                break

    def _read_string(self, quote_char: str) -> Token:
        start_line = self.line
        start_col = self.column
        self._advance()  # Skip opening quote

        value_chars = []
        while True:
            ch = self._peek()
            if ch is None or ch == '\n':
                raise LexerError(
                    f"Unterminated string literal (missing closing {quote_char})",
                    line=start_line,
                    column=start_col,
                    source=self.source,
                    suggestion=f"Add a closing {quote_char} to terminate the string."
                )
            if ch == quote_char:
                self._advance()  # Skip closing quote
                break
            if ch == '\\':
                self._advance()  # Skip backslash
                escaped = self._peek()
                if escaped == 'n':
                    value_chars.append('\n')
                elif escaped == 't':
                    value_chars.append('\t')
                elif escaped == 'r':
                    value_chars.append('\r')
                elif escaped == quote_char:
                    value_chars.append(quote_char)
                elif escaped == '\\':
                    value_chars.append('\\')
                elif escaped is not None:
                    value_chars.append(escaped)
                self._advance()
            else:
                value_chars.append(ch)
                self._advance()

        val = "".join(value_chars)
        return Token(TokenType.STRING, val, start_line, start_col, lexeme=f'{quote_char}{val}{quote_char}')

    def _read_number(self) -> Token:
        start_line = self.line
        start_col = self.column
        num_str = []
        is_float = False

        while self._peek() and self._peek().isdigit():
            num_str.append(self._advance())

        if self._peek() == '.' and self._peek(1) and self._peek(1).isdigit():
            is_float = True
            num_str.append(self._advance())  # Append '.'
            while self._peek() and self._peek().isdigit():
                num_str.append(self._advance())

        lexeme = "".join(num_str)
        val = float(lexeme) if is_float else int(lexeme)
        return Token(TokenType.NUMBER, val, start_line, start_col, lexeme=lexeme)

    def _read_identifier_or_keyword(self) -> Token:
        start_line = self.line
        start_col = self.column
        chars = []

        while self._peek() and (self._peek().isalnum() or self._peek() == '_'):
            chars.append(self._advance())

        lexeme = "".join(chars)
        upper_lexeme = lexeme.upper()

        if upper_lexeme in KEYWORDS:
            tok_type = KEYWORDS[upper_lexeme]
            val = True if tok_type == TokenType.BOOLEAN and upper_lexeme == "TRUE" else \
                  False if tok_type == TokenType.BOOLEAN and upper_lexeme == "FALSE" else upper_lexeme
            return Token(tok_type, val, start_line, start_col, lexeme=lexeme)
        
        # Check if user misspelled a known keyword
        close_matches = difflib.get_close_matches(upper_lexeme, list(KEYWORDS.keys()), n=1, cutoff=0.75)
        # Note: We return IDENTIFIER, but semantic or parser can use close_matches if an identifier is out of place
        return Token(TokenType.IDENTIFIER, lexeme, start_line, start_col, lexeme=lexeme)

    def tokenize(self) -> List[Token]:
        tokens: List[Token] = []

        while self.position < self.length:
            self._skip_whitespace_and_comments()
            if self.position >= self.length:
                break

            ch = self._peek()
            start_line = self.line
            start_col = self.column

            # String literals
            if ch in ('"', "'"):
                tokens.append(self._read_string(ch))
            # Numbers (including negative numbers)
            elif ch.isdigit() or (ch == '-' and self._peek(1) and self._peek(1).isdigit()):
                is_negative = False
                if ch == '-':
                    is_negative = True
                    self._advance()
                num_tok = self._read_number()
                if is_negative:
                    num_tok.value = -num_tok.value
                    num_tok.lexeme = f"-{num_tok.lexeme}"
                    num_tok.column = start_col
                tokens.append(num_tok)
            # Identifiers & Keywords
            elif ch.isalpha() or ch == '_':
                tokens.append(self._read_identifier_or_keyword())
            # Semicolon
            elif ch == ';':
                self._advance()
                tokens.append(Token(TokenType.SEMICOLON, ";", start_line, start_col, ";"))
            # Comma
            elif ch == ',':
                self._advance()
                tokens.append(Token(TokenType.COMMA, ",", start_line, start_col, ","))
            # Parentheses
            elif ch == '(':
                self._advance()
                tokens.append(Token(TokenType.LPAREN, "(", start_line, start_col, "("))
            elif ch == ')':
                self._advance()
                tokens.append(Token(TokenType.RPAREN, ")", start_line, start_col, ")"))
            # Relational Operators
            elif ch == '=':
                self._advance()
                # Friendly error if user wrote ==
                if self._match('='):
                    tokens.append(Token(TokenType.EQUALS, "=", start_line, start_col, "=="))
                else:
                    tokens.append(Token(TokenType.EQUALS, "=", start_line, start_col, "="))
            elif ch == '!':
                self._advance()
                if self._match('='):
                    tokens.append(Token(TokenType.NOT_EQUALS, "!=", start_line, start_col, "!="))
                else:
                    raise LexerError(
                        "Unexpected character '!' (did you mean '!='?)",
                        line=start_line,
                        column=start_col,
                        source=self.source,
                        suggestion="Use '!=' for inequality."
                    )
            elif ch == '<':
                self._advance()
                if self._match('='):
                    tokens.append(Token(TokenType.LESS_EQUALS, "<=", start_line, start_col, "<="))
                elif self._match('>'):
                    tokens.append(Token(TokenType.NOT_EQUALS, "!=", start_line, start_col, "<>"))
                else:
                    tokens.append(Token(TokenType.LESS_THAN, "<", start_line, start_col, "<"))
            elif ch == '>':
                self._advance()
                if self._match('='):
                    tokens.append(Token(TokenType.GREATER_EQUALS, ">=", start_line, start_col, ">="))
                else:
                    tokens.append(Token(TokenType.GREATER_THAN, ">", start_line, start_col, ">"))
            else:
                self._advance()
                raise LexerError(
                    f"Unexpected character '{ch}'",
                    line=start_line,
                    column=start_col,
                    source=self.source,
                    suggestion="Remove or replace this character."
                )

        tokens.append(Token(TokenType.EOF, "", self.line, self.column, ""))
        return tokens
