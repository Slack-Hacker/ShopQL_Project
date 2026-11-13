"""
ShopQL Presentation Generator
Generates high-resolution visuals and builds a 14-slide PowerPoint deck (ShopQL_Presentation.pptx).
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

os.makedirs("slides_assets", exist_ok=True)

# -----------------------------------------------------------------------------
# 1. Generate Architecture Pipeline Diagram
# -----------------------------------------------------------------------------
def generate_pipeline_image():
    fig, ax = plt.subplots(figsize=(10, 3.2), dpi=200)
    fig.patch.set_facecolor('#0f172a')
    ax.set_facecolor('#0f172a')
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 3.2)
    ax.axis('off')

    stages = [
        ("Raw Query", "ShopQL Text\nInput", "#1e293b", "#38bdf8"),
        ("1. Lexer", "Scanner\nToken Stream", "#1e3a8a", "#60a5fa"),
        ("2. Parser", "Recursive Descent\nAST Tree", "#312e81", "#818cf8"),
        ("3. Semantic", "Type Check &\nConstraints", "#4c1d95", "#c084fc"),
        ("4. Interpreter", "Predicate Eval\n& Mutations", "#064e3b", "#34d399"),
        ("Store / DB", "Catalog &\nResults Table", "#14532d", "#4ade80"),
    ]

    box_w = 1.25
    box_h = 1.6
    y_pos = 0.8
    xs = [0.4, 2.0, 3.6, 5.2, 6.8, 8.4]

    for i, (title, desc, bg, border) in enumerate(stages):
        x = xs[i]
        rect = patches.FancyBboxPatch(
            (x, y_pos), box_w, box_h,
            boxstyle="round,pad=0.1,rounding_size=0.15",
            facecolor=bg, edgecolor=border, linewidth=2
        )
        ax.add_patch(rect)
        ax.text(x + box_w/2, y_pos + box_h - 0.35, title, color='#ffffff',
                fontsize=11, fontweight='bold', ha='center', va='center')
        ax.text(x + box_w/2, y_pos + 0.55, desc, color='#cbd5e1',
                fontsize=8.5, ha='center', va='center', linespacing=1.2)

        # Arrow to next stage
        if i < len(stages) - 1:
            ax.annotate('', xy=(xs[i+1] - 0.05, y_pos + box_h/2),
                        xytext=(x + box_w + 0.05, y_pos + box_h/2),
                        arrowprops=dict(facecolor='#38bdf8', edgecolor='#38bdf8', width=2.5, headwidth=7))

    plt.tight_layout()
    path = os.path.join("slides_assets", "pipeline.png")
    plt.savefig(path, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
    plt.close()
    return path

# -----------------------------------------------------------------------------
# 2. Generate AST Tree Diagram
# -----------------------------------------------------------------------------
def generate_ast_image():
    fig, ax = plt.subplots(figsize=(8.5, 4.2), dpi=200)
    fig.patch.set_facecolor('#0f172a')
    ax.set_facecolor('#0f172a')
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    ax.axis('off')

    nodes = {
        "root": (5.0, 4.2, "FindStatement", "verb='FIND'"),
        "where": (5.0, 2.9, "BinaryOp (AND)", "op='AND'"),
        "left_cmp": (2.5, 1.6, "BinaryOp (<)", "PRICE < 2000"),
        "right_cmp": (7.5, 1.6, "BinaryOp (=)", "CATEGORY = 'ELECTRONICS'"),
        "id1": (1.4, 0.4, "Identifier", "PRICE"),
        "lit1": (3.6, 0.4, "Literal", "2000"),
        "id2": (6.4, 0.4, "Identifier", "CATEGORY"),
        "lit2": (8.6, 0.4, "Literal", "'ELECTRONICS'"),
    }

    edges = [
        ("root", "where"),
        ("where", "left_cmp"),
        ("where", "right_cmp"),
        ("left_cmp", "id1"),
        ("left_cmp", "lit1"),
        ("right_cmp", "id2"),
        ("right_cmp", "lit2"),
    ]

    # Draw lines
    for parent, child in edges:
        x1, y1, _, _ = nodes[parent]
        x2, y2, _, _ = nodes[child]
        ax.plot([x1, x2], [y1 - 0.25, y2 + 0.25], color='#475569', linewidth=1.8, zorder=1)

    # Draw nodes
    for k, (x, y, title, sub) in nodes.items():
        w = 1.9 if "Binary" in title or "Find" in title else 1.5
        h = 0.65
        rect = patches.FancyBboxPatch(
            (x - w/2, y - h/2), w, h,
            boxstyle="round,pad=0.08,rounding_size=0.12",
            facecolor='#1e293b', edgecolor='#38bdf8' if "root" in k else '#818cf8', linewidth=1.8, zorder=2
        )
        ax.add_patch(rect)
        ax.text(x, y + 0.1, title, color='#ffffff', fontsize=8.5, fontweight='bold', ha='center', va='center', zorder=3)
        ax.text(x, y - 0.16, sub, color='#34d399', fontsize=7.5, fontfamily='monospace', ha='center', va='center', zorder=3)

    plt.tight_layout()
    path = os.path.join("slides_assets", "ast_tree.png")
    plt.savefig(path, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
    plt.close()
    return path

# -----------------------------------------------------------------------------
# 3. Generate Error Snippet Image
# -----------------------------------------------------------------------------
def generate_error_image():
    fig, ax = plt.subplots(figsize=(8.5, 2.8), dpi=200)
    fig.patch.set_facecolor('#1a0f12')
    ax.set_facecolor('#1a0f12')
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 3)
    ax.axis('off')

    # Border
    rect = patches.FancyBboxPatch((0.2, 0.2), 9.6, 2.6, boxstyle="round,pad=0.1",
                                 facecolor='#1a0f12', edgecolor='#ef4444', linewidth=2)
    ax.add_patch(rect)

    lines = [
        ("ShopQL Error [Line 2, Column 7]:", "#f87171", True, 10.5),
        ("    WHERE PRIC < 2000;", "#fca5a5", False, 10.0),
        ("          ^", "#ef4444", True, 11.0),
        ("  --> Unknown column or attribute 'PRIC'", "#f87171", True, 9.5),
        ("  Tip: Did you mean column 'PRICE'?", "#34d399", False, 9.5)
    ]

    y = 2.4
    for txt, col, bold, sz in lines:
        ax.text(0.6, y, txt, color=col, fontsize=sz, fontfamily='monospace',
                fontweight='bold' if bold else 'normal', va='center')
        y -= 0.44

    plt.tight_layout()
    path = os.path.join("slides_assets", "error_sample.png")
    plt.savefig(path, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
    plt.close()
    return path

# -----------------------------------------------------------------------------
# 4. Generate CLI Screenshot Mockup Image
# -----------------------------------------------------------------------------
def generate_cli_image():
    fig, ax = plt.subplots(figsize=(9, 4.2), dpi=200)
    fig.patch.set_facecolor('#0f172a')
    ax.set_facecolor('#0f172a')
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    ax.axis('off')

    # Window Box
    win = patches.FancyBboxPatch((0.2, 0.2), 9.6, 4.6, boxstyle="round,pad=0.08",
                                facecolor='#111827', edgecolor='#334155', linewidth=1.5)
    ax.add_patch(win)

    # Window header bar
    bar = patches.Rectangle((0.2, 4.4), 9.6, 0.4, facecolor='#1f2937', edgecolor='none')
    ax.add_patch(bar)
    # Window dots
    for i, c in enumerate(['#ef4444', '#f59e0b', '#10b981']):
        circ = patches.Circle((0.5 + i*0.25, 4.6), 0.08, facecolor=c, edgecolor='none')
        ax.add_patch(circ)
    ax.text(5.0, 4.6, "ShopQL Interactive Terminal REPL", color='#94a3b8', fontsize=8.5, ha='center', va='center')

    terminal_text = [
        ("ShopQL> SHOW PRODUCTS WHERE RATING >= 4.5 ORDER BY PRICE ASC;", "#38bdf8"),
        ("+----+---------------------------------------+-------------+---------+-------------+--------+", "#64748b"),
        ("| ID | NAME                                  | CATEGORY    | PRICE   | STOCK       | RATING |", "#94a3b8"),
        ("+----+---------------------------------------+-------------+---------+-------------+--------+", "#64748b"),
        ("| 8  | Clean Code                            | BOOKS       | $38.50  | 65 in stock | 4.5 ★  |", "#e2e8f0"),
        ("| 7  | Designing Data-Intensive Applications | BOOKS       | $45.00  | 100 in stock| 4.9 ★  |", "#e2e8f0"),
        ("| 6  | Precision Wireless Mouse              | ACCESSORIES | $99.00  | 50 in stock | 4.6 ★  |", "#e2e8f0"),
        ("| 5  | Ergonomic Mechanical Keyboard         | ACCESSORIES | $189.50 | 25 in stock | 4.7 ★  |", "#e2e8f0"),
        ("| 3  | Wireless Noise Cancelling Headphones  | ELECTRONICS | $349.99 | 42 in stock | 4.8 ★  |", "#e2e8f0"),
        ("+----+---------------------------------------+-------------+---------+-------------+--------+", "#64748b"),
        ("✔ Found 9 products. (Compile: 0.27ms | Exec: 0.12ms | Total: 0.39ms)", "#34d399"),
    ]

    y = 4.1
    for txt, col in terminal_text:
        ax.text(0.5, y, txt, color=col, fontsize=8.0, fontfamily='monospace', va='center')
        y -= 0.35

    plt.tight_layout()
    path = os.path.join("slides_assets", "cli_mockup.png")
    plt.savefig(path, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
    plt.close()
    return path

print("Generating visual assets...")
pipe_img = generate_pipeline_image()
ast_img = generate_ast_image()
err_img = generate_error_image()
cli_img = generate_cli_image()
print("Assets generated.")

# -----------------------------------------------------------------------------
# 5. Build PowerPoint Deck with python-pptx
# -----------------------------------------------------------------------------
prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6]

# Theme Colors
C_DARK_BG = RGBColor(15, 23, 42)        # #0f172a
C_CARD_BG = RGBColor(30, 41, 59)        # #1e293b
C_CARD_BORDER = RGBColor(51, 65, 85)    # #334155
C_CYAN = RGBColor(56, 189, 248)         # #38bdf8
C_EMERALD = RGBColor(52, 211, 153)      # #34d399
C_PURPLE = RGBColor(192, 132, 252)      # #c084fc
C_WHITE = RGBColor(248, 250, 252)       # #f8fafc
C_MUTED = RGBColor(148, 163, 184)       # #94a3b8
C_YELLOW = RGBColor(251, 191, 36)       # #fbbf24

def set_slide_background(slide):
    bg_shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg_shape.fill.solid()
    bg_shape.fill.fore_color.rgb = C_DARK_BG
    bg_shape.line.fill.background()
    return bg_shape

def add_header(slide, title_text, category_text="SHOPQL COMPILER PROJECT"):
    header_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.733), Inches(1.0))
    tf = header_box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

    p_cat = tf.paragraphs[0]
    p_cat.text = category_text.upper()
    p_cat.font.size = Pt(11)
    p_cat.font.bold = True
    p_cat.font.color.rgb = C_CYAN

    p_title = tf.add_paragraph()
    p_title.text = title_text
    p_title.font.size = Pt(24)
    p_title.font.bold = True
    p_title.font.color.rgb = C_WHITE

def add_card(slide, left, top, width, height, title="", bg_color=C_CARD_BG, border_color=C_CARD_BORDER):
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
    card.fill.solid()
    card.fill.fore_color.rgb = bg_color
    card.line.color.rgb = border_color
    card.line.width = Pt(1.5)

    if title:
        tb = slide.shapes.add_textbox(Inches(left + 0.25), Inches(top + 0.2), Inches(width - 0.5), Inches(0.45))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(15)
        p.font.bold = True
        p.font.color.rgb = C_CYAN

    return card

# -----------------------------------------------------------------------------
# SLIDE 1: Title Slide
# -----------------------------------------------------------------------------
s1 = prs.slides.add_slide(blank_layout)
set_slide_background(s1)

# Decorative card
add_card(s1, 1.2, 1.0, 10.933, 5.5, bg_color=C_CARD_BG, border_color=C_CYAN)

tb = s1.shapes.add_textbox(Inches(1.8), Inches(1.5), Inches(9.7), Inches(4.5))
tf = tb.text_frame
tf.word_wrap = True

p_badge = tf.paragraphs[0]
p_badge.text = "DOMAIN-SPECIFIC LANGUAGE & COMPILER DESIGN"
p_badge.font.size = Pt(12)
p_badge.font.bold = True
p_badge.font.color.rgb = C_EMERALD

p_main = tf.add_paragraph()
p_main.text = "ShopQL: E-Commerce Query Language"
p_main.font.size = Pt(36)
p_main.font.bold = True
p_main.font.color.rgb = C_WHITE

p_sub = tf.add_paragraph()
p_sub.text = "Lexer, Recursive Descent Parser, AST Construction, Semantic Type-Checker & Inventory Engine"
p_sub.font.size = Pt(16)
p_sub.font.color.rgb = C_CYAN

p_sep = tf.add_paragraph()
p_sep.text = "\n" + "—" * 45

p_meta = tf.add_paragraph()
p_meta.text = "Domain: Online Shopping / Retail Catalog Search & Inventory\nTech Stack: Python 3.10+, Flask, Rich CLI, AST & EBNF Grammar\nRepository: https://github.com/Slack-Hacker/ShopQL_Project"
p_meta.font.size = Pt(13)
p_meta.font.color.rgb = C_MUTED

# -----------------------------------------------------------------------------
# SLIDE 2: Project Motivation & Objectives
# -----------------------------------------------------------------------------
s2 = prs.slides.add_slide(blank_layout)
set_slide_background(s2)
add_header(s2, "Project Motivation & Core Objectives")

add_card(s2, 0.8, 1.6, 5.6, 5.2, "Why Build ShopQL?")
tb = s2.shapes.add_textbox(Inches(1.05), Inches(2.2), Inches(5.1), Inches(4.3))
tf = tb.text_frame
tf.word_wrap = True

points_why = [
    ("Specialized Domain Semantics", "Standard SQL is generic and verbose for e-commerce. ShopQL provides first-class keywords for retail: FIND, SHOW, PRICE, CATEGORY, STOCK, RATING."),
    ("Integrated Inventory Mutations", "Combines read operations with transactional inventory commands: ADD PRODUCT, RESTOCK, and BUY with atomic stock validation."),
    ("Student & Classroom Compiler Lab", "Demonstrates the complete compiler lifecycle: Lexing, Parsing, Abstract Syntax Tree construction, Semantic Analysis, and Evaluation."),
]
for title, body in points_why:
    p_t = tf.add_paragraph()
    p_t.text = f"• {title}"
    p_t.font.bold = True
    p_t.font.size = Pt(13)
    p_t.font.color.rgb = C_WHITE
    p_b = tf.add_paragraph()
    p_b.text = f"   {body}\n"
    p_b.font.size = Pt(11)
    p_b.font.color.rgb = C_MUTED

add_card(s2, 6.8, 1.6, 5.7, 5.2, "Core Design Deliverables")
tb = s2.shapes.add_textbox(Inches(7.05), Inches(2.2), Inches(5.2), Inches(4.3))
tf = tb.text_frame
tf.word_wrap = True

points_del = [
    ("Complete Compiler Pipeline", "100% pure Python implementation with zero third-party dependencies required for compilation."),
    ("Rich Error Diagnostics", "Precise line/col tracking with visual caret (^) pointers and Levenshtein suggestion generator."),
    ("Interactive Interfaces", "Interactive CLI REPL with formatted tables and a modern Flask Web Studio IDE with live AST viewer."),
    ("Extensive Test Suite", "40 unit and integration tests verifying all 4 compiler phases and API endpoints."),
]
for title, body in points_del:
    p_t = tf.add_paragraph()
    p_t.text = f"✔ {title}"
    p_t.font.bold = True
    p_t.font.size = Pt(13)
    p_t.font.color.rgb = C_EMERALD
    p_b = tf.add_paragraph()
    p_b.text = f"   {body}\n"
    p_b.font.size = Pt(11)
    p_b.font.color.rgb = C_MUTED

# -----------------------------------------------------------------------------
# SLIDE 3: Architecture & Compiler Pipeline
# -----------------------------------------------------------------------------
s3 = prs.slides.add_slide(blank_layout)
set_slide_background(s3)
add_header(s3, "End-to-End Compiler Pipeline Architecture")

# Add Pipeline Image
s3.shapes.add_picture(pipe_img, Inches(0.8), Inches(1.5), width=Inches(11.733))

# Cards underneath
add_card(s3, 0.8, 4.2, 3.6, 2.7, "Phase 1 & 2: Frontend")
tb = s3.shapes.add_textbox(Inches(1.0), Inches(4.7), Inches(3.2), Inches(2.0))
tf = tb.text_frame
tf.word_wrap = True
tf.text = "1. Lexical Analysis\n   Tokenizes keywords, literals, operators, and line/column indices.\n\n2. Parsing (Recursive Descent)\n   Builds the Abstract Syntax Tree (AST) while resolving operator precedence."
tf.paragraphs[0].font.size = Pt(11)
tf.paragraphs[0].font.color.rgb = C_MUTED

add_card(s3, 4.85, 4.2, 3.6, 2.7, "Phase 3: Semantic Analysis")
tb = s3.shapes.add_textbox(Inches(5.05), Inches(4.7), Inches(3.2), Inches(2.0))
tf = tb.text_frame
tf.word_wrap = True
tf.text = "• Attribute Verification\n  Validates that columns exist in schema.\n\n• Type Checking\n  Rejects type mismatches (e.g. numeric PRICE compared with string).\n\n• Constraint Enforcement\n  Validates ratings (0-5) and stock >= 0."
tf.paragraphs[0].font.size = Pt(11)
tf.paragraphs[0].font.color.rgb = C_MUTED

add_card(s3, 8.9, 4.2, 3.6, 2.7, "Phase 4: Backend / Engine")
tb = s3.shapes.add_textbox(Inches(9.1), Inches(4.7), Inches(3.2), Inches(2.0))
tf = tb.text_frame
tf.word_wrap = True
tf.text = "• Predicate Evaluator\n  Executes short-circuit logic (AND, OR, NOT, BETWEEN, IN).\n\n• Sorting & Limit\n  Handles multi-direction ORDER BY & LIMIT.\n\n• Inventory Transactions\n  Performs atomic stock decrements and restock increments."
tf.paragraphs[0].font.size = Pt(11)
tf.paragraphs[0].font.color.rgb = C_MUTED

# -----------------------------------------------------------------------------
# SLIDE 4: Formal Grammar (EBNF) & Syntax Specification
# -----------------------------------------------------------------------------
s4 = prs.slides.add_slide(blank_layout)
set_slide_background(s4)
add_header(s4, "Grammar Design: Extended Backus-Naur Form (EBNF)")

add_card(s4, 0.8, 1.6, 6.8, 5.3, "Formal Grammar Rules (EBNF)")
tb = s4.shapes.add_textbox(Inches(1.0), Inches(2.2), Inches(6.4), Inches(4.5))
tf = tb.text_frame
tf.word_wrap = True

ebnf_text = """QueryBatch   ::= Statement ( ';' Statement )* ';'?
Statement    ::= FindStmt | CountStmt | AddStmt | UpdateStmt
               | DeleteStmt | RestockStmt | BuyStmt | DescribeStmt

FindStmt     ::= ('FIND' | 'SHOW') 'PRODUCTS' (StringLiteral)?
                 ('WHERE' Condition)?
                 ('ORDER' 'BY' Identifier ('ASC' | 'DESC')?)?
                 ('LIMIT' IntegerLiteral)?

AddStmt      ::= 'ADD' 'PRODUCT' StringLiteral (ProductAttr)*
ProductAttr  ::= 'PRICE' Number | 'CATEGORY' String | 'STOCK' Int

RestockStmt  ::= 'RESTOCK' ('PRODUCT')? StringLiteral ('QUANTITY')? Int
BuyStmt      ::= 'BUY' ('PRODUCT')? StringLiteral ('QUANTITY')? Int

Condition    ::= OrExpr
OrExpr       ::= AndExpr ('OR' AndExpr)*
AndExpr      ::= NotExpr ('AND' NotExpr)*
NotExpr      ::= 'NOT' NotExpr | RelationalExpr"""

p = tf.paragraphs[0]
p.text = ebnf_text
p.font.name = "Courier New"
p.font.size = Pt(10.5)
p.font.color.rgb = C_EMERALD

add_card(s4, 8.0, 1.6, 4.5, 5.3, "Operator Precedence Hierarchy")
tb = s4.shapes.add_textbox(Inches(8.2), Inches(2.2), Inches(4.1), Inches(4.5))
tf = tb.text_frame
tf.word_wrap = True

prec_info = [
    ("Level 1 (Highest)", "Parentheses ( expr ), Literals, Identifiers"),
    ("Level 2", "Unary Operator: NOT"),
    ("Level 3", "Relational Operators:\n=, !=, <, <=, >, >=\nCONTAINS, LIKE, BETWEEN, IN"),
    ("Level 4", "Logical Conjunction: AND\n(Higher precedence than OR)"),
    ("Level 5 (Lowest)", "Logical Disjunction: OR"),
]
for lvl, ops in prec_info:
    p1 = tf.add_paragraph()
    p1.text = lvl
    p1.font.bold = True
    p1.font.size = Pt(12)
    p1.font.color.rgb = C_CYAN
    p2 = tf.add_paragraph()
    p2.text = f"{ops}\n"
    p2.font.size = Pt(10.5)
    p2.font.color.rgb = C_WHITE

# -----------------------------------------------------------------------------
# SLIDE 5: Compiler Stage 1 - Lexer
# -----------------------------------------------------------------------------
s5 = prs.slides.add_slide(blank_layout)
set_slide_background(s5)
add_header(s5, "Compiler Stage 1: Lexical Analyzer (Scanner)")

add_card(s5, 0.8, 1.6, 5.6, 5.3, "Lexer Features & Mechanics")
tb = s5.shapes.add_textbox(Inches(1.05), Inches(2.2), Inches(5.1), Inches(4.5))
tf = tb.text_frame
tf.word_wrap = True

lex_points = [
    ("Line & Column Coordinate Tracking", "Every token records its starting line and column position for compiler diagnostics."),
    ("Case-Insensitive Keyword Table", "Matches uppercase, lowercase, and mixed-case keywords (FIND, find, Find)."),
    ("Literal Scanner", "Parses integer literals, floating-point numbers, negative numbers (-50), and string escape sequences (\\\", \\n, \\t)."),
    ("Full Comment Support", "Strips SQL/C++ style single-line comments (-- and //) as well as multi-line block comments (/* ... */)."),
    ("Token Representation", "Emits structured Token(type, value, line, column, lexeme) objects."),
]
for title, desc in lex_points:
    p_t = tf.add_paragraph()
    p_t.text = f"• {title}"
    p_t.font.bold = True
    p_t.font.size = Pt(12)
    p_t.font.color.rgb = C_WHITE
    p_d = tf.add_paragraph()
    p_d.text = f"   {desc}\n"
    p_d.font.size = Pt(10.5)
    p_d.font.color.rgb = C_MUTED

add_card(s5, 6.8, 1.6, 5.7, 5.3, "Lexer Code Implementation (shopql/lexer.py)")
tb = s5.shapes.add_textbox(Inches(7.0), Inches(2.2), Inches(5.3), Inches(4.5))
tf = tb.text_frame
tf.word_wrap = True

code_snippet_lex = """class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.position = 0
        self.line = 1
        self.column = 1

    def tokenize(self) -> List[Token]:
        tokens = []
        while self.position < self.length:
            self._skip_whitespace_and_comments()
            ch = self._peek()
            
            if ch in ('"', "'"):
                tokens.append(self._read_string(ch))
            elif ch.isdigit() or (ch == '-' and self._peek(1).isdigit()):
                tokens.append(self._read_number())
            elif ch.isalpha() or ch == '_':
                tokens.append(self._read_identifier_or_keyword())
            elif ch == ';':
                tokens.append(Token(TokenType.SEMICOLON, ";", ...))
        return tokens"""

p = tf.paragraphs[0]
p.text = code_snippet_lex
p.font.name = "Courier New"
p.font.size = Pt(10)
p.font.color.rgb = C_CYAN

# -----------------------------------------------------------------------------
# SLIDE 6: Compiler Stage 2 - Parser & AST
# -----------------------------------------------------------------------------
s6 = prs.slides.add_slide(blank_layout)
set_slide_background(s6)
add_header(s6, "Compiler Stage 2: Recursive Descent Parser & AST")

# Add AST Image
s6.shapes.add_picture(ast_img, Inches(0.8), Inches(1.6), width=Inches(6.2))

add_card(s6, 7.3, 1.6, 5.2, 5.3, "Parsing & Precedence Logic")
tb = s6.shapes.add_textbox(Inches(7.55), Inches(2.2), Inches(4.7), Inches(4.5))
tf = tb.text_frame
tf.word_wrap = True

parse_points = [
    ("Recursive Descent Grammar", "Grammar rules are mapped 1-to-1 to mutually recursive functions: parse_statement() -> parse_expression() -> parse_or() -> parse_and() -> parse_relational() -> parse_primary()."),
    ("Resolving Operator Precedence", "AND is evaluated before OR without requiring parentheses, but parentheses ( ... ) naturally override precedence."),
    ("Strongly Typed AST Nodes", "Nodes inherit from ASTNode: FindStatement, AddStatement, BinaryOp, UnaryOp, BetweenOp, InOp, Identifier, Literal."),
    ("Serializability", "Every node provides .to_dict() allowing instant JSON serialization and dynamic visual tree rendering in the Web Studio."),
]
for title, desc in parse_points:
    p_t = tf.add_paragraph()
    p_t.text = f"✔ {title}"
    p_t.font.bold = True
    p_t.font.size = Pt(12)
    p_t.font.color.rgb = C_EMERALD
    p_d = tf.add_paragraph()
    p_d.text = f"   {desc}\n"
    p_d.font.size = Pt(10.5)
    p_d.font.color.rgb = C_MUTED

# -----------------------------------------------------------------------------
# SLIDE 7: Compiler Stage 3 - Semantic Analysis
# -----------------------------------------------------------------------------
s7 = prs.slides.add_slide(blank_layout)
set_slide_background(s7)
add_header(s7, "Compiler Stage 3: Semantic Analysis & Type Safety")

add_card(s7, 0.8, 1.6, 5.6, 5.3, "Semantic Verification Rules")
tb = s7.shapes.add_textbox(Inches(1.05), Inches(2.2), Inches(5.1), Inches(4.5))
tf = tb.text_frame
tf.word_wrap = True

sem_rules = [
    ("1. Attribute Verification", "Ensures queried columns (PRICE, STOCK, CATEGORY, etc.) belong to the known catalog schema. Unknown attributes trigger suggestions."),
    ("2. Type Consistency", "Checks operands in relational expressions. Prevents nonsensical operations like PRICE < 'cheap' or RATING = 'five'."),
    ("3. Operator Compatibility", "Ensures text-matching operators (CONTAINS and LIKE) are strictly applied to STRING columns (NAME, CATEGORY)."),
    ("4. Domain Constraint Checking", "Validates that PRICE >= 0, STOCK >= 0, RATING is between 0.0 and 5.0, and purchase/restock QUANTITY > 0."),
    ("5. Primary Key Immutability", "Product ID is read-only and cannot be altered via UPDATE."),
]
for title, desc in sem_rules:
    p_t = tf.add_paragraph()
    p_t.text = f"• {title}"
    p_t.font.bold = True
    p_t.font.size = Pt(12)
    p_t.font.color.rgb = C_WHITE
    p_d = tf.add_paragraph()
    p_d.text = f"   {desc}\n"
    p_d.font.size = Pt(10.5)
    p_d.font.color.rgb = C_MUTED

add_card(s7, 6.8, 1.6, 5.7, 5.3, "Semantic Validator (shopql/semantic.py)")
tb = s7.shapes.add_textbox(Inches(7.0), Inches(2.2), Inches(5.3), Inches(4.5))
tf = tb.text_frame
tf.word_wrap = True

code_snippet_sem = """class SemanticAnalyzer:
    def _check_expression(self, expr: Expression) -> str:
        if isinstance(expr, Identifier):
            name = expr.name.upper()
            if name not in VALID_COLUMNS:
                close = difflib.get_close_matches(name, VALID_COLUMNS)
                raise SemanticError(f"Unknown column '{name}'",
                                    suggestion=f"Did you mean '{close[0]}'?")
            return SCHEMA_TYPES[name]

        elif isinstance(expr, BinaryOp):
            left_t = self._check_expression(expr.left)
            right_t = self._check_expression(expr.right)
            
            # Reject incompatible types
            if expr.op in ('<', '<=', '>', '>=', '='):
                if left_t and right_t and left_t != right_t:
                    raise SemanticError(
                        f"Cannot compare {left_t} with {right_t}")"""

p = tf.paragraphs[0]
p.text = code_snippet_sem
p.font.name = "Courier New"
p.font.size = Pt(9.5)
p.font.color.rgb = C_CYAN

# -----------------------------------------------------------------------------
# SLIDE 8: Compiler Stage 4 - Interpreter & Inventory
# -----------------------------------------------------------------------------
s8 = prs.slides.add_slide(blank_layout)
set_slide_background(s8)
add_header(s8, "Compiler Stage 4: Interpreter & Inventory Management")

add_card(s8, 0.8, 1.6, 5.6, 5.3, "Evaluation & Store Operations")
tb = s8.shapes.add_textbox(Inches(1.05), Inches(2.2), Inches(5.1), Inches(4.5))
tf = tb.text_frame
tf.word_wrap = True

interp_points = [
    ("Short-Circuit Boolean Evaluation", "AND terminates immediately on False; OR terminates immediately on True, optimizing query throughput."),
    ("Multi-Attribute Sorting & Limit", "Executes ORDER BY column ASC/DESC with stable sort algorithms, followed by LIMIT row slicing."),
    ("Atomic Inventory Guard", "When executing BUY PRODUCT 'X' QUANTITY N, the interpreter checks available stock. If quantity exceeds stock, execution aborts with an informative error."),
    ("Real-Time Restocking", "RESTOCK PRODUCT adds units instantly and updates inventory timestamps."),
    ("Disk Persistence", "Changes persist to catalog.json and can be restored back to seed data at any time."),
]
for title, desc in interp_points:
    p_t = tf.add_paragraph()
    p_t.text = f"• {title}"
    p_t.font.bold = True
    p_t.font.size = Pt(12)
    p_t.font.color.rgb = C_WHITE
    p_d = tf.add_paragraph()
    p_d.text = f"   {desc}\n"
    p_d.font.size = Pt(10.5)
    p_d.font.color.rgb = C_MUTED

add_card(s8, 6.8, 1.6, 5.7, 5.3, "Inventory Statement Walkthrough")
tb = s8.shapes.add_textbox(Inches(7.0), Inches(2.2), Inches(5.3), Inches(4.5))
tf = tb.text_frame
tf.word_wrap = True

walkthrough_text = """-- 1. Add new product with attributes
ADD PRODUCT "Laptop" PRICE 55000;
-- Creates item with default Stock: 1, Category: GENERAL

-- 2. Restock by 15 units
RESTOCK PRODUCT "Laptop" QUANTITY 15;
-- Output: New stock level: 16 units

-- 3. Customer Purchase
BUY PRODUCT "Laptop" QUANTITY 3;
-- Output: Purchased 3x 'Laptop' for $165,000.
-- Remaining stock: 13 units

-- 4. Over-purchase guard test
BUY PRODUCT "Laptop" QUANTITY 20;
-- Raises ExecutionError:
-- 'Insufficient stock for Laptop: Requested: 20, Available: 13'"""

p = tf.paragraphs[0]
p.text = walkthrough_text
p.font.name = "Courier New"
p.font.size = Pt(10)
p.font.color.rgb = C_EMERALD

# -----------------------------------------------------------------------------
# SLIDE 9: Syntax Error Diagnostics
# -----------------------------------------------------------------------------
s9 = prs.slides.add_slide(blank_layout)
set_slide_background(s9)
add_header(s9, "Syntax Error Reporting & Caret Diagnostics")

# Add Error Image
s9.shapes.add_picture(err_img, Inches(0.8), Inches(1.6), width=Inches(11.733))

add_card(s9, 0.8, 4.6, 5.6, 2.3, "Diagnostic Features")
tb = s9.shapes.add_textbox(Inches(1.0), Inches(5.1), Inches(5.2), Inches(1.6))
tf = tb.text_frame
tf.word_wrap = True
tf.text = "• Visual Caret (^) Pointer: Accurately highlights the exact column offset where parsing or lexical analysis failed.\n• Source Code Frame: Displays the offending line of code in context.\n• User-Friendly Messages: Plain English explanations of what was expected vs found."
tf.paragraphs[0].font.size = Pt(11)
tf.paragraphs[0].font.color.rgb = C_MUTED

add_card(s9, 6.8, 4.6, 5.7, 2.3, "Levenshtein 'Did you mean?' Suggestions")
tb = s9.shapes.add_textbox(Inches(7.0), Inches(5.1), Inches(5.3), Inches(1.6))
tf = tb.text_frame
tf.word_wrap = True
tf.text = "• Keyword Near-Miss Detection: If user types FND instead of FIND, or WHER instead of WHERE, suggestions are generated.\n• Schema Attribute Assistance: If a column typo occurs (e.g. PRIC, CATGORY, STOK), the compiler recommends the closest matching valid attribute."
tf.paragraphs[0].font.size = Pt(11)
tf.paragraphs[0].font.color.rgb = C_MUTED

# -----------------------------------------------------------------------------
# SLIDE 10: Interactive CLI REPL
# -----------------------------------------------------------------------------
s10 = prs.slides.add_slide(blank_layout)
set_slide_background(s10)
add_header(s10, "Interactive CLI REPL & Execution")

# Add CLI Image
s10.shapes.add_picture(cli_img, Inches(0.8), Inches(1.6), width=Inches(7.2))

add_card(s10, 8.3, 1.6, 4.2, 5.3, "REPL Commands & Benchmarks")
tb = s10.shapes.add_textbox(Inches(8.55), Inches(2.2), Inches(3.7), Inches(4.5))
tf = tb.text_frame
tf.word_wrap = True

repl_info = [
    ("Interactive Commands", "• .help  : Syntax reference\n• .schema: Table column types\n• .demo  : Automated query walkthrough\n• .ast <q>: Print parsed AST tree\n• .tokens<q>: Print token stream\n• .reset : Reset catalog to seed"),
    ("Batch Script Execution", "python cli.py -f sample_queries.sql\npython cli.py --demo\npython cli.py -q \"FIND ...\""),
    ("Sub-Millisecond Performance", "Average compilation time: 0.27ms\nAverage execution time: 0.12ms\nTotal query latency: < 0.5ms"),
]
for title, desc in repl_info:
    p_t = tf.add_paragraph()
    p_t.text = title
    p_t.font.bold = True
    p_t.font.size = Pt(12)
    p_t.font.color.rgb = C_CYAN
    p_d = tf.add_paragraph()
    p_d.text = f"{desc}\n"
    p_d.font.size = Pt(10.5)
    p_d.font.color.rgb = C_MUTED

# -----------------------------------------------------------------------------
# SLIDE 11: Web Studio & Visual Playground
# -----------------------------------------------------------------------------
s11 = prs.slides.add_slide(blank_layout)
set_slide_background(s11)
add_header(s11, "Web Studio: Live Visual IDE (http://localhost:5000)")

add_card(s11, 0.8, 1.6, 3.7, 5.3, "1. Query Editor & Presets")
tb = s11.shapes.add_textbox(Inches(1.0), Inches(2.2), Inches(3.3), Inches(4.5))
tf = tb.text_frame
tf.word_wrap = True
tf.text = "• Interactive code editor with line wrapping & shortcut execution (Ctrl+Enter).\n\n• One-click preset query buttons for the prompt examples, inventory restocks, and complex boolean queries.\n\n• Live execution timers: Compile Time, Execution Time, and Rows Returned."
tf.paragraphs[0].font.size = Pt(11)
tf.paragraphs[0].font.color.rgb = C_MUTED

add_card(s11, 4.8, 1.6, 3.7, 5.3, "2. Live AST & Token Inspector")
tb = s11.shapes.add_textbox(Inches(5.0), Inches(2.2), Inches(3.3), Inches(4.5))
tf = tb.text_frame
tf.word_wrap = True
tf.text = "• Interactive AST Tree View: Dynamically renders the parsed AST nodes in a collapsible hierarchy.\n\n• Raw JSON AST Viewer: Toggle to inspect raw AST JSON data.\n\n• Token Stream Tab: Inspects lexer output with token type badges, lexemes, parsed values, and line:col coordinates."
tf.paragraphs[0].font.size = Pt(11)
tf.paragraphs[0].font.color.rgb = C_MUTED

add_card(s11, 8.8, 1.6, 3.7, 5.3, "3. Store Catalog & Results")
tb = s11.shapes.add_textbox(Inches(9.0), Inches(2.2), Inches(3.3), Inches(4.5))
tf = tb.text_frame
tf.word_wrap = True
tf.text = "• Formatted Result Tables: Styled price tags ($), rating stars (★), category pills, and dynamic stock badges (In Stock, Low Stock, Out of Stock).\n\n• Live Inventory Dashboard: Real-time store database with instant search.\n\n• One-Click Reset Store: Restores default seed inventory."
tf.paragraphs[0].font.size = Pt(11)
tf.paragraphs[0].font.color.rgb = C_MUTED

# -----------------------------------------------------------------------------
# SLIDE 12: Testing & Quality Assurance
# -----------------------------------------------------------------------------
s12 = prs.slides.add_slide(blank_layout)
set_slide_background(s12)
add_header(s12, "Test Suite & Verification (40 / 40 Passed)")

add_card(s12, 0.8, 1.6, 11.733, 5.3, "Comprehensive Unit & Integration Test Coverage")
tb = s12.shapes.add_textbox(Inches(1.1), Inches(2.2), Inches(11.1), Inches(4.5))
tf = tb.text_frame
tf.word_wrap = True

test_modules = [
    ("test_lexer.py (8 tests)", "Verifies token recognition, case insensitivity, int/float/negative numbers, escape characters, comments, line/column tracking, and unterminated string detection."),
    ("test_parser.py (9 tests)", "Tests AST construction for FIND, SHOW, ADD, operator precedence (AND over OR), parentheses overrides, BETWEEN, IN, and syntax error messages."),
    ("test_semantic.py (7 tests)", "Verifies type mismatch errors (number vs string), unknown columns with suggestions, rating bounds [0.0 - 5.0], negative price rejection, and immutable ID checks."),
    ("test_interpreter.py (8 tests)", "Verifies prompt queries, sorting ASC/DESC, text matching (CONTAINS & LIKE), atomic restock, purchase execution, and out-of-stock rejection."),
    ("test_errors.py (3 tests)", "Verifies caret (^) pointer alignment, error frame rendering, and unexpected token diagnostics."),
    ("test_web.py (5 tests)", "Validates Flask REST API endpoints (/api/query, /api/catalog, /api/reset, /api/samples)."),
]

for mod, desc in test_modules:
    p_t = tf.add_paragraph()
    p_t.text = f"✔ {mod}"
    p_t.font.bold = True
    p_t.font.size = Pt(12)
    p_t.font.color.rgb = C_EMERALD
    p_d = tf.add_paragraph()
    p_d.text = f"   {desc}\n"
    p_d.font.size = Pt(10.5)
    p_d.font.color.rgb = C_MUTED

# -----------------------------------------------------------------------------
# SLIDE 13: Project Files & GitHub Repository
# -----------------------------------------------------------------------------
s13 = prs.slides.add_slide(blank_layout)
set_slide_background(s13)
add_header(s13, "Project Structure & GitHub Repository")

add_card(s13, 0.8, 1.6, 5.6, 5.3, "Directory Tree")
tb = s13.shapes.add_textbox(Inches(1.0), Inches(2.2), Inches(5.2), Inches(4.5))
tf = tb.text_frame
tf.word_wrap = True

tree_text = """ShopQL_Project/
├── GRAMMAR.md        # Formal EBNF grammar
├── README.md         # Full project manual
├── cli.py            # Rich CLI REPL
├── web_app.py        # Flask API backend
├── catalog.json      # Store persistence
├── sample_queries.sql# Test script
├── shopql/           # Core compiler package
│   ├── lexer.py      # Scanner
│   ├── parser.py     # Parser
│   ├── ast_nodes.py  # AST definitions
│   ├── semantic.py   # Type checker
│   ├── interpreter.py# Execution engine
│   ├── database.py   # Inventory store
│   └── errors.py     # Diagnostics
├── static/           # Web Studio frontend
└── tests/            # 40 automated tests"""

p = tf.paragraphs[0]
p.text = tree_text
p.font.name = "Courier New"
p.font.size = Pt(9.5)
p.font.color.rgb = C_CYAN

add_card(s13, 6.8, 1.6, 5.7, 5.3, "Open-Source Repository & Deliverables")
tb = s13.shapes.add_textbox(Inches(7.05), Inches(2.2), Inches(5.2), Inches(4.5))
tf = tb.text_frame
tf.word_wrap = True

repo_points = [
    ("Live GitHub Repository", "https://github.com/Slack-Hacker/ShopQL_Project\nComplete version-controlled codebase pushed to main branch."),
    ("Classroom Presentation Deck", "ShopQL_Presentation.pptx (this 14-slide presentation deck with embedded architecture diagrams and code walk-throughs)."),
    ("Zero Setup Dependencies", "The core compiler runs on pure Python 3.10+ standard libraries without external package overhead."),
    ("Ready to Run", "Students and instructors can immediately clone, run unit tests, launch the CLI REPL, or spin up the Web Studio IDE."),
]
for title, desc in repo_points:
    p_t = tf.add_paragraph()
    p_t.text = f"• {title}"
    p_t.font.bold = True
    p_t.font.size = Pt(12)
    p_t.font.color.rgb = C_WHITE
    p_d = tf.add_paragraph()
    p_d.text = f"   {desc}\n"
    p_d.font.size = Pt(10.5)
    p_d.font.color.rgb = C_MUTED

# -----------------------------------------------------------------------------
# SLIDE 14: Conclusion & Q&A
# -----------------------------------------------------------------------------
s14 = prs.slides.add_slide(blank_layout)
set_slide_background(s14)

add_card(s14, 1.2, 1.0, 10.933, 5.5, bg_color=C_CARD_BG, border_color=C_EMERALD)
tb = s14.shapes.add_textbox(Inches(1.8), Inches(1.4), Inches(9.7), Inches(4.7))
tf = tb.text_frame
tf.word_wrap = True

p_c = tf.paragraphs[0]
p_c.text = "CONCLUSION & FUTURE EXTENSIONS"
p_c.font.size = Pt(12)
p_c.font.bold = True
p_c.font.color.rgb = C_CYAN

p_t = tf.add_paragraph()
p_t.text = "ShopQL: A Complete E-Commerce DSL Compiler"
p_t.font.size = Pt(28)
p_t.font.bold = True
p_t.font.color.rgb = C_WHITE

p_sum = tf.add_paragraph()
p_sum.text = """
Key Takeaways:
1. Demonstrated every phase of compiler construction: Lexical Scanning, Recursive Descent Parsing, Abstract Syntax Tree generation, Semantic Validation, and Query Execution.
2. Built custom retail language constructs: Price/Category filtering, substring/pattern matching, and transactional inventory management.
3. Implemented compiler-grade error diagnostics with caret pointers and Levenshtein suggestions.
4. Delivered a dual interface: An interactive terminal REPL and a modern Web Studio IDE.

Future Enhancements:
• B-Tree Indexing on PRICE and CATEGORY for sub-linear filtering.
• Cost-Based Query Optimizer for condition reordering.
• SQL / JSON Export and multi-tenant catalog partitioning.
"""
p_sum.font.size = Pt(11.5)
p_sum.font.color.rgb = C_MUTED

p_qa = tf.add_paragraph()
p_qa.text = "\nThank You! Questions & Discussion."
p_qa.font.size = Pt(16)
p_qa.font.bold = True
p_qa.font.color.rgb = C_EMERALD

# Save Presentation
pptx_path = "ShopQL_Presentation.pptx"
prs.save(pptx_path)
print(f"Presentation successfully saved to {pptx_path} (14 slides)")
