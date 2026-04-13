from database import get_connection
from models.product import deduct_sale
from models.customer import get_customer_by_id, update_customer




def create_sale(customer_id, items, payment_method, amount_paid, total_amount=None, actual_amount_received=None):
    # items = list of dicts: [{product_id, quantity, unit_price, subtotal}] 
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Calculate total if not provided
        if total_amount is None:
            total_amount = sum(item["subtotal"] for item in items)
        
        # Ensure numeric types for calculations
        total_amount = float(total_amount)
        amount_paid = float(amount_paid)
        
        # For CASH: calculate change based on actual amount received, not amount_paid
        if actual_amount_received is not None:
            actual_amount_received = float(actual_amount_received)
            change_amount = max(0, actual_amount_received - total_amount)
        else:
            change_amount = max(0, amount_paid - total_amount)
        
        status = "PAID" if payment_method != "CREDIT" else "NOT PAID"

        cursor.execute(
            "INSERT INTO sales (customer_id, total_amount, payment_method, amount_paid, change_amount, status, created_by) VALUES (%s, %s, %s, %s, %s, %s, NULL)",
            (customer_id, total_amount, payment_method, amount_paid, change_amount, status),
        )
        sale_id = cursor.lastrowid

        for item in items:
            cursor.execute(
                "INSERT INTO sold_items (sale_id, product_id, quantity, unit_price, subtotal) VALUES (%s, %s, %s, %s, %s)",
                (sale_id, item["product_id"], item["quantity"], item["unit_price"], item["subtotal"]),
            )
            deduct_sale(item["product_id"], item["quantity"], cursor=cursor, conn=conn)

        if payment_method == "CREDIT" and customer_id:
            try:
                customer = get_customer_by_id(customer_id)
                if customer:
                    # Balance due = total - amount paid
                    # If they paid less than total, add the difference to their credit balance
                    # If they paid more than total, subtract from their balance
                    balance_due = total_amount - amount_paid
                    new_balance = float(customer["current_balance"]) + balance_due
                    
                    # Update customer with new balance (pass current connection to reuse it)
                    update_customer(
                        customer_id,
                        name=customer["name"],
                        address=customer["address"],
                        contact_number=customer["contact_number"],
                        current_balance=new_balance,
                        conn=conn
                    )
            except Exception as e:
                print(f"Error updating customer balance: {e}")

        conn.commit()
        cursor.close()
        conn.close()
        return sale_id
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        raise Exception(f"Database error creating sale: {str(e)}")



def get_sales_history():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM sales_view"
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def get_money_flow_history():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM money_flow ORDER BY date ASC"
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows
