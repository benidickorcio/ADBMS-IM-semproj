from database import get_connection


def add_product(name, price, quantity):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO products (name, price, quantity) VALUES (%s, %s, %s)",
        (name, price, quantity),
    )
    product_id = cursor.lastrowid
    conn.commit()
    cursor.close()
    conn.close()
    return product_id


def delete_product(product_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE product_id=%s", (product_id,))
    conn.commit()
    rowcount = cursor.rowcount
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
    return rows


def update_product(product_id, name=None, price=None, quantity=None):
    fields = []
    values = []

    if name is not None:
        fields.append("name=%s")
        values.append(name)
    if price is not None:
        fields.append("price=%s")
        values.append(price)
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
    """Calculate total inventory value"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT SUM(quantity * price) AS total_value FROM products")
        result = cursor.fetchone()
        total_value = float(result[0]) if result[0] else 0.0
    except Exception as e:
        print(f"Error calculating total inventory value: {e}")
        total_value = 0.0
    finally:
        cursor.close()
        conn.close()
    return total_value
