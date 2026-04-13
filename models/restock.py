from database import get_connection
from models.product import add_stock


def restock_product(product_id, quantity, unit_cost):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO restock (product_id, quantity, unit_cost) VALUES (%s, %s, %s)",
            (product_id, quantity, unit_cost),
        )
        restock_id = cursor.lastrowid

        add_stock(product_id, quantity, cursor=cursor, conn=conn)

        conn.commit()
        return restock_id
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def get_all_restock():
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM v_restock_history")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def get_restock_by_id(restock_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM restock WHERE restock_id = %s", (restock_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row


def update_restock(restock_id, quantity, unit_cost):
    conn = get_connection()
    cursor = conn.cursor()
    # Get old values
    cursor.execute("SELECT product_id, quantity FROM restock WHERE restock_id = %s", (restock_id,))
    old = cursor.fetchone()
    if not old:
        raise ValueError("Restock not found")
    old_product_id, old_quantity = old
    # Calculate difference
    qty_diff = quantity - old_quantity
    # Update restock
    cursor.execute("UPDATE restock SET quantity = %s, unit_cost = %s WHERE restock_id = %s", (quantity, unit_cost, restock_id))
    # Update inventory
    from models.product import add_stock
    add_stock(old_product_id, qty_diff, cursor=cursor, conn=conn)
    conn.commit()
    cursor.close()
    conn.close()


def delete_restock(restock_id):
    conn = get_connection()
    cursor = conn.cursor()
    # Get values
    cursor.execute("SELECT product_id, quantity FROM restock WHERE restock_id = %s", (restock_id,))
    row = cursor.fetchone()
    if not row:
        raise ValueError("Restock not found")
    product_id, quantity = row
    # Delete restock
    cursor.execute("DELETE FROM restock WHERE restock_id = %s", (restock_id,))
    # Update inventory (subtract)
    from models.product import add_stock
    add_stock(product_id, -quantity, cursor=cursor, conn=conn)
    conn.commit()
    cursor.close()
    conn.close()


def get_total_restock_cost():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(quantity * unit_cost) AS total_cost FROM restock")
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result[0] if result[0] else 0.0