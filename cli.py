"""
ShopQL Interactive Command-Line Interface (REPL)
Allows users to execute ShopQL queries interactively or in batch mode with rich table formatting.
"""

import sys
import os
import argparse
import time
from typing import List, Optional

# Try importing rich for enhanced console rendering; fall back to standard formatting if needed
try:
    from rich.console import Console
    from rich.table import Table
    from rich.syntax import Syntax
    from rich.panel import Panel
    from rich.tree import Tree
    from rich import print as rprint
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

from shopql.engine import ShopQLEngine, EngineResult
from shopql.database import Database
from shopql.tokens import Token, TokenType
from shopql.ast_nodes import ASTNode, Statement


BANNER = r"""
========================================================================
   ____  _                 ____  _     
  / ___|| |__   ___  _ __ / __ \| |    
  \___ \| '_ \ / _ \| '_ \ |  | | |    
   ___) | | | | (_) | |_) | |__| | |___ 
  |____/|_| |_|\___/| .__/ \___\_\_____|
                    |_|                 
  ShopQL - E-Commerce Query Language & Compiler REPL
========================================================================
Type ShopQL queries ending with a semicolon (;).
Meta-commands:
  .help     - Show syntax guide and examples
  .schema   - Display table schema
  .demo     - Run guided demo queries
  .reset    - Reset product catalog to default seed
  .ast <q>  - Display parsed AST tree for query
  .tokens<q>- Display token stream for query
  .catalog  - Show all products currently in store
  .exit     - Exit REPL
========================================================================
"""


def format_ascii_table(columns: List[str], rows: List[dict]) -> str:
    if not rows:
        return "(0 rows returned)"
    
    # Calculate column widths
    widths = {c: len(c) for c in columns}
    for r in rows:
        for c in columns:
            val_str = str(r.get(c, ""))
            if len(val_str) > widths[c]:
                widths[c] = len(val_str)

    # Format header
    sep = "+" + "+".join(["-" * (widths[c] + 2) for c in columns]) + "+"
    header = "|" + "|".join([f" {c.upper():<{widths[c]}} " for c in columns]) + "|"
    lines = [sep, header, sep]

    for r in rows:
        row_str = "|" + "|".join([f" {str(r.get(c, '')):<{widths[c]}} " for c in columns]) + "|"
        lines.append(row_str)

    lines.append(sep)
    return "\n".join(lines)


def display_result(engine_res: EngineResult, console=None):
    if not engine_res.success:
        if HAS_RICH and console:
            console.print(Panel(f"[bold red]{engine_res.error}[/bold red]", title="Compilation / Execution Error", border_style="red"))
        else:
            print(f"\n{engine_res.error}\n")
        return

    for qr in engine_res.results:
        print()
        if qr.rows and qr.columns:
            if HAS_RICH and console:
                table = Table(title=f"{qr.statement_type} Results ({qr.count} row{'s' if qr.count != 1 else ''})", show_header=True, header_style="bold cyan")
                for c in qr.columns:
                    col_style = "green" if c in ("price", "stock") else "yellow" if c == "rating" else "white"
                    table.add_column(c.upper(), style=col_style)
                for r in qr.rows:
                    row_vals = []
                    for c in qr.columns:
                        v = r.get(c, "")
                        if c == "price":
                            row_vals.append(f"${float(v):.2f}" if v != "" else "")
                        elif c == "rating":
                            row_vals.append(f"{float(v):.1f} ★" if v != "" else "")
                        elif c == "stock":
                            row_vals.append(f"{v} in stock" if int(v) > 0 else "[bold red]OUT OF STOCK[/bold red]")
                        else:
                            row_vals.append(str(v))
                    table.add_row(*row_vals)
                console.print(table)
            else:
                print(format_ascii_table(qr.columns, qr.rows))

        if HAS_RICH and console:
            console.print(f"[bold green]✔[/bold green] {qr.message} [dim](Compile: {engine_res.compile_time_ms}ms | Exec: {qr.execution_time_ms}ms | Total: {engine_res.total_time_ms}ms)[/dim]")
        else:
            print(f"OK: {qr.message} (Compile: {engine_res.compile_time_ms}ms | Exec: {qr.execution_time_ms}ms)")
        print()


def render_ast_tree(node: ASTNode, tree=None):
    name = node.__class__.__name__
    props = {k: v for k, v in node.__dict__.items() if not isinstance(v, (ASTNode, list)) and k not in ("line", "column")}
    label = f"[bold cyan]{name}[/bold cyan] [dim]{props}[/dim]" if HAS_RICH else f"{name} {props}"
    
    if tree is None:
        if HAS_RICH:
            tree = Tree(label)
        else:
            print(label)
            return

    for k, v in node.__dict__.items():
        if isinstance(v, ASTNode):
            sub = tree.add(f"[yellow]{k}:[/yellow]" if HAS_RICH else f"{k}:")
            render_ast_tree(v, sub)
        elif isinstance(v, list) and v and isinstance(v[0], ASTNode):
            sub_list = tree.add(f"[yellow]{k}:[/yellow]" if HAS_RICH else f"{k}:")
            for item in v:
                render_ast_tree(item, sub_list)
    return tree


def run_demo(engine: ShopQLEngine, console=None):
    demo_queries = [
        ("-- 1. Search products under $2000 in Electronics (User Example 1)",
         "FIND PRODUCTS WHERE PRICE < 2000 AND CATEGORY = 'ELECTRONICS';"),
        ("-- 2. Show top-rated products sorted by price (User Example 2)",
         "SHOW PRODUCTS WHERE RATING >= 4.5 ORDER BY PRICE ASC;"),
        ("-- 3. Add a new product (User Example 3)",
         'ADD PRODUCT "Laptop" PRICE 55000;'),
        ("-- 4. Verify newly added Laptop",
         'FIND PRODUCTS WHERE NAME = "Laptop";'),
        ("-- 5. Restock inventory by 15 units",
         'RESTOCK PRODUCT "Laptop" QUANTITY 15;'),
        ("-- 6. Customer purchase 3 units",
         'BUY PRODUCT "Laptop" QUANTITY 3;'),
        ("-- 7. Complex filtering with parenthesized logic and BETWEEN",
         "FIND PRODUCTS WHERE (CATEGORY = 'ELECTRONICS' OR CATEGORY = 'BOOKS') AND PRICE BETWEEN 30 AND 500 ORDER BY RATING DESC;")
    ]

    for desc, q in demo_queries:
        if HAS_RICH and console:
            console.print(f"\n[bold magenta]{desc}[/bold magenta]")
            console.print(f"[bold white]> {q}[/bold white]")
        else:
            print(f"\n{desc}\n> {q}")
        res = engine.execute(q)
        display_result(res, console)
        time.sleep(0.3)


def print_help():
    help_text = """
ShopQL Language Syntax Reference:
------------------------------------------------------------------------
1. FIND & SHOW PRODUCTS:
   FIND PRODUCTS;
   FIND PRODUCTS WHERE PRICE < 2000 AND CATEGORY = "ELECTRONICS";
   SHOW PRODUCTS WHERE RATING >= 4.5 ORDER BY PRICE ASC;
   FIND PRODUCTS WHERE NAME CONTAINS "Pro" LIMIT 5;
   FIND PRODUCTS WHERE PRICE BETWEEN 100 AND 1000;
   FIND PRODUCTS WHERE CATEGORY IN ("ELECTRONICS", "ACCESSORIES");

2. ADD PRODUCT:
   ADD PRODUCT "Laptop" PRICE 55000;
   ADD PRODUCT "Phone" PRICE 45000 CATEGORY "ELECTRONICS" STOCK 20 RATING 4.7;

3. INVENTORY MANAGEMENT (BUY & RESTOCK):
   RESTOCK PRODUCT "Laptop" QUANTITY 10;
   BUY PRODUCT "Laptop" QUANTITY 2;

4. UPDATE & DELETE:
   UPDATE PRODUCT "Laptop" SET PRICE = 52000, STOCK = 15;
   DELETE PRODUCT "Laptop";
   DELETE PRODUCTS WHERE STOCK <= 0;

5. UTILITY & SCHEMA:
   COUNT PRODUCTS WHERE STOCK > 0;
   DESCRIBE PRODUCTS;
------------------------------------------------------------------------
"""
    print(help_text)


def repl(persistence_file: Optional[str] = "catalog.json"):
    console = Console() if HAS_RICH else None
    print(BANNER)
    
    db = Database(persistence_file=persistence_file)
    engine = ShopQLEngine(db=db)

    buffer = []

    while True:
        try:
            prompt = "ShopQL> " if not buffer else "   ... > "
            line = input(prompt)
        except (EOFError, KeyboardInterrupt):
            print("\nExiting ShopQL. Goodbye!")
            break

        stripped = line.strip()

        # Handle REPL meta-commands
        if not buffer and stripped.startswith("."):
            cmd = stripped.lower()
            if cmd in (".exit", ".quit"):
                print("Goodbye!")
                break
            elif cmd == ".help":
                print_help()
            elif cmd == ".schema":
                res = engine.execute("DESCRIBE PRODUCTS;")
                display_result(res, console)
            elif cmd == ".reset":
                db.reset_to_seed()
                print("Catalog reset to default seed products.")
            elif cmd in (".catalog", ".all"):
                res = engine.execute("FIND PRODUCTS;")
                display_result(res, console)
            elif cmd == ".demo":
                run_demo(engine, console)
            elif cmd.startswith(".ast "):
                query = stripped[5:].strip()
                res = engine.execute(query)
                if res.ast:
                    if HAS_RICH and console:
                        for s in res.ast:
                            t = render_ast_tree(s)
                            console.print(t)
                    else:
                        import pprint
                        for s in res.ast:
                            pprint.pprint(s.to_dict())
                else:
                    display_result(res, console)
            elif cmd.startswith(".tokens "):
                query = stripped[8:].strip()
                res = engine.execute(query)
                if res.tokens:
                    tok_data = [{"type": t.type.name, "value": t.value, "line": t.line, "col": t.column} for t in res.tokens]
                    print(format_ascii_table(["type", "value", "line", "col"], tok_data))
                else:
                    display_result(res, console)
            else:
                print(f"Unknown meta-command '{stripped}'. Type .help for assistance.")
            continue

        buffer.append(line)

        # Check if query ends with semicolon
        full_query = "\n".join(buffer).strip()
        if full_query.endswith(";"):
            res = engine.execute(full_query)
            display_result(res, console)
            buffer = []


def main():
    parser = argparse.ArgumentParser(description="ShopQL Compiler & REPL")
    parser.add_argument("-q", "--query", type=str, help="Single query to execute")
    parser.add_argument("-f", "--file", type=str, help="Script file containing ShopQL queries to execute")
    parser.add_argument("--demo", action="store_true", help="Run automated demo")
    parser.add_argument("--catalog", type=str, default="catalog.json", help="Path to JSON catalog file")

    args = parser.parse_args()
    engine = ShopQLEngine(persistence_file=args.catalog)
    console = Console() if HAS_RICH else None

    if args.demo:
        run_demo(engine, console)
        return

    if args.query:
        res = engine.execute(args.query)
        display_result(res, console)
        return

    if args.file:
        if not os.path.exists(args.file):
            print(f"Error: File '{args.file}' not found.")
            sys.exit(1)
        with open(args.file, "r", encoding="utf-8") as f:
            content = f.read()
        res = engine.execute(content)
        display_result(res, console)
        return

    # Default to interactive REPL
    repl(persistence_file=args.catalog)


if __name__ == "__main__":
    main()

