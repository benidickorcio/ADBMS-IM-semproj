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
        price        DECIMAL(10,2) NOT NULL,
        quantity     INT           NOT NULL DEFAULT 0,
        status       ENUM('IN STOCK','LOW STOCK','OUT OF STOCK')
            NOT NULL DEFAULT 'IN STOCK',
        last_updated DATETIME      DEFAULT CURRENT_TIMESTAMP
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

    # SALES
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
        created_by     INT           DEFAULT NULL,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON UPDATE CASCADE ON DELETE CASCADE,
        FOREIGN KEY (created_by)  REFERENCES users(user_id)         ON UPDATE CASCADE
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
        FOREIGN KEY (sale_id)    REFERENCES sales(sales_id)       ON UPDATE CASCADE ON DELETE CASCADE,
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
]
    # top selling products view for sales
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
            COALESCE(c.name, 'Walk-in') AS customer_name

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
                    """,("Ezekiel Reyes","devskiel",default_password,"ADMIN"))
        
    # -------CASHIER DEFAULT ACCOUNTS-------------------------------------
        def_cashier_password = hashlib.sha256("cashier123".encode()).hexdigest()
        
        cashier_def_accounts = [
            ("Giane Ogana","Doxgiane",def_cashier_password,"CASHIER"),
            ("Benedick Orcio","Doxbene",def_cashier_password,"CASHIER")
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

