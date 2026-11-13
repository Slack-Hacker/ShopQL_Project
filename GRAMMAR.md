# ShopQL Grammar & Language Specification

This document provides the formal grammar specification, operator precedence hierarchy, lexical structure, and compiler architecture for **ShopQL** (E-Commerce Query Language).

---

## 1. Lexical Grammar

### 1.1 Keywords (Case-Insensitive)
```
FIND, SHOW, PRODUCTS, PRODUCT, ADD, UPDATE, DELETE, RESTOCK, BUY, PURCHASE, COUNT, DESCRIBE, SCHEMA,
WHERE, SET, ORDER, BY, ASC, DESC, LIMIT, QUANTITY, PRICE, CATEGORY, STOCK, RATING,
AND, OR, NOT, CONTAINS, LIKE, BETWEEN, IN, TRUE, FALSE
```

### 1.2 Literals & Identifiers
- **Numeric Literals (`NUMBER`)**:
  - Integer: `[0-9]+` (e.g. `2000`, `55000`)
  - Floating Point: `[0-9]+\.[0-9]+` (e.g. `4.5`, `19.99`)
  - Negative Numbers: `-[0-9]+(\.[0-9]+)?` (e.g. `-10`)
- **String Literals (`STRING`)**:
  - Enclosed in double quotes `"` or single quotes `'`.
  - Supports escape characters: `\"`, `\'`, `\\`, `\n`, `\t`.
  - Examples: `"Laptop"`, `"ELECTRONICS"`, `'Clean Code'`
- **Boolean Literals (`BOOLEAN`)**:
  - `TRUE`, `FALSE`
- **Identifiers (`IDENTIFIER`)**:
  - `[A-Za-z_][A-Za-z0-9_]*`
  - Examples: `PRICE`, `CATEGORY`, `STOCK`, `RATING`, `NAME`, `ID`, `DESCRIPTION`

### 1.3 Operators & Punctuation
- Relational Operators: `=`, `!=`, `<>`, `<`, `<=`, `>`, `>=`
- String Matching: `CONTAINS`, `LIKE`
- Range & Set: `BETWEEN`, `IN`
- Logical Operators: `AND`, `OR`, `NOT`
- Delimiters: `;`, `,`, `(`, `)`
- Comments:
  - Single-line: `-- comment` or `// comment`
  - Multi-line: `/* comment */`

---

## 2. Syntactic Grammar (EBNF)

```ebnf
QueryBatch       ::= Statement ( ';' Statement )* ';'? EOF

Statement        ::= FindStmt
                   | CountStmt
                   | AddStmt
                   | UpdateStmt
                   | DeleteStmt
                   | RestockStmt
                   | PurchaseStmt
                   | DescribeStmt

(* Query Statements *)
FindStmt         ::= ( "FIND" | "SHOW" ) "PRODUCTS" ( StringLiteral )?
                     ( "WHERE" Condition )?
                     ( "ORDER" "BY" Identifier ( "ASC" | "DESC" )? )?
                     ( "LIMIT" IntegerLiteral )?

CountStmt        ::= "COUNT" "PRODUCTS" ( "WHERE" Condition )?

DescribeStmt     ::= ( "DESCRIBE" "PRODUCTS" | "SCHEMA" )

(* Modification & Inventory Statements *)
AddStmt          ::= "ADD" "PRODUCT" StringLiteral ( ProductAttr )*

ProductAttr      ::= "PRICE" NumberLiteral
                   | "CATEGORY" StringLiteral
                   | "STOCK" IntegerLiteral
                   | "RATING" NumberLiteral
                   | "DESCRIPTION" StringLiteral

UpdateStmt       ::= "UPDATE" ( "PRODUCTS" | "PRODUCT" ( StringLiteral )? )
                     "SET" Assignment ( ',' Assignment )*
                     ( "WHERE" Condition )?

Assignment       ::= Identifier '=' Expression

DeleteStmt       ::= "DELETE" ( "PRODUCTS" | "PRODUCT" StringLiteral )
                     ( "WHERE" Condition )?

RestockStmt      ::= "RESTOCK" ( "PRODUCT" )? StringLiteral
                     ( "QUANTITY" | "BY" | "AMOUNT" )? IntegerLiteral

PurchaseStmt     ::= ( "BUY" | "PURCHASE" ) ( "PRODUCT" )? StringLiteral
                     ( ( "QUANTITY" | "AMOUNT" )? IntegerLiteral )?

(* Expression Precedence Hierarchy *)
Condition        ::= OrExpr

OrExpr           ::= AndExpr ( "OR" AndExpr )*

AndExpr          ::= NotExpr ( "AND" NotExpr )*

NotExpr          ::= "NOT" NotExpr
                   | RelationalExpr

RelationalExpr   ::= PrimaryExpr (
                       RelOp PrimaryExpr
                     | "BETWEEN" PrimaryExpr "AND" PrimaryExpr
                     | ( "NOT" )? "IN" '(' ExprList ')'
                     | "CONTAINS" PrimaryExpr
                     | "LIKE" PrimaryExpr
                     )?

PrimaryExpr      ::= '(' Condition ')'
                   | Identifier
                   | NumberLiteral
                   | StringLiteral
                   | BooleanLiteral

RelOp            ::= '=' | '!=' | '<>' | '<' | '<=' | '>' | '>='

ExprList         ::= PrimaryExpr ( ',' PrimaryExpr )*
```

---

## 3. Operator Precedence & Associativity

| Precedence | Operator | Associativity | Description |
|:---:|:---|:---:|:---|
| **1 (Highest)** | `( ... )`, Literals, Identifiers | N/A | Grouping and primary operands |
| **2** | `NOT` | Right | Logical negation |
| **3** | `=`, `!=`, `<>`, `<`, `<=`, `>`, `>=` | Non-assoc | Relational comparisons |
| **3** | `CONTAINS`, `LIKE` | Non-assoc | Substring and wildcard pattern matching |
| **3** | `BETWEEN ... AND ...` | Non-assoc | Range containment |
| **3** | `[NOT] IN ( ... )` | Non-assoc | Set membership |
| **4** | `AND` | Left | Logical conjunction (short-circuiting) |
| **5 (Lowest)** | `OR` | Left | Logical disjunction (short-circuiting) |

---

## 4. Compiler Architecture & Phases

```mermaid
flowchart LR
    A["Raw Query String"] --> B["Lexer (Scanner)"]
    B -->|Token Stream + Line/Col| C["Parser (Recursive Descent)"]
    C -->|Abstract Syntax Tree (AST)| D["Semantic Analyzer"]
    D -->|Type-Checked AST| E["Interpreter (Execution Engine)"]
    E --> F[("Product Catalog / Store")]
    E --> G["QueryResult (Rows, Metrics)"]
```

1. **Lexical Analysis (`lexer.py`)**:
   - Converts the input stream into strongly-typed `Token` objects with exact line and column coordinates.
   - Strips single-line (`--`, `//`) and multi-line (`/* ... */`) comments.
   - Detects unterminated strings, invalid numeric formats, and unknown tokens.

2. **Parsing & AST Construction (`parser.py`)**:
   - Uses recursive descent to build a clean AST.
   - Enforces operator precedence without ambiguity.
   - Implements error recovery and suggests keyword corrections when near-miss identifiers are encountered (e.g. `WHER` → `WHERE`).

3. **Semantic Analysis (`semantic.py`)**:
   - Verifies referenced columns exist in the product schema (`ID`, `NAME`, `PRICE`, `CATEGORY`, `STOCK`, `RATING`, `DESCRIPTION`).
   - Validates type safety (e.g., prevents comparing numeric `PRICE` with string literals using `<`).
   - Ensures inventory constraints: prices and ratings are positive/bounded, stock is non-negative, and immutable `ID` cannot be reassigned.

4. **Execution & Inventory Management (`interpreter.py`)**:
   - Evaluates boolean expressions with short-circuiting.
   - Filters, sorts (`ASC` / `DESC`), projects, and limits rows.
   - Enforces inventory checks during purchases, preventing out-of-stock transactions.

