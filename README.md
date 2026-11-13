# ShopQL: E-Commerce Query Language & Compiler

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/tests-40%20passed-brightgreen.svg)]()
[![License](https://img.shields.io/badge/license-MIT-green.svg)]()

> A domain-specific query language (DSL) and compiler engine built for e-commerce catalog search, product filtering, multi-attribute sorting, and real-time inventory management.

---

## Table of Contents
1. [Overview](#overview)
2. [Example Syntax](#example-syntax)
3. [Features](#features)
4. [Compiler Concepts Implemented](#compiler-concepts-implemented)
5. [Syntax Error Diagnostics](#syntax-error-diagnostics)
6. [Project Structure](#project-structure)
7. [Quickstart Guide](#quickstart-guide)
   - [Interactive CLI REPL](#interactive-cli-repl)
   - [Web Studio & Visual Playground](#web-studio--visual-playground)
   - [Running the Test Suite](#running-the-test-suite)
8. [Language Grammar Reference](#language-grammar-reference)

---

## Overview

**ShopQL** is a custom declarative query language inspired by SQL. It simplifies product discovery and store operations by offering specialized constructs tailored to online retail: price range queries, category filters, text matching, and atomic inventory transactions (`BUY`, `RESTOCK`, `ADD`).

Under the hood, ShopQL implements a full compiler pipeline:
1. **Lexical Analyzer (Scanner)** with line & column tracking.
2. **Recursive Descent Parser** constructing an Abstract Syntax Tree (AST).
3. **Semantic Analyzer & Type Checker** validating schema constraints and types.
4. **Execution Engine (Interpreter)** handling predicate evaluation, sorting, limits, and inventory state transitions.

---

## Example Syntax

### 1. Product Search & Category Filtering
```sql
FIND PRODUCTS
WHERE PRICE < 2000
AND CATEGORY = "ELECTRONICS";
```

### 2. Rating Filtering with Product Sorting
```sql
SHOW PRODUCTS
WHERE RATING >= 4.5
ORDER BY PRICE ASC;
```

### 3. Adding New Products to Inventory
```sql
ADD PRODUCT "Laptop" PRICE 55000;
```

### 4. Inventory Restock & Purchases
```sql
-- Restock 20 additional units
RESTOCK PRODUCT "Laptop" QUANTITY 20;

-- Customer purchase with inventory guard
BUY PRODUCT "Laptop" QUANTITY 2;
```

### 5. Complex Boolean Predicates & Pattern Matching
```sql
FIND PRODUCTS
WHERE (CATEGORY IN ("ELECTRONICS", "ACCESSORIES") OR RATING > 4.7)
AND PRICE BETWEEN 50 AND 1000
AND NAME CONTAINS "Pro"
ORDER BY RATING DESC
LIMIT 5;
```

---

## Features

- **Product Searching**: Quick full-text search across titles and descriptions, substring matching with `CONTAINS`, and SQL wildcard matching with `LIKE` (e.g. `LIKE "ELEC%"`).
- **Price & Attribute Filtering**: Relational comparisons (`=`, `!=`, `<`, `<=`, `>`, `>=`) and range checks (`BETWEEN min AND max`).
- **Category Filtering**: Single equality checks (`CATEGORY = "ELECTRONICS"`) or set membership (`CATEGORY IN ("BOOKS", "HOME")`).
- **Product Sorting**: Multi-direction sorting (`ORDER BY PRICE ASC`, `ORDER BY RATING DESC`).
- **Real-Time Inventory Management**:
  - `ADD PRODUCT`: Creates items with custom or defaulted attributes (`PRICE`, `CATEGORY`, `STOCK`, `RATING`).
  - `RESTOCK PRODUCT`: Increases inventory levels.
  - `BUY / PURCHASE`: Decrements inventory with atomic out-of-stock validation.
  - `UPDATE PRODUCT`: Mutates prices, stock, or ratings.
  - `DELETE PRODUCT`: Removes items or clears zero-stock records.
- **Persistence & Seeding**: In-memory execution with optional disk persistence (`catalog.json`) and instant reset to seed catalog.

---

## Compiler Concepts Implemented

| Concept | Implementation in ShopQL |
|:---|:---|
| **Lexical Analysis** | [lexer.py](file:///c:/Users/abd98/OneDrive/Desktop/try/new/shopql/lexer.py) handles tokenization, string escape sequences (`\"`, `\n`), numeric literals (int/float/negative), single-line (`--`, `//`) and block (`/* */`) comments, maintaining exact line and column coordinates. |
| **Grammar Design** | Formal EBNF grammar specification detailed in [GRAMMAR.md](file:///c:/Users/abd98/OneDrive/Desktop/try/new/GRAMMAR.md). Clean operator precedence resolution. |
| **Recursive Descent Parsing** | [parser.py](file:///c:/Users/abd98/OneDrive/Desktop/try/new/shopql/parser.py) builds a strongly-typed Abstract Syntax Tree ([ast_nodes.py](file:///c:/Users/abd98/OneDrive/Desktop/try/new/shopql/ast_nodes.py)) with Pratt-style precedence handling. |
| **Operator Precedence** | Enforces: `Primary / ( )` > `NOT` > `Relational (=, !=, <, <=, >, >=, CONTAINS, LIKE, BETWEEN, IN)` > `AND` > `OR`. |
| **Semantic Analysis** | [semantic.py](file:///c:/Users/abd98/OneDrive/Desktop/try/new/shopql/semantic.py) verifies attributes exist in schema, type checks operands (e.g. rejects `PRICE < "cheap"`), validates bounds (rating 0.0–5.0), and enforces immutable ID fields. |
| **Syntax Error Reporting** | [errors.py](file:///c:/Users/abd98/OneDrive/Desktop/try/new/shopql/errors.py) outputs compiler diagnostics with line number, column number, code snippet with `^` pointer, and Levenshtein "Did you mean?" suggestions for misspelled keywords. |

---

## Syntax Error Diagnostics

When a syntax or semantic error occurs, ShopQL highlights the exact location with a caret pointer and helpful recommendations:

```
ShopQL Error [Line 2, Column 7]:
    WHERE PRIC < 2000
          ^
  --> Unknown column or attribute 'PRIC'
  Tip: Did you mean column 'PRICE'?
```

```
ShopQL Error [Line 1, Column 1]:
    FND PRODUCTS;
    ^
  --> Unexpected token 'FND'. Expected query command (FIND, SHOW, ADD, UPDATE, DELETE, RESTOCK, BUY, COUNT, DESCRIBE)
  Tip: Did you mean command 'FIND'?
```

---

## Project Structure

```
.
├── GRAMMAR.md                  # Formal EBNF specification & precedence tables
├── README.md                   # Main documentation & user guide
├── cli.py                      # Interactive REPL with formatted table output
├── sample_queries.sql          # Ready-to-run queries demonstrating all features
├── web_app.py                  # Flask Web Studio backend & API
├── catalog.json                # Seed / persistent inventory store
├── shopql/
│   ├── __init__.py             # Public package exports
│   ├── tokens.py               # TokenType enum and Token dataclass
│   ├── lexer.py                # Lexical scanner with line/col tracking
│   ├── ast_nodes.py            # AST node dataclasses
│   ├── parser.py               # Recursive descent parser with error recovery
│   ├── semantic.py             # Semantic analyzer & type checker
│   ├── database.py             # Product catalog & inventory manager
│   ├── interpreter.py          # Query executor & predicate evaluator
│   ├── errors.py               # Custom compiler exceptions & caret formatter
│   └── engine.py               # Unified compiler facade
├── static/
│   ├── index.html              # Modern Web Studio UI
│   ├── style.css               # Dark-mode developer IDE styling
│   └── app.js                  # Frontend client (AST visualizer, live tables)
└── tests/
    ├── test_lexer.py           # Scanner tests (tokens, escapes, comments, errors)
    ├── test_parser.py          # Parser & AST tests (precedence, clauses)
    ├── test_semantic.py        # Type checking & constraint tests
    ├── test_interpreter.py     # Execution & inventory management tests
    ├── test_errors.py          # Diagnostic caret pointer tests
    └── test_web.py             # Flask API endpoints test suite
```

---

## Quickstart Guide

### 1. Interactive CLI REPL

Launch the interactive REPL:
```bash
python cli.py
```

Inside the REPL, you can execute multi-line queries terminated by `;` or use meta-commands:
```
ShopQL> FIND PRODUCTS WHERE PRICE < 2000 AND CATEGORY = "ELECTRONICS";
ShopQL> .schema
ShopQL> .demo
ShopQL> .ast FIND PRODUCTS WHERE RATING >= 4.5;
ShopQL> .exit
```

You can also run automated demos or script files directly:
```bash
# Run guided interactive demo
python cli.py --demo

# Execute queries from a file
python cli.py -f sample_queries.sql

# Execute an inline query
python cli.py -q "FIND PRODUCTS WHERE PRICE < 500;"
```

---

### 2. Web Studio & Visual Playground

Start the local web server:
```bash
python web_app.py
```
Open **`http://localhost:5000`** in your browser. The Web Studio includes:
- **Interactive Query Editor** with syntax hints and one-click sample queries.
- **Results View** with colored price tags, category pills, star ratings, and inventory badges.
- **AST Tree Inspector** with collapsible visual hierarchy and raw JSON view.
- **Token Stream Inspector** showing all tokens emitted by the lexer.
- **Live Inventory Manager** with instant search and one-click reset.

---

### 3. Running the Test Suite

The test suite covers the lexer, parser, semantic analyzer, interpreter, and web APIs:
```bash
python -m unittest discover -s tests -v
```
Output:
```
Ran 40 tests in 0.15s
OK
```

---

## Language Grammar Reference

For the full EBNF grammar, lexical specification, and operator precedence hierarchy, refer to **[GRAMMAR.md](file:///c:/Users/abd98/OneDrive/Desktop/try/new/GRAMMAR.md)**.

