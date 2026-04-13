from database import get_connection
import mysql.connector


def get_all_customers():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM customers ORDER BY customer_id")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def get_customer_by_id(customer_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM customers WHERE customer_id=%s", (customer_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row


def search_customer(keyword):
    query = "%" + keyword + "%"
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM customers WHERE name LIKE %s OR contact_number LIKE %s OR address LIKE %s",
        (query, query, query),
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def add_customer(name, address, contact):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO customers (name, address, contact_number, current_balance) VALUES (%s, %s, %s, 0.00)",
        (name, address, contact),
    )
    c_id = cursor.lastrowid
    conn.commit()
    cursor.close()
    conn.close()
    return c_id


def update_customer(customer_id, name, address=None, contact_number=None, current_balance=None, conn=None):
    if not name:
        return 0

    # Use provided connection or create a new one
    own_conn = conn is None
    if own_conn:
        conn = get_connection()

    cursor = conn.cursor()

    if current_balance is None:
        existing_customer = get_customer_by_id(customer_id)
        current_balance = existing_customer["current_balance"] if existing_customer else 0.00

    cursor.callproc(
        "UpdateCustomer",
        (customer_id, name, address, contact_number, current_balance),
    )
    conn.commit()
    cursor.close()

    # Only close connection if we created it
    if own_conn:
        conn.close()

    return 1


def get_customer_balance(customer_id):
    customer = get_customer_by_id(customer_id)
    return float(customer["current_balance"]) if customer else None


def mark_customer_paid_balance(customer_id):
    customer = get_customer_by_id(customer_id)
    if not customer:
        return None

    balance = float(customer.get("current_balance", 0.0) or 0.0)
    if balance <= 0:
        return None

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE customers SET current_balance = 0.00 WHERE customer_id=%s",
            (customer_id,)
        )
        cursor.execute(
            "UPDATE sales SET status = 'PAID' WHERE customer_id=%s AND status != 'PAID'",
            (customer_id,)
        )
        cursor.execute(
            "INSERT INTO sales (customer_id, total_amount, payment_method, amount_paid, change_amount, status, created_by) VALUES (%s, %s, %s, %s, %s, 'PAID', NULL)",
            (customer_id, balance, 'BALANCE PAYMENT', balance, 0.00)
        )
        payment_sale_id = cursor.lastrowid
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Error marking customer as paid: {e}")
        payment_sale_id = None
    finally:
        cursor.close()
        conn.close()

    return payment_sale_id


def delete_customer(customer_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Remove sales history first to allow deleting the customer
        cursor.execute(
            "DELETE si FROM sold_items si JOIN sales s ON si.sale_id = s.sales_id WHERE s.customer_id = %s",
            (customer_id,)
        )
        cursor.execute("DELETE FROM sales WHERE customer_id=%s", (customer_id,))
        cursor.execute("DELETE FROM customers WHERE customer_id=%s", (customer_id,))
        conn.commit()
        rowcount = cursor.rowcount
    except mysql.connector.Error as e:
        conn.rollback()
        print(f"Error deleting customer and sales history: {e}")
        rowcount = 0
    finally:
        cursor.close()
        conn.close()
    return rowcount

