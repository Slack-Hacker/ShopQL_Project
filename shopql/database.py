"""
ShopQL Database & Product Catalog
Stores, persists, and manages products and inventory levels.
"""

from typing import List, Dict, Any, Optional
import json
import os
import copy
from .errors import ExecutionError


DEFAULT_SEED_PRODUCTS = [
    {
        "id": 1,
        "name": "MacBook Pro 16",
        "price": 2499.00,
        "category": "ELECTRONICS",
        "stock": 14,
        "rating": 4.9,
        "description": "Apple M3 Pro 16-inch Retina display laptop with 36GB unified memory."
    },
    {
        "id": 2,
        "name": "Dell XPS 15",
        "price": 1850.00,
        "category": "ELECTRONICS",
        "stock": 8,
        "rating": 4.7,
        "description": "Premium Windows ultrabook with 4K OLED touch display and Intel i9."
    },
    {
        "id": 3,
        "name": "Wireless Noise Cancelling Headphones",
        "price": 349.99,
        "category": "ELECTRONICS",
        "stock": 42,
        "rating": 4.8,
        "description": "Industry leading noise canceling with 30-hour battery life."
    },
    {
        "id": 4,
        "name": "Ultra-Wide Gaming Monitor 34-inch",
        "price": 799.00,
        "category": "ELECTRONICS",
        "stock": 12,
        "rating": 4.6,
        "description": "Curved 144Hz 1ms IPS gaming display with HDR600."
    },
    {
        "id": 5,
        "name": "Ergonomic Mechanical Keyboard",
        "price": 189.50,
        "category": "ACCESSORIES",
        "stock": 25,
        "rating": 4.7,
        "description": "Customizable RGB split mechanical keyboard with hot-swappable switches."
    },
    {
        "id": 6,
        "name": "Precision Wireless Mouse",
        "price": 99.00,
        "category": "ACCESSORIES",
        "stock": 50,
        "rating": 4.6,
        "description": "Ergonomic master series mouse with ultra-fast scrolling."
    },
    {
        "id": 7,
        "name": "Designing Data-Intensive Applications",
        "price": 45.00,
        "category": "BOOKS",
        "stock": 100,
        "rating": 4.9,
        "description": "The definitive handbook by Martin Kleppmann on distributed systems and storage."
    },
    {
        "id": 8,
        "name": "Clean Code",
        "price": 38.50,
        "category": "BOOKS",
        "stock": 65,
        "rating": 4.5,
        "description": "A handbook of agile software craftsmanship by Robert C. Martin."
    },
    {
        "id": 9,
        "name": "Modern Espresso Machine",
        "price": 699.00,
        "category": "HOME",
        "stock": 6,
        "rating": 4.8,
        "description": "15-bar Italian pump stainless steel espresso and cappuccino maker."
    },
    {
        "id": 10,
        "name": "Smart HEPA Air Purifier",
        "price": 199.99,
        "category": "HOME",
        "stock": 18,
        "rating": 4.4,
        "description": "Captures 99.97% of airborne particles with WiFi app control."
    },
    {
        "id": 11,
        "name": "USB-C 10-in-1 Multiport Hub",
        "price": 59.99,
        "category": "ACCESSORIES",
        "stock": 0,  # Out of stock example for inventory queries!
        "rating": 4.3,
        "description": "Compact hub featuring dual 4K HDMI, Gigabit Ethernet, and 100W PD."
    },
    {
        "id": 12,
        "name": "Budget Smartphone 5G",
        "price": 299.00,
        "category": "ELECTRONICS",
        "stock": 35,
        "rating": 4.2,
        "description": "Affordable 5G smartphone with 120Hz AMOLED and 5000mAh battery."
    }
]


class Database:
    def __init__(self, persistence_file: Optional[str] = None):
        self.persistence_file = persistence_file
        self.products: List[Dict[str, Any]] = []
        self._next_id = 1
        self._audit_log: List[str] = []
        
        if persistence_file and os.path.exists(persistence_file):
            self.load()
        else:
            self.reset_to_seed()

    def reset_to_seed(self):
        """Reset products to the default seed inventory."""
        self.products = copy.deepcopy(DEFAULT_SEED_PRODUCTS)
        self._next_id = max(p["id"] for p in self.products) + 1 if self.products else 1
        self.log("Database reset to default seed catalog.")
        self.save()

    def log(self, message: str):
        self._audit_log.append(message)

    def get_audit_log(self) -> List[str]:
        return list(self._audit_log)

    def save(self):
        if self.persistence_file:
            try:
                with open(self.persistence_file, "w", encoding="utf-8") as f:
                    json.dump({"products": self.products, "next_id": self._next_id}, f, indent=2)
            except Exception:
                pass

    def load(self):
        if self.persistence_file and os.path.exists(self.persistence_file):
            try:
                with open(self.persistence_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.products = data.get("products", [])
                    self._next_id = data.get("next_id", len(self.products) + 1)
            except Exception:
                self.reset_to_seed()

    def get_all(self) -> List[Dict[str, Any]]:
        return [copy.deepcopy(p) for p in self.products]

    def find_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        norm = name.strip().lower()
        for p in self.products:
            if p["name"].strip().lower() == norm:
                return p
        return None

    def find_by_id(self, product_id: int) -> Optional[Dict[str, Any]]:
        for p in self.products:
            if p["id"] == product_id:
                return p
        return None

    def add_product(self, name: str, price: float, category: str = "GENERAL", stock: int = 1, rating: float = 5.0, description: str = "") -> Dict[str, Any]:
        existing = self.find_by_name(name)
        if existing:
            # If already exists, increment stock and update price
            existing["stock"] += stock
            existing["price"] = price
            self.log(f"Product '{name}' already exists. Restocked +{stock} units (New total: {existing['stock']}).")
            self.save()
            return copy.deepcopy(existing)

        new_prod = {
            "id": self._next_id,
            "name": name,
            "price": round(float(price), 2),
            "category": category.upper(),
            "stock": int(stock),
            "rating": round(float(rating), 2),
            "description": description or f"{name} ({category.upper()})"
        }
        self._next_id += 1
        self.products.append(new_prod)
        self.log(f"Added product #{new_prod['id']} '{name}' (Price: {price}, Stock: {stock}).")
        self.save()
        return copy.deepcopy(new_prod)

    def update_product(self, product_id: int, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        prod = self.find_by_id(product_id)
        if not prod:
            return None
        for k, v in updates.items():
            key = k.lower()
            if key in prod and key != "id":
                if key == "category":
                    prod[key] = str(v).upper()
                elif key in ("price", "rating"):
                    prod[key] = round(float(v), 2)
                elif key == "stock":
                    prod[key] = int(v)
                else:
                    prod[key] = v
        self.log(f"Updated product #{product_id} '{prod['name']}'.")
        self.save()
        return copy.deepcopy(prod)

    def delete_product(self, product_id: int) -> bool:
        initial_len = len(self.products)
        self.products = [p for p in self.products if p["id"] != product_id]
        if len(self.products) < initial_len:
            self.log(f"Deleted product #{product_id}.")
            self.save()
            return True
        return False

    def restock(self, name: str, quantity: int) -> Dict[str, Any]:
        prod = self.find_by_name(name)
        if not prod:
            raise ExecutionError(f"Product '{name}' not found in catalog to restock.", suggestion="Use 'ADD PRODUCT' to add new products.")
        prod["stock"] += quantity
        self.log(f"Restocked '{name}' by {quantity} units. Current stock: {prod['stock']}.")
        self.save()
        return copy.deepcopy(prod)

    def purchase(self, name: str, quantity: int) -> Dict[str, Any]:
        prod = self.find_by_name(name)
        if not prod:
            raise ExecutionError(f"Product '{name}' not found in catalog.", suggestion="Search available products with 'FIND PRODUCTS;'")
        if prod["stock"] < quantity:
            raise ExecutionError(
                f"Insufficient stock for '{name}'. Requested: {quantity}, Available: {prod['stock']}",
                suggestion=f"Available stock is {prod['stock']}. Restock using: RESTOCK PRODUCT \"{name}\" QUANTITY 10;"
            )
        prod["stock"] -= quantity
        self.log(f"Purchased {quantity} units of '{name}'. Remaining stock: {prod['stock']}.")
        self.save()
        return copy.deepcopy(prod)

    def get_categories(self) -> List[str]:
        return sorted(list(set(p["category"] for p in self.products)))

