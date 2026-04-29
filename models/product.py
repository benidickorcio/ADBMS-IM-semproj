from database import get_connection


def add_product(name, total_price=0.0, quantity=0, cost_price=0.0, profit=None):
    if profit is None:
        profit = float(total_price) - float(cost_price)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO products (name, cost_price, profit, total_price, quantity) VALUES (%s, %s, %s, %s, %s)",
        (name, cost_price, profit, total_price, quantity),
    )
    product_id = cursor.lastrowid
    conn.commit()
    cursor.close()
    conn.close()
    return product_id


def delete_product(product_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # First get all sale_ids that contain this product
        cursor.execute(
            "SELECT DISTINCT sale_id FROM sold_items WHERE product_id = %s",
            (product_id,)
        )
        sale_ids = [row[0] for row in cursor.fetchall()]
        
        # Delete related sold_items
        cursor.execute("DELETE FROM sold_items WHERE product_id=%s", (product_id,))
        
        # Delete related restock history
        cursor.execute("DELETE FROM restock WHERE product_id=%s", (product_id,))
        
        # Delete sales that had this product (only if no other products)
        for sale_id in sale_ids:
            cursor.execute(
                "SELECT COUNT(*) FROM sold_items WHERE sale_id = %s",
                (sale_id,)
            )
            count = cursor.fetchone()[0]
            if count == 0:
                cursor.execute("DELETE FROM sales WHERE sales_id = %s", (sale_id,))
        
        # Now delete the product
        cursor.execute("DELETE FROM products WHERE product_id=%s", (product_id,))
        conn.commit()
        rowcount = cursor.rowcount
    except Exception as e:
        conn.rollback()
        print(f"Error deleting product: {e}")
        rowcount = 0
    finally:
        cursor.close()
        conn.close()
    return rowcount


def view_products():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM products ORDER BY product_id")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    for row in rows:
        if 'price' not in row:
            row['price'] = row.get('total_price', 0.0)
    return rows


def update_product(product_id, name=None, cost_price=None, profit=None, total_price=None, quantity=None):
    fields = []
    values = []

    if name is not None:
        fields.append("name=%s")
        values.append(name)
    if cost_price is not None:
        fields.append("cost_price=%s")
        values.append(cost_price)
    if profit is not None:
        fields.append("profit=%s")
        values.append(profit)
    if total_price is not None:
        fields.append("total_price=%s")
        values.append(total_price)
    if quantity is not None:
        fields.append("quantity=%s")
        values.append(quantity)

    if not fields:
        return 0

    values.append(product_id)
    sql = "UPDATE products SET " + ", ".join(fields) + " WHERE product_id=%s"

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql, tuple(values))
    conn.commit()
    rowcount = cursor.rowcount
    cursor.close()
    conn.close()
    return rowcount


def get_product_by_id(product_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM products WHERE product_id=%s", (product_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if row is not None and 'price' not in row:
        row['price'] = row.get('total_price', 0.0)
    return row


def get_stock(product_id):
    product = get_product_by_id(product_id)
    return product["quantity"] if product else None


def deduct_sale(product_id, quantity, cursor=None, conn=None):
    """Deduct quantity from product stock. Can use existing cursor/connection or create new ones."""
    if cursor is None or conn is None:
        # Create new connection if not provided
        product = get_product_by_id(product_id)
        if not product:
            raise ValueError("Product not found")
        new_qty = max(0, product["quantity"] - quantity)
        return update_product(product_id, quantity=new_qty)
    else:
        # Use provided cursor and connection
        try:
            cursor.execute("SELECT quantity FROM products WHERE product_id=%s", (product_id,))
            result = cursor.fetchone()
            if not result:
                raise ValueError(f"Product {product_id} not found")
            
            current_qty = result[0]
            new_qty = max(0, current_qty - quantity)
            
            cursor.execute(
                "UPDATE products SET quantity=%s WHERE product_id=%s",
                (new_qty, product_id)
            )
            return 1
        except Exception as e:
            raise ValueError(f"Error deducting sale for product {product_id}: {str(e)}")


def add_stock(product_id, quantity, cursor=None, conn=None):
    if cursor is not None and conn is not None:
        cursor.execute("SELECT quantity FROM products WHERE product_id=%s", (product_id,))
        result = cursor.fetchone()
        if not result:
            raise ValueError("Product not found")
        current_qty = result[0]
        new_qty = current_qty + quantity
        cursor.execute(
            "UPDATE products SET quantity=%s WHERE product_id=%s",
            (new_qty, product_id)
        )
        return 1

    product = get_product_by_id(product_id)
    if not product:
        raise ValueError("Product not found")

    new_qty = product["quantity"] + quantity
    return update_product(product_id, quantity=new_qty)


def get_all_inventory():
    return view_products()


def get_total_inventory_value():
    """Calculate total inventory value using the latest restock unit cost or stored pricing."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT SUM(
                p.quantity * (
                    CASE
                        WHEN latest.unit_cost IS NOT NULL AND latest.unit_cost > 0 THEN latest.unit_cost + COALESCE(p.profit, 0)
                        ELSE COALESCE(NULLIF(p.total_price, 0), COALESCE(p.cost_price, 0) + COALESCE(p.profit, 0))
                    END
                )
            ) AS total_value
            FROM products p
            LEFT JOIN (
                SELECT r.product_id, r.unit_cost
                FROM restock r
                JOIN (
                    SELECT product_id, MAX(restock_id) AS max_id
                    FROM restock
                    GROUP BY product_id
                ) mx ON r.product_id = mx.product_id AND r.restock_id = mx.max_id
            ) latest ON p.product_id = latest.product_id
            """
        )
        result = cursor.fetchone()
        total_value = float(result[0]) if result and result[0] is not None else 0.0
    except Exception as e:
        print(f"Error calculating total inventory value: {e}")
        total_value = 0.0
    finally:
        cursor.close()
        conn.close()
    return total_value
