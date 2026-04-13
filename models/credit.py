from models.customer import get_customer_by_id, update_customer


def add_charge(customer_id, amount, sale_id=None):
    customer = get_customer_by_id(customer_id)
    if customer is None:
        raise ValueError("Customer not found")

    current_balance = float(customer.get("current_balance", 0.0))
    updated = current_balance + float(amount)

    update_customer(customer_id, current_balance=updated)
    return updated


def add_payment(customer_id, amount, notes=None):
    customer = get_customer_by_id(customer_id)
    if customer is None:
        raise ValueError("Customer not found")

    current_balance = float(customer.get("current_balance", 0.0))
    updated = max(0.0, current_balance - float(amount))

    update_customer(customer_id, current_balance=updated)
    return updated


def get_customer_balance(customer_id):
    customer = get_customer_by_id(customer_id)
    return float(customer.get("current_balance", 0.0)) if customer else None