from database import get_connection
import mysql.connector


def get_all_customers():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM customers WHERE is_deleted = FALSE ORDER BY customer_id")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def get_customer_by_id(customer_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM customers WHERE customer_id=%s AND is_deleted = FALSE", (customer_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row


def search_customer(keyword):
    query = "%" + keyword + "%"
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM customers WHERE is_deleted = FALSE AND (name LIKE %s OR contact_number LIKE %s OR address LIKE %s)",
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
    """Backup customer to customers_backup table, then mark as deleted"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Get complete customer details before backing up
        cursor.execute(
            "SELECT customer_id, name, address, contact_number, current_balance FROM customers WHERE customer_id=%s AND is_deleted = FALSE",
            (customer_id,)
        )
        customer_data = cursor.fetchone()
        
        if not customer_data:
            return 0
        
        # Insert customer data into backup table
        cursor.execute(
            "INSERT INTO customers_backup (customer_id, name, address, contact_number, current_balance) VALUES (%s, %s, %s, %s, %s)",
            (customer_data[0], customer_data[1], customer_data[2], customer_data[3], customer_data[4])
        )
        
        # Mark customer as deleted (soft delete)
        cursor.execute(
            "UPDATE customers SET is_deleted = TRUE, deleted_at = NOW(), name = 'Unknown' WHERE customer_id=%s",
            (customer_id,)
        )
        conn.commit()
        rowcount = cursor.rowcount
    except Exception as e:
        conn.rollback()
        print(f"Error deleting and backing up customer: {e}")
        rowcount = 0
    finally:
        cursor.close()
        conn.close()
    return rowcount


def get_all_backup_customers():
    """Fetch all customers from the customers_backup table"""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM customers_backup ORDER BY customer_id")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def search_backup_customer(keyword):
    """Search customers in the customers_backup table"""
    query = "%" + keyword + "%"
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM customers_backup WHERE name LIKE %s OR contact_number LIKE %s OR address LIKE %s",
        (query, query, query),
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def restore_backup_customer(customer_id):
    """Restore a customer from backup to active customers table"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Get customer data from backup
        cursor.execute("SELECT * FROM customers_backup WHERE customer_id=%s", (customer_id,))
        customer_data = cursor.fetchone()
        
        if not customer_data:
            return False
        
        # Update the deleted customer record in active table to restore it
        # Note: customer_data indices: [0]=backup_id, [1]=customer_id, [2]=name, [3]=address, [4]=contact_number, [5]=current_balance
        cursor.execute(
            "UPDATE customers SET is_deleted=FALSE, deleted_at=NULL, name=%s, address=%s, contact_number=%s, current_balance=%s WHERE customer_id=%s",
            (customer_data[2], customer_data[3], customer_data[4], customer_data[5], customer_data[1])
        )
        
        # Delete from backup
        cursor.execute("DELETE FROM customers_backup WHERE customer_id=%s", (customer_id,))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Error restoring customer from backup: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def delete_backup_customer_permanently(customer_id):
    """Permanently delete a customer from the backup table"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM customers_backup WHERE customer_id=%s", (customer_id,))
        conn.commit()
        rowcount = cursor.rowcount
        return rowcount > 0
    except Exception as e:
        conn.rollback()
        print(f"Error permanently deleting customer from backup: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

