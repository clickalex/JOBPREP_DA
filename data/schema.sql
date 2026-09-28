-- ShopKart schema (SQLite). Created by data/generate_data.py
PRAGMA foreign_keys = ON;

CREATE TABLE customers (
    customer_id         INTEGER PRIMARY KEY,
    first_name          TEXT NOT NULL,
    last_name           TEXT NOT NULL,
    email               TEXT,
    gender              TEXT,
    birth_year          INTEGER,
    city                TEXT,
    state               TEXT,
    region              TEXT,
    acquisition_channel TEXT,
    signup_date         TEXT            -- 'YYYY-MM-DD'
);

CREATE TABLE products (
    product_id   INTEGER PRIMARY KEY,
    product_name TEXT NOT NULL,
    category     TEXT NOT NULL,
    subcategory  TEXT,
    list_price   REAL,                  -- current catalogue price (INR, before FY26 hike)
    unit_cost    REAL,                  -- cost of goods per unit (INR)
    launch_date  TEXT
);

CREATE TABLE orders (
    order_id       INTEGER PRIMARY KEY,
    customer_id    INTEGER NOT NULL REFERENCES customers(customer_id),
    order_ts       TEXT NOT NULL,       -- 'YYYY-MM-DD HH:MM:SS'
    status         TEXT NOT NULL,       -- Delivered | Shipped | Cancelled | Returned
    payment_method TEXT,
    device         TEXT,
    coupon_code    TEXT,                -- NULL when no coupon
    shipping_fee   REAL
);

CREATE TABLE order_items (
    order_item_id INTEGER PRIMARY KEY,
    order_id      INTEGER NOT NULL REFERENCES orders(order_id),
    product_id    INTEGER NOT NULL REFERENCES products(product_id),
    quantity      INTEGER NOT NULL,
    unit_price    REAL NOT NULL,        -- price actually charged per unit (INR)
    discount      REAL NOT NULL         -- total discount on the line (INR)
);

CREATE TABLE web_sessions (
    session_id      TEXT PRIMARY KEY,
    session_start   TEXT,
    customer_id     INTEGER,            -- NULL for anonymous visitors
    device          TEXT,
    traffic_source  TEXT,
    pages_viewed    INTEGER,
    viewed_product  INTEGER,            -- funnel flags (0/1)
    added_to_cart   INTEGER,
    began_checkout  INTEGER,
    purchased       INTEGER
);

CREATE TABLE checkout_experiment (
    visitor_id  TEXT PRIMARY KEY,
    variant     TEXT,                   -- A_control | B_new_checkout
    device      TEXT,
    assigned_at TEXT,
    converted   INTEGER,
    order_value REAL
);

CREATE TABLE employees (
    employee_id    INTEGER PRIMARY KEY,
    full_name      TEXT,
    department     TEXT,
    manager_id     INTEGER REFERENCES employees(employee_id),
    hire_date      TEXT,
    monthly_salary INTEGER              -- INR
);

CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_ts ON orders(order_ts);
CREATE INDEX idx_items_order ON order_items(order_id);
CREATE INDEX idx_items_product ON order_items(product_id);
