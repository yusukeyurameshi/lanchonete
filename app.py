from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, redirect, render_template, request, url_for

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "lanchonete.db"
SCHEMA_PATH = BASE_DIR / "schema.sql"

app = Flask(__name__)


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))


def row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return dict(row)


def get_cash_summary() -> tuple[float, float, float]:
    with get_connection() as conn:
        cash_summary = conn.execute(
            """
            SELECT
                COALESCE(SUM(CASE WHEN type='ENTRADA' THEN amount ELSE 0 END), 0) AS entradas,
                COALESCE(SUM(CASE WHEN type='SAIDA' THEN amount ELSE 0 END), 0) AS saidas
            FROM cash_movements
            """
        ).fetchone()
    entradas = float(cash_summary["entradas"])
    saidas = float(cash_summary["saidas"])
    return entradas, saidas, entradas - saidas


@app.get("/")
def index() -> str:
    with get_connection() as conn:
        products = conn.execute(
            "SELECT id, name, price, stock, created_at FROM products ORDER BY name"
        ).fetchall()
    entradas, saidas, saldo = get_cash_summary()
    return render_template(
        "index.html",
        products=products,
        entradas=entradas,
        saidas=saidas,
        saldo=saldo,
        active_page="inicio",
    )


@app.get("/pedidos")
def pedidos() -> str:
    with get_connection() as conn:
        products = conn.execute(
            "SELECT id, name, price, stock, created_at FROM products ORDER BY name"
        ).fetchall()
        orders = conn.execute(
            "SELECT id, status, total, created_at FROM orders ORDER BY id DESC LIMIT 30"
        ).fetchall()
    return render_template(
        "pedidos.html",
        products=products,
        orders=orders,
        active_page="pedidos",
    )


@app.post("/products")
def create_product():
    name = request.form.get("name", "").strip()
    price = request.form.get("price", "").strip()
    stock = request.form.get("stock", "").strip()

    if not name:
        return jsonify({"error": "Nome do produto e obrigatorio."}), 400

    try:
        price_value = float(price)
        stock_value = int(stock)
    except ValueError:
        return jsonify({"error": "Preco e estoque devem ser numericos."}), 400

    if price_value < 0 or stock_value < 0:
        return jsonify({"error": "Preco e estoque nao podem ser negativos."}), 400

    try:
        with get_connection() as conn:
            conn.execute(
                "INSERT INTO products (name, price, stock) VALUES (?, ?, ?)",
                (name, price_value, stock_value),
            )
    except sqlite3.IntegrityError:
        return jsonify({"error": "Produto ja existe."}), 409

    return redirect(url_for("pedidos"))


@app.post("/orders")
def create_order():
    product_id = request.form.get("product_id", "").strip()
    quantity = request.form.get("quantity", "").strip()

    try:
        product_id_value = int(product_id)
        quantity_value = int(quantity)
    except ValueError:
        return jsonify({"error": "Produto e quantidade devem ser inteiros."}), 400

    if quantity_value <= 0:
        return jsonify({"error": "Quantidade deve ser maior que zero."}), 400

    with get_connection() as conn:
        product = conn.execute(
            "SELECT id, name, price, stock FROM products WHERE id = ?",
            (product_id_value,),
        ).fetchone()

        if product is None:
            return jsonify({"error": "Produto nao encontrado."}), 404

        if product["stock"] < quantity_value:
            return jsonify({"error": "Estoque insuficiente."}), 400

        subtotal = float(product["price"]) * quantity_value
        cursor = conn.execute("INSERT INTO orders (status, total) VALUES ('ABERTO', 0)")
        order_id = cursor.lastrowid

        conn.execute(
            """
            INSERT INTO order_items (order_id, product_id, quantity, unit_price, subtotal)
            VALUES (?, ?, ?, ?, ?)
            """,
            (order_id, product["id"], quantity_value, float(product["price"]), subtotal),
        )
        conn.execute(
            "UPDATE orders SET total = ? WHERE id = ?",
            (subtotal, order_id),
        )
        conn.execute(
            "UPDATE products SET stock = stock - ? WHERE id = ?",
            (quantity_value, product["id"]),
        )

    return redirect(url_for("index"))


@app.post("/orders/cart")
def create_order_from_cart():
    raw_cart = request.form.get("cart_json", "").strip()
    if not raw_cart:
        return jsonify({"error": "Pedido vazio."}), 400

    try:
        cart = json.loads(raw_cart)
    except json.JSONDecodeError:
        return jsonify({"error": "Formato de pedido invalido."}), 400

    if not isinstance(cart, list) or not cart:
        return jsonify({"error": "Pedido vazio."}), 400

    normalized_items: list[tuple[int, int]] = []
    for item in cart:
        if not isinstance(item, dict):
            return jsonify({"error": "Item do pedido invalido."}), 400
        try:
            product_id = int(item.get("product_id"))
            quantity = int(item.get("quantity"))
        except (TypeError, ValueError):
            return jsonify({"error": "Produto e quantidade devem ser inteiros."}), 400
        if quantity <= 0:
            return jsonify({"error": "Quantidade deve ser maior que zero."}), 400
        normalized_items.append((product_id, quantity))

    totals_by_product: dict[int, int] = {}
    for product_id, quantity in normalized_items:
        totals_by_product[product_id] = totals_by_product.get(product_id, 0) + quantity

    with get_connection() as conn:
        placeholders = ",".join(["?"] * len(totals_by_product))
        products_rows = conn.execute(
            f"""
            SELECT id, name, price, stock
            FROM products
            WHERE id IN ({placeholders})
            """,
            tuple(totals_by_product.keys()),
        ).fetchall()

        products_by_id = {row["id"]: row for row in products_rows}
        if len(products_by_id) != len(totals_by_product):
            return jsonify({"error": "Um ou mais produtos nao foram encontrados."}), 404

        for product_id, quantity in totals_by_product.items():
            if products_by_id[product_id]["stock"] < quantity:
                product_name = products_by_id[product_id]["name"]
                return jsonify({"error": f"Estoque insuficiente para {product_name}."}), 400

        cursor = conn.execute("INSERT INTO orders (status, total) VALUES ('ABERTO', 0)")
        order_id = cursor.lastrowid
        order_total = 0.0

        for product_id, quantity in totals_by_product.items():
            product = products_by_id[product_id]
            unit_price = float(product["price"])
            subtotal = unit_price * quantity
            order_total += subtotal

            conn.execute(
                """
                INSERT INTO order_items (order_id, product_id, quantity, unit_price, subtotal)
                VALUES (?, ?, ?, ?, ?)
                """,
                (order_id, product_id, quantity, unit_price, subtotal),
            )
            conn.execute(
                "UPDATE products SET stock = stock - ? WHERE id = ?",
                (quantity, product_id),
            )

        conn.execute(
            "UPDATE orders SET total = ? WHERE id = ?",
            (order_total, order_id),
        )

    return redirect(url_for("pedidos"))


@app.post("/orders/<int:order_id>/close")
def close_order(order_id: int):
    with get_connection() as conn:
        order = conn.execute(
            "SELECT id, status, total FROM orders WHERE id = ?",
            (order_id,),
        ).fetchone()

        if order is None:
            return jsonify({"error": "Pedido nao encontrado."}), 404

        if order["status"] == "FECHADO":
            return redirect(url_for("pedidos"))

        conn.execute(
            "UPDATE orders SET status = 'FECHADO' WHERE id = ?",
            (order_id,),
        )
        conn.execute(
            """
            INSERT INTO cash_movements (type, amount, description)
            VALUES ('ENTRADA', ?, ?)
            """,
            (float(order["total"]), f"Fechamento do pedido #{order_id}"),
        )

    return redirect(url_for("pedidos"))


@app.post("/cash")
def create_cash_movement():
    movement_type = request.form.get("type", "").strip().upper()
    amount = request.form.get("amount", "").strip()
    description = request.form.get("description", "").strip()

    if movement_type not in {"ENTRADA", "SAIDA"}:
        return jsonify({"error": "Tipo deve ser ENTRADA ou SAIDA."}), 400

    try:
        amount_value = float(amount)
    except ValueError:
        return jsonify({"error": "Valor deve ser numerico."}), 400

    if amount_value <= 0:
        return jsonify({"error": "Valor deve ser maior que zero."}), 400

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO cash_movements (type, amount, description)
            VALUES (?, ?, ?)
            """,
            (movement_type, amount_value, description or None),
        )

    return redirect(url_for("index"))


@app.get("/api/products")
def list_products():
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, name, price, stock, created_at FROM products ORDER BY name"
        ).fetchall()
    return jsonify([row_to_dict(r) for r in rows])


@app.get("/api/orders")
def list_orders():
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, status, total, created_at FROM orders ORDER BY id DESC"
        ).fetchall()
    return jsonify([row_to_dict(r) for r in rows])


@app.get("/api/cash/summary")
def cash_summary():
    entradas, saidas, saldo = get_cash_summary()
    return jsonify(
        {
            "entradas": entradas,
            "saidas": saidas,
            "saldo": saldo,
        }
    )


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
