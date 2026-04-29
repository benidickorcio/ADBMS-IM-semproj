# MySQL connection, create tables

import mysql.connector
from config import DB_CONFIG

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


def initialize_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    
    
    tables = [
    # USERS
    """
    CREATE TABLE IF NOT EXISTS users (
        user_id       INT           AUTO_INCREMENT PRIMARY KEY,
        name          VARCHAR(100)  NOT NULL,
        username      VARCHAR(50)   NOT NULL UNIQUE,
        password_hash VARCHAR(255)  NOT NULL,
        role          ENUM('ADMIN','CASHIER') DEFAULT 'CASHIER'
    );
    """,

    # PRODUCTS
    """
    CREATE TABLE IF NOT EXISTS products (
        product_id   INT           AUTO_INCREMENT PRIMARY KEY,
        name         VARCHAR(50)   NOT NULL,
        quantity     INT           NOT NULL DEFAULT 0,
        cost_price        DECIMAL(10,2) NOT NULL,
        profit DECIMAL(10,2) DEFAULT 0.00,
        total_price DECIMAL(10,2) DEFAULT 0.00,
        status       ENUM('IN STOCK','LOW STOCK','OUT OF STOCK')
            NOT NULL DEFAULT 'IN STOCK',
        last_updated DATETIME  DEFAULT CURRENT_TIMESTAMP
            ON UPDATE CURRENT_TIMESTAMP
    );
    """,

    # CUSTOMERS
    """
    CREATE TABLE IF NOT EXISTS customers (
        customer_id     INT           AUTO_INCREMENT PRIMARY KEY,
        name            VARCHAR(100)  NOT NULL,
        address         VARCHAR(200),
        contact_number  VARCHAR(20),
        current_balance DECIMAL(10,2) DEFAULT 0.00
    );
    """,

    # CUSTOMERS BACKUP
    """
    CREATE TABLE IF NOT EXISTS customers_backup (
        backup_id       INT           AUTO_INCREMENT PRIMARY KEY,
        customer_id     INT           NOT NULL,
        name            VARCHAR(100)  NOT NULL,
        address         VARCHAR(200),
        contact_number  VARCHAR(20),
        current_balance DECIMAL(10,2) DEFAULT 0.00,
        deleted_at      DATETIME      DEFAULT CURRENT_TIMESTAMP
    );
    """,

    # SALES sa created by ay kung sino yung nag process ng sale, pwede admin or cashier username
    """
    CREATE TABLE IF NOT EXISTS sales (
        sales_id       INT           AUTO_INCREMENT PRIMARY KEY,
        customer_id    INT           DEFAULT NULL,
        sale_date      DATETIME      DEFAULT CURRENT_TIMESTAMP,
        total_amount   DECIMAL(10,2) NOT NULL,
        payment_method VARCHAR(20)   NOT NULL,
        amount_paid    DECIMAL(10,2) DEFAULT 0.00,
        change_amount  DECIMAL(10,2) DEFAULT 0.00,
        status         VARCHAR(30)   DEFAULT 'PAID',
        created_by     VARCHAR(50)   DEFAULT NULL,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON UPDATE CASCADE,
        FOREIGN KEY (created_by)  REFERENCES users(username)        ON UPDATE CASCADE 
    );
    """,

    # SALE ITEMS transaction history ng bawat item sa sales
    """
    CREATE TABLE IF NOT EXISTS sold_items (
        item_id    INT           AUTO_INCREMENT PRIMARY KEY,
        sale_id    INT           NOT NULL,
        product_id INT           NOT NULL,
        quantity   INT           NOT NULL,
        unit_price DECIMAL(10,2) NOT NULL,
        subtotal   DECIMAL(10,2) NOT NULL,
        FOREIGN KEY (sale_id)    REFERENCES sales(sales_id)       ON UPDATE CASCADE,
        FOREIGN KEY (product_id) REFERENCES products(product_id)  ON UPDATE CASCADE
    );
    """,

    # 6. RESTOCK (history ng bawat restock)
    """
    CREATE TABLE IF NOT EXISTS restock (
        restock_id   INT           AUTO_INCREMENT PRIMARY KEY,
        product_id   INT           NOT NULL,
        quantity     INT           NOT NULL,
        unit_cost    DECIMAL(10,2) NOT NULL,
        restock_date DATETIME      DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES products(product_id) ON UPDATE CASCADE
    );
    """,

    # 7. TRANSACTIONS LOG
    """
    CREATE TABLE IF NOT EXISTS transactions (
        transaction_id   INT           AUTO_INCREMENT PRIMARY KEY,
        sale_id          INT           DEFAULT NULL,
        created_by       VARCHAR(50)   NOT NULL,
        transaction_date DATETIME      DEFAULT CURRENT_TIMESTAMP,
        status           ENUM('SUCCESS','FAILED') NOT NULL DEFAULT 'SUCCESS',
        message          TEXT          DEFAULT NULL,
        FOREIGN KEY (sale_id)    REFERENCES sales(sales_id)   ON UPDATE CASCADE,
        FOREIGN KEY (created_by) REFERENCES users(username)   ON UPDATE CASCADE
    );
    """,
]
    
    
    triggers = [
    # INSERT TRIGGER
    """CREATE TRIGGER IF NOT EXISTS update_status_on_insert
        BEFORE INSERT ON products
        FOR EACH ROW
        BEGIN
            IF NEW.quantity = 0 THEN
                SET NEW.status = 'OUT OF STOCK';
            ELSEIF NEW.quantity <= 10 THEN
                SET NEW.status = 'LOW STOCK';
            ELSE
                SET NEW.status = 'IN STOCK';
            END IF;
        END
    """,

    # UPDATE TRIGGER
    """CREATE TRIGGER IF NOT EXISTS update_status_on_update
        BEFORE UPDATE ON products
        FOR EACH ROW
        BEGIN
            IF NEW.quantity = 0 THEN
                SET NEW.status = 'OUT OF STOCK';
            ELSEIF NEW.quantity <= 10 THEN
                SET NEW.status = 'LOW STOCK';
            ELSE
                SET NEW.status = 'IN STOCK';
            END IF;
        END
    """,

    # BACKUP TRIGGER — fires before a customer row is deleted
    """CREATE TRIGGER IF NOT EXISTS backup_customer_on_delete
        BEFORE DELETE ON customers
        FOR EACH ROW
        BEGIN
            INSERT INTO customers_backup (
                customer_id,
                name,
                address,
                contact_number,
                current_balance,
                deleted_at
            )
            VALUES (
                OLD.customer_id,
                OLD.name,
                OLD.address,
                OLD.contact_number,
                OLD.current_balance,
                NOW()
            );
        END
    """,
]
    views = [
        
        """
        CREATE VIEW IF NOT EXISTS v_restock_history AS
        SELECT  r.restock_id,
                r.product_id,
                p.name        AS product_name,
                r.quantity,
                r.unit_cost,
                r.restock_date
        FROM restock r
        JOIN products p ON p.product_id = r.product_id
        ORDER BY r.restock_date DESC;
        """,
        """CREATE VIEW IF NOT EXISTS sales_view AS
        SELECT
            s.sales_id        AS sale_id,
            p.name            AS product_name,
            si.unit_price     AS unit_price,
            si.quantity       AS quantity,
            si.subtotal       AS subtotal,
            s.sale_date       AS sale_date,
            s.payment_method  AS payment_method,
            s.status          AS status,
            s.created_by      AS created_by,
            c.name            AS customer_name
        FROM sales s
        LEFT JOIN customers  c  ON s.customer_id = c.customer_id
        INNER JOIN sold_items si ON s.sales_id    = si.sale_id
        INNER JOIN products   p  ON si.product_id = p.product_id

        ORDER BY s.sales_id DESC;""",
        """CREATE VIEW IF NOT EXISTS money_flow AS
        SELECT
            'SALE' AS transaction_type,
            s.sale_date AS date,
            p.name AS product_name,
            si.quantity AS quantity,
            si.subtotal AS amount
        FROM sales s
        JOIN sold_items si ON si.sale_id = s.sales_id
        JOIN products p ON p.product_id = si.product_id

        UNION ALL

        SELECT
            'RESTOCK' AS transaction_type,
            r.restock_date AS date,
            p.name AS product_name,
            r.quantity AS quantity,
            r.unit_cost * r.quantity AS amount
        FROM restock r
        JOIN products p ON p.product_id = r.product_id;"""
]
    
    procedures = [
    """
    CREATE PROCEDURE IF NOT EXISTS GetUser(
        IN p_username VARCHAR(50),
        IN p_password VARCHAR(255)
    )
    BEGIN
        SELECT user_id, name, username, role
        FROM users
        WHERE username = p_username
        AND password_hash = p_password;
    END
    """,
    """
    CREATE PROCEDURE IF NOT EXISTS UpdateCustomer(
    IN p_customer_id     INT,
    IN p_name            VARCHAR(100),
    IN p_address         VARCHAR(200),
    IN p_contact_number  VARCHAR(20),
    IN p_current_balance DECIMAL(10,2)
)
BEGIN
    UPDATE customers
    SET
        name            = p_name,
        address         = p_address,
        contact_number  = p_contact_number,
        current_balance = p_current_balance
    WHERE customer_id = p_customer_id;
END
    """
]
    functions = [
    """CREATE FUNCTION IF NOT EXISTS CalculateChange(
        total DECIMAL(10,2),
        amount_paid DECIMAL(10,2)
    )
    RETURNS DECIMAL(10,2)
    DETERMINISTIC
    BEGIN
        RETURN amount_paid - total;
    END
    """,
    """CREATE FUNCTION IF NOT EXISTS users_count()
    RETURNS INT
    DETERMINISTIC
    BEGIN
        DECLARE count INT;
        SELECT COUNT(*) INTO count FROM users;
        RETURN count;
    END
    """,
    """CREATE FUNCTION IF NOT EXISTS total_stock_amount(qty INT, unit_price DECIMAL(10,2))
    RETURNS DECIMAL(15,2)
    DETERMINISTIC
    BEGIN
        DECLARE total DECIMAL(15,2);
        SET total = qty * unit_price;
        RETURN total;
    END
    """,
]
    #execute tables
    for table in tables:
        cursor.execute(table)
    
    #execute triggers
    for trigger in triggers:
        cursor.execute(trigger)
    
    #execute views
    for view in views:
        cursor.execute(view)
        
    # execute procedures
    for procedure in procedures:
        cursor.execute(procedure)

    # execute functions
    for function in functions:
        cursor.execute(function)
    #------- DEFAULT ADMIN ACCOUNT --------------
    
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    
    if count == 0:
        import hashlib
        default_password = hashlib.sha256("admin123".encode()).hexdigest()
        
        cursor.execute("""
                    INSERT INTO users (name,username,password_hash,role)
                    VALUES(%s,%s,%s,%s)
                    """,("ARNEL ERMITA","rnel",default_password,"ADMIN"))
        
    # -------CASHIER DEFAULT ACCOUNTS-------------------------------------
        def_cashier_password = hashlib.sha256("cashier123".encode()).hexdigest()
        
        cashier_def_accounts = [
            ("RONALD GREGORIO","ronald",def_cashier_password,"CASHIER")
        ]
        cursor.executemany("""
                        INSERT INTO users (name,username,password_hash,role)
                        VALUES(%s,%s,%s,%s)
                        """,cashier_def_accounts)
        
    conn.commit()
    cursor.close()
    conn.close()
    
def get_current_user(username: str, password_hash: str) -> dict | None:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.callproc("GetUser", (username, password_hash))

    user = None
    for result in cursor.stored_results():
        row = result.fetchone()
        if row:
            user = row

    cursor.close()
    conn.close()
    return user


# ========== USER MANAGEMENT FUNCTIONS ==========

def get_all_users():
    """Get all users (for admin view). Returns list of user dicts."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT user_id, name, username, password_hash, role FROM users ORDER BY user_id")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def delete_user_by_username(username: str) -> bool:
    """Delete user by username. Returns True if successful, False if failed or not allowed."""
    # List of default accounts that cannot be deleted
    default_usernames = ["devskiel", "Doxgiane", "Doxbene"]
    
    if username in default_usernames:
        return False
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM users WHERE username = %s", (username,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error deleting user: {str(e)}")
    finally:
        cursor.close()
        conn.close()


def update_username(old_username: str, new_username: str) -> bool:
    """Update username. Returns True if successful."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("UPDATE users SET username = %s WHERE username = %s", (new_username, old_username))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error updating username: {str(e)}")
    finally:
        cursor.close()
        conn.close()


def update_password(username: str, new_password_hash: str) -> bool:
    """Update password. Returns True if successful."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("UPDATE users SET password_hash = %s WHERE username = %s", (new_password_hash, username))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error updating password: {str(e)}")
    finally:
        cursor.close()
        conn.close()


def add_user(name: str, username: str, password: str, role: str) -> bool:
    """Add new user. Returns True if successful."""
    import hashlib
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO users (name, username, password_hash, role) VALUES (%s, %s, %s, %s)",
            (name, username, password_hash, role)
        )
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error adding user: {str(e)}")
    finally:
        cursor.close()
        conn.close()


def get_admin_count() -> int:
    """Get the number of admin accounts."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'ADMIN'")
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return count


def verify_password(username: str, password: str) -> bool:
    """Verify if password is correct for the given username."""
    import hashlib
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE username = %s AND password_hash = %s", (username, password_hash))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result is not None

