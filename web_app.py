"""
ShopQL Web Playground & Studio Server
Serves a modern, interactive web-based IDE for ShopQL with live query execution,
AST tree visualization, token inspection, and inventory management.
"""

import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

from shopql.engine import ShopQLEngine
from shopql.database import Database

app = Flask(__name__, static_folder="static", static_url_path="")
CORS(app)

# Use persistent catalog file for web studio
CATALOG_PATH = os.path.join(os.path.dirname(__file__), "catalog.json")
db = Database(persistence_file=CATALOG_PATH)
engine = ShopQLEngine(db=db)


SAMPLE_QUERIES = [
    {
        "id": "ex1",
        "title": "Example 1 (Prompt)",
        "desc": "Find products under $2000 in Electronics",
        "query": "FIND PRODUCTS\nWHERE PRICE < 2000\nAND CATEGORY = \"ELECTRONICS\";"
    },
    {
        "id": "ex2",
        "title": "Example 2 (Prompt)",
        "desc": "Show high-rated products sorted by price ascending",
        "query": "SHOW PRODUCTS\nWHERE RATING >= 4.5\nORDER BY PRICE ASC;"
    },
    {
        "id": "ex3",
        "title": "Example 3 (Prompt)",
        "desc": "Add a new Laptop with price 55,000",
        "query": "ADD PRODUCT \"Laptop\" PRICE 55000;"
    },
    {
        "id": "inventory",
        "title": "Purchase & Restock",
        "desc": "Buy units and restock inventory",
        "query": "BUY PRODUCT \"MacBook Pro 16\" QUANTITY 2;\nRESTOCK PRODUCT \"Precision Wireless Mouse\" QUANTITY 20;"
    },
    {
        "id": "advanced",
        "title": "Complex Filters",
        "desc": "Between, In, and parenthesized logical operators",
        "query": "FIND PRODUCTS\nWHERE (CATEGORY IN (\"ELECTRONICS\", \"BOOKS\") OR RATING >= 4.7)\nAND PRICE BETWEEN 40 AND 800\nORDER BY RATING DESC\nLIMIT 6;"
    },
    {
        "id": "schema",
        "title": "Inspect Schema",
        "desc": "Display table columns, data types, and constraints",
        "query": "DESCRIBE PRODUCTS;"
    }
]


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/query", methods=["POST"])
def run_query():
    data = request.get_json(force=True, silent=True) or {}
    query_str = data.get("query", "").strip()
    if not query_str:
        return jsonify({"success": False, "error": "Query string cannot be empty."}), 400

    res = engine.execute(query_str)
    return jsonify(res.to_dict())


@app.route("/api/catalog", methods=["GET"])
def get_catalog():
    return jsonify({
        "products": db.get_all(),
        "categories": db.get_categories(),
        "total": len(db.products)
    })


@app.route("/api/reset", methods=["POST"])
def reset_catalog():
    db.reset_to_seed()
    return jsonify({"success": True, "message": "Catalog restored to default seed products."})


@app.route("/api/samples", methods=["GET"])
def get_samples():
    return jsonify(SAMPLE_QUERIES)


if __name__ == "__main__":
    print("Starting ShopQL Web Studio on http://localhost:5000 ...")
    app.run(host="0.0.0.0", port=5000, debug=False)

