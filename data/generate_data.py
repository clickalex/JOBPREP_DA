"""
Generate the ShopKart practice datasets used across this repo.

ShopKart is a FICTIONAL Indian e-commerce company. The data is synthetic but
built to behave like the real thing: growth, festive-season (Diwali) spikes,
channel-dependent retention, category-dependent returns, a regional logistics
incident, a checkout A/B test and messy "raw" exports that need cleaning.

Run from the repo root:
    python data/generate_data.py

Outputs (deterministic, seed=42):
    data/clean/*.csv      analysis-ready tables
    data/raw/*.csv        messy exports (duplicates, bad casing, mixed dates, outliers...)
    data/shopkart.db      SQLite database of the clean tables (for SQL practice)
"""
from __future__ import annotations

import sys

import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

# Windows consoles/pipes default to cp1252, which can't print ✓ ✗ ₹ — force UTF-8.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

SEED = 42
START = pd.Timestamp("2024-01-01")
END = pd.Timestamp("2025-12-31")
N_CUSTOMERS = 8000

ROOT = Path(__file__).resolve().parent
CLEAN = ROOT / "clean"
RAW = ROOT / "raw"
DB_PATH = ROOT / "shopkart.db"

rng = np.random.default_rng(SEED)

# --------------------------------------------------------------------------- #
# Reference data
# --------------------------------------------------------------------------- #
CITIES = [  # city, state, region, weight
    ("Delhi", "Delhi", "North", 0.14), ("Gurugram", "Haryana", "North", 0.05),
    ("Noida", "Uttar Pradesh", "North", 0.04), ("Lucknow", "Uttar Pradesh", "North", 0.04),
    ("Jaipur", "Rajasthan", "North", 0.04), ("Chandigarh", "Chandigarh", "North", 0.03),
    ("Mumbai", "Maharashtra", "West", 0.13), ("Pune", "Maharashtra", "West", 0.07),
    ("Ahmedabad", "Gujarat", "West", 0.05), ("Indore", "Madhya Pradesh", "West", 0.03),
    ("Bengaluru", "Karnataka", "South", 0.13), ("Hyderabad", "Telangana", "South", 0.08),
    ("Chennai", "Tamil Nadu", "South", 0.07), ("Kochi", "Kerala", "South", 0.03),
    ("Kolkata", "West Bengal", "East", 0.07),
]

# channel: share of signups, P(churn after each order), mean days between orders,
#          P(never orders)
CHANNELS = {
    "Organic Search": (0.28, 0.45, 75, 0.18),
    "Paid Search":    (0.20, 0.52, 90, 0.20),
    "Paid Social":    (0.24, 0.62, 110, 0.30),
    "Referral":       (0.12, 0.33, 55, 0.10),
    "Email":          (0.08, 0.40, 70, 0.15),
    "Affiliate":      (0.08, 0.66, 120, 0.28),
}

FIRST = ["Aarav", "Vivaan", "Aditya", "Arjun", "Sai", "Reyansh", "Krishna", "Ishaan",
         "Rohan", "Kabir", "Ananya", "Diya", "Aadhya", "Saanvi", "Pari", "Myra", "Kiara",
         "Isha", "Priya", "Neha", "Rahul", "Amit", "Sneha", "Pooja", "Vikram", "Karan",
         "Meera", "Tanvi", "Nikhil", "Riya", "Farhan", "Zoya", "Aman", "Simran", "Harpreet",
         "Arnav", "Lakshmi", "Deepak", "Kavya", "Manish"]
LAST = ["Sharma", "Verma", "Gupta", "Singh", "Kumar", "Patel", "Reddy", "Iyer", "Nair",
        "Das", "Banerjee", "Mehta", "Joshi", "Khan", "Chopra", "Malhotra", "Rao", "Pillai",
        "Agarwal", "Bose", "Kapoor", "Mishra", "Yadav", "Shah", "Menon"]

# category: (margin range, return probability for an order containing it, popularity)
CATEGORIES = {
    "Electronics":    ((0.12, 0.25), 0.05, 1.2),
    "Fashion":        ((0.45, 0.60), 0.16, 1.5),
    "Home & Kitchen": ((0.30, 0.40), 0.04, 1.0),
    "Beauty":         ((0.50, 0.65), 0.03, 1.1),
    "Books":          ((0.25, 0.35), 0.02, 0.7),
    "Sports":         ((0.35, 0.45), 0.05, 0.6),
}

PRODUCTS = [  # name, category, subcategory, list price (INR)
    ("Wireless Earbuds", "Electronics", "Audio", 1999), ("Over-Ear Headphones", "Electronics", "Audio", 3499),
    ("Bluetooth Speaker", "Electronics", "Audio", 2499), ("Smartwatch", "Electronics", "Wearables", 4999),
    ("Fitness Band", "Electronics", "Wearables", 2299), ("20000mAh Power Bank", "Electronics", "Accessories", 1499),
    ("65W Fast Charger", "Electronics", "Accessories", 1199), ("USB-C Cable (2-pack)", "Electronics", "Accessories", 399),
    ("Mechanical Keyboard", "Electronics", "Computer", 3999), ("Wireless Mouse", "Electronics", "Computer", 799),
    ("Cotton T-Shirt", "Fashion", "Menswear", 499), ("Slim Fit Jeans", "Fashion", "Menswear", 1499),
    ("Linen Shirt", "Fashion", "Menswear", 1299), ("Printed Kurta", "Fashion", "Womenswear", 1199),
    ("Silk Saree", "Fashion", "Womenswear", 3999), ("Anarkali Dress", "Fashion", "Womenswear", 2499),
    ("Running Sneakers", "Fashion", "Footwear", 2999), ("Casual Sandals", "Fashion", "Footwear", 899),
    ("Denim Jacket", "Fashion", "Menswear", 2199), ("Leather Wallet", "Fashion", "Accessories", 699),
    ("Non-Stick Cookware Set", "Home & Kitchen", "Cookware", 2799), ("Pressure Cooker 5L", "Home & Kitchen", "Cookware", 1899),
    ("Mixer Grinder", "Home & Kitchen", "Appliances", 3299), ("Electric Kettle", "Home & Kitchen", "Appliances", 1099),
    ("Cotton Bedsheet Set", "Home & Kitchen", "Furnishing", 1299), ("Steel Water Bottle", "Home & Kitchen", "Kitchen Tools", 449),
    ("Storage Containers (6)", "Home & Kitchen", "Kitchen Tools", 649), ("Table Lamp", "Home & Kitchen", "Decor", 999),
    ("Diya & Candle Set", "Home & Kitchen", "Decor", 549),
    ("Vitamin C Serum", "Beauty", "Skincare", 699), ("Face Wash", "Beauty", "Skincare", 299),
    ("Sunscreen SPF 50", "Beauty", "Skincare", 449), ("Matte Lipstick", "Beauty", "Makeup", 399),
    ("Kajal", "Beauty", "Makeup", 199), ("Perfume 100ml", "Beauty", "Fragrance", 1499),
    ("Beard Grooming Kit", "Beauty", "Grooming", 899), ("Hair Oil", "Beauty", "Haircare", 249),
    ("Bestselling Novel", "Books", "Fiction", 399), ("Self-Help Paperback", "Books", "Non-Fiction", 349),
    ("Competitive Exam Guide", "Books", "Education", 599), ("Children's Storybook", "Books", "Kids", 249),
    ("SQL for Data Analysis", "Books", "Education", 799),
    ("Yoga Mat", "Sports", "Fitness", 799), ("Adjustable Dumbbells", "Sports", "Fitness", 2999),
    ("Resistance Bands", "Sports", "Fitness", 599), ("English Willow Cricket Bat", "Sports", "Cricket", 4499),
    ("Badminton Racket", "Sports", "Racket Sports", 1299), ("Football", "Sports", "Outdoor", 699),
]

PAYMENT = {"UPI": 0.46, "Credit Card": 0.17, "Debit Card": 0.11, "Cash on Delivery": 0.20, "Net Banking": 0.06}
DEVICES = {"Mobile App": 0.50, "Mobile Web": 0.30, "Desktop": 0.20}

FESTIVE = [(pd.Timestamp("2024-10-15"), pd.Timestamp("2024-11-05")),   # Diwali 2024: 1 Nov
           (pd.Timestamp("2025-10-05"), pd.Timestamp("2025-10-25"))]   # Diwali 2025: 21 Oct
PRICE_HIKE_DATE = pd.Timestamp("2025-04-01")  # list prices +5% from FY26
INCIDENT = ("Maharashtra", pd.Timestamp("2025-06-01"), pd.Timestamp("2025-06-30"))  # courier outage


def pick(options: dict, size=None):
    keys = list(options)
    p = np.array(list(options.values()), dtype=float)
    return rng.choice(keys, size=size, p=p / p.sum())


def in_festive(ts: pd.Timestamp) -> bool:
    return any(a <= ts <= b for a, b in FESTIVE)


# --------------------------------------------------------------------------- #
# Products
# --------------------------------------------------------------------------- #
def make_products() -> pd.DataFrame:
    rows = []
    for i, (name, cat, sub, price) in enumerate(PRODUCTS, start=1):
        lo, hi = CATEGORIES[cat][0]
        margin = rng.uniform(lo, hi)
        rows.append({
            "product_id": 100 + i,
            "product_name": name,
            "category": cat,
            "subcategory": sub,
            "list_price": float(price),
            "unit_cost": round(price * (1 - margin), 2),
            "launch_date": (START - pd.Timedelta(days=int(rng.integers(30, 400)))).date(),
        })
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------- #
# Customers
# --------------------------------------------------------------------------- #
def make_customers() -> pd.DataFrame:
    total_days = (END - START).days
    # growth: signup density rises linearly (~2.2x by the end) + a festive bump
    u = rng.random(N_CUSTOMERS * 3)
    days = (np.sqrt(1 + 3.84 * u) - 1) / 1.2 * total_days  # inverse CDF of linear density
    days = days[days <= total_days]
    dates = START + pd.to_timedelta(days.astype(int), unit="D")
    festive_extra = [d for d in dates if in_festive(d)]
    dates = np.concatenate([dates, np.array(festive_extra[: int(len(festive_extra) * 0.4)])])
    dates = pd.to_datetime(rng.choice(dates, N_CUSTOMERS, replace=False))
    dates = dates.sort_values()

    city_idx = rng.choice(len(CITIES), N_CUSTOMERS, p=np.array([c[3] for c in CITIES]) / sum(c[3] for c in CITIES))
    channel_names = list(CHANNELS)
    ch_p = np.array([CHANNELS[c][0] for c in channel_names])
    channels = rng.choice(channel_names, N_CUSTOMERS, p=ch_p / ch_p.sum())

    first = rng.choice(FIRST, N_CUSTOMERS)
    last = rng.choice(LAST, N_CUSTOMERS)
    ids = np.arange(1, N_CUSTOMERS + 1) + 10000
    emails = [f"{f.lower()}.{l.lower()}{i % 1000}@{rng.choice(['gmail.com', 'yahoo.in', 'outlook.com', 'rediffmail.com'], p=[.7, .12, .13, .05])}"
              for f, l, i in zip(first, last, ids)]
    return pd.DataFrame({
        "customer_id": ids,
        "first_name": first,
        "last_name": last,
        "email": emails,
        "gender": rng.choice(["F", "M"], N_CUSTOMERS, p=[.48, .52]),
        "birth_year": rng.normal(1994, 8, N_CUSTOMERS).clip(1960, 2006).astype(int),
        "city": [CITIES[i][0] for i in city_idx],
        "state": [CITIES[i][1] for i in city_idx],
        "region": [CITIES[i][2] for i in city_idx],
        "acquisition_channel": channels,
        "signup_date": dates.date,
    })


# --------------------------------------------------------------------------- #
# Orders + items
# --------------------------------------------------------------------------- #
def make_orders(customers: pd.DataFrame, products: pd.DataFrame):
    pop = np.array([CATEGORIES[c][2] for c in products["category"]]) * rng.uniform(0.5, 1.5, len(products))
    pop /= pop.sum()
    prod_ids = products["product_id"].to_numpy()
    prod_price = dict(zip(products["product_id"], products["list_price"]))
    prod_cat = dict(zip(products["product_id"], products["category"]))
    diya_id = products.loc[products["product_name"] == "Diya & Candle Set", "product_id"].iloc[0]

    orders, items = [], []
    order_id, item_id = 500000, 1

    def add_order(cust, ts: pd.Timestamp, n_prev: int):
        nonlocal order_id, item_id
        order_id += 1
        ts = ts + pd.Timedelta(minutes=int(rng.integers(7 * 60, 24 * 60)))  # time of day
        device = pick(DEVICES)
        payment = pick(PAYMENT)
        # coupons: welcome coupon on first orders, festival coupon in festive windows
        coupon = None
        if n_prev == 0 and rng.random() < 0.45:
            coupon = "WELCOME15"
        elif in_festive(ts.normalize()) and rng.random() < 0.55:
            coupon = "FEST10"
        elif rng.random() < 0.08:
            coupon = "SAVE5"
        pct = {"WELCOME15": 0.15, "FEST10": 0.10, "SAVE5": 0.05, None: 0.0}[coupon]

        n_items = rng.choice([1, 2, 3, 4], p=[.55, .28, .12, .05])
        chosen = rng.choice(prod_ids, n_items, replace=False, p=pop)
        if in_festive(ts.normalize()) and rng.random() < 0.35 and diya_id not in chosen:
            chosen = np.append(chosen, diya_id)
        subtotal, cats = 0.0, set()
        for pid in chosen:
            qty = int(rng.choice([1, 2, 3], p=[.82, .14, .04]))
            price = prod_price[pid] * (1.05 if ts >= PRICE_HIKE_DATE else 1.0)
            price = round(price, 0)
            disc = round(price * qty * pct, 2)
            items.append({"order_item_id": item_id, "order_id": order_id, "product_id": int(pid),
                          "quantity": qty, "unit_price": price, "discount": disc})
            item_id += 1
            subtotal += price * qty - disc
            cats.add(prod_cat[pid])

        # status
        p_cancel = 0.04 + (0.07 if payment == "Cash on Delivery" else 0)
        if cust.state == INCIDENT[0] and INCIDENT[1] <= ts <= INCIDENT[2] + pd.Timedelta(days=1):
            p_cancel += 0.22
        p_return = max(CATEGORIES[c][1] for c in cats)
        r = rng.random()
        if ts >= END - pd.Timedelta(days=4):
            status = "Shipped" if r > p_cancel else "Cancelled"
        elif r < p_cancel:
            status = "Cancelled"
        elif r < p_cancel + p_return:
            status = "Returned"
        else:
            status = "Delivered"
        ship_fee = 0.0 if subtotal >= 499 else 49.0
        orders.append({"order_id": order_id, "customer_id": int(cust.customer_id),
                       "order_ts": ts, "status": status, "payment_method": payment,
                       "device": device, "coupon_code": coupon, "shipping_fee": ship_fee})

    for cust in customers.itertuples(index=False):
        churn_p, mean_gap, never_p = CHANNELS[cust.acquisition_channel][1:]
        if rng.random() < never_p:
            continue
        ts = pd.Timestamp(cust.signup_date) + pd.Timedelta(days=int(rng.exponential(4)))
        n = 0
        while ts <= END:
            add_order(cust, ts, n)
            n += 1
            if rng.random() < churn_p * (0.85 if n > 2 else 1.0):
                break
            gap = rng.exponential(mean_gap) + 3
            nxt = ts + pd.Timedelta(days=int(gap))
            # festive pull-forward: if the next order would land shortly after a sale, pull it in
            for a, b in FESTIVE:
                if ts < a and b < nxt < b + pd.Timedelta(days=45) and rng.random() < 0.3:
                    nxt = a + pd.Timedelta(days=int(rng.integers(0, (b - a).days)))
            ts = nxt
        # extra festive-sale orders from existing customers
        for a, b in FESTIVE:
            if pd.Timestamp(cust.signup_date) < a and rng.random() < 0.07 * (1 if n else 0.3):
                add_order(cust, a + pd.Timedelta(days=int(rng.integers(0, (b - a).days))), max(n, 1))

    orders = pd.DataFrame(orders).sort_values("order_ts").reset_index(drop=True)
    items = pd.DataFrame(items)
    # re-number orders chronologically so order_id increases with time
    mapping = dict(zip(orders["order_id"], range(500001, 500001 + len(orders))))
    orders["order_id"] = orders["order_id"].map(mapping)
    items["order_id"] = items["order_id"].map(mapping)
    items = items.sort_values(["order_id", "order_item_id"]).reset_index(drop=True)
    items["order_item_id"] = np.arange(1, len(items) + 1)
    orders["order_ts"] = orders["order_ts"].dt.strftime("%Y-%m-%d %H:%M:%S")
    return orders, items


# --------------------------------------------------------------------------- #
# Web sessions (funnel), A/B test, employees
# --------------------------------------------------------------------------- #
def make_sessions(customers: pd.DataFrame) -> pd.DataFrame:
    n = 40000
    start, end = pd.Timestamp("2025-07-01"), pd.Timestamp("2025-12-31 23:59:59")
    ts = start + pd.to_timedelta(rng.integers(0, int((end - start).total_seconds()), n), unit="s")
    device = pick(DEVICES, n)
    source = pick({"Organic Search": .30, "Paid Search": .18, "Paid Social": .25, "Direct": .12,
                   "Email": .08, "Referral": .07}, n)
    logged_in = rng.random(n) < np.where(device == "Mobile App", 0.85, 0.40)
    cust = np.where(logged_in, rng.choice(customers["customer_id"], n), None)
    # step conversion probabilities by device
    base = {"Mobile App": (.72, .38, .66, .70), "Mobile Web": (.60, .26, .52, .55), "Desktop": (.66, .31, .60, .66)}
    src_mult = {"Organic Search": 1.0, "Paid Search": 1.05, "Paid Social": 0.80, "Direct": 1.15, "Email": 1.20, "Referral": 1.10}
    p = np.array([base[d] for d in device]) * np.array([src_mult[s] for s in source])[:, None]
    p = p.clip(0, 0.95)
    r = rng.random((n, 4))
    view = r[:, 0] < p[:, 0]
    cart = view & (r[:, 1] < p[:, 1])
    checkout = cart & (r[:, 2] < p[:, 2])
    purchase = checkout & (r[:, 3] < p[:, 3])
    pages = 1 + rng.poisson(2, n) + view * rng.poisson(3, n) + cart * 2 + checkout * 2
    df = pd.DataFrame({
        "session_id": [f"S{100000 + i}" for i in range(n)],
        "session_start": ts,
        "customer_id": cust,
        "device": device,
        "traffic_source": source,
        "pages_viewed": pages,
        "viewed_product": view.astype(int),
        "added_to_cart": cart.astype(int),
        "began_checkout": checkout.astype(int),
        "purchased": purchase.astype(int),
    }).sort_values("session_start").reset_index(drop=True)
    df["session_id"] = [f"S{100001 + i}" for i in range(n)]
    df["session_start"] = df["session_start"].dt.strftime("%Y-%m-%d %H:%M:%S")
    df["customer_id"] = df["customer_id"].astype("Int64")
    return df


def make_experiment() -> pd.DataFrame:
    """Checkout redesign test (1-28 Sep 2025). B lifts conversion in the Mobile App only."""
    r = np.random.default_rng(53)  # independent stream so the test result is stable
    n = 24000
    variant = r.choice(["A_control", "B_new_checkout"], n)
    device = r.choice(["Mobile App", "Mobile Web", "Desktop"], n, p=[.45, .35, .20])
    base = np.select([device == "Mobile App", device == "Mobile Web"], [0.115, 0.085], 0.105)
    lift = np.where(variant == "B_new_checkout", np.where(device == "Mobile App", 0.026, 0.0), 0)
    converted = (r.random(n) < base + lift).astype(int)
    value = np.where(converted == 1, np.round(r.lognormal(7.1, 0.55, n), 2), 0.0)
    assigned = pd.Timestamp("2025-09-01") + pd.to_timedelta(r.integers(0, 28 * 86400, n), unit="s")
    df = pd.DataFrame({"visitor_id": [f"V{700000 + i}" for i in range(n)], "variant": variant,
                       "device": device, "assigned_at": assigned, "converted": converted,
                       "order_value": value}).sort_values("assigned_at").reset_index(drop=True)
    df["assigned_at"] = df["assigned_at"].dt.strftime("%Y-%m-%d %H:%M:%S")
    return df


def make_employees() -> pd.DataFrame:
    rows = [
        (1, "Rajesh Khanna", "Leadership", None, "2018-04-01", 450000),
        (2, "Sunita Rao", "Analytics", 1, "2019-06-15", 260000),
        (3, "Imran Qureshi", "Marketing", 1, "2019-01-10", 240000),
        (4, "Lakshmi Iyer", "Operations", 1, "2018-11-20", 230000),
        (5, "Arvind Menon", "Engineering", 1, "2018-07-01", 300000),
        (6, "Neha Gupta", "Analytics", 2, "2021-02-01", 140000),
        (7, "Karan Malhotra", "Analytics", 2, "2022-07-18", 110000),
        (8, "Pooja Shah", "Analytics", 2, "2023-01-09", 95000),
        (9, "Farhan Ali", "Analytics", 6, "2024-06-03", 75000),
        (10, "Riya Das", "Analytics", 6, "2024-06-03", 75000),
        (11, "Vikram Singh", "Marketing", 3, "2020-03-16", 150000),
        (12, "Tanvi Joshi", "Marketing", 3, "2022-09-05", 105000),
        (13, "Aman Verma", "Marketing", 11, "2023-11-13", 80000),
        (14, "Simran Kaur", "Marketing", 11, "2024-02-19", 80000),
        (15, "Deepak Yadav", "Operations", 4, "2019-08-26", 120000),
        (16, "Meera Pillai", "Operations", 4, "2021-05-10", 98000),
        (17, "Rohit Mishra", "Operations", 15, "2022-12-01", 62000),
        (18, "Sneha Reddy", "Operations", 15, "2023-04-17", 60000),
        (19, "Manish Agarwal", "Operations", 15, "2025-01-06", 58000),
        (20, "Kavya Nair", "Engineering", 5, "2019-10-01", 210000),
        (21, "Nikhil Bose", "Engineering", 5, "2020-08-24", 195000),
        (22, "Isha Kapoor", "Engineering", 20, "2022-03-14", 160000),
        (23, "Arjun Patel", "Engineering", 20, "2023-07-03", 140000),
        (24, "Diya Chopra", "Engineering", 21, "2024-01-22", 125000),
        (25, "Sai Krishnan", "Engineering", 21, "2025-03-10", 125000),
        (26, "Harpreet Gill", "Customer Support", 4, "2020-01-13", 90000),
        (27, "Zoya Sheikh", "Customer Support", 26, "2023-06-12", 45000),
        (28, "Rahul Kumar", "Customer Support", 26, "2024-09-02", 42000),
        (29, "Priya Sharma", "Customer Support", 26, "2025-05-19", 42000),
        (30, "Ananya Banerjee", "Analytics", 2, "2025-08-04", 95000),
    ]
    return pd.DataFrame(rows, columns=["employee_id", "full_name", "department", "manager_id",
                                       "hire_date", "monthly_salary"]).astype({"manager_id": "Int64"})


# --------------------------------------------------------------------------- #
# Messy raw exports
# --------------------------------------------------------------------------- #
def make_raw(customers: pd.DataFrame, orders: pd.DataFrame, items: pd.DataFrame, products: pd.DataFrame):
    c = customers.copy()
    # inconsistent city spellings / casing / whitespace
    variants = {"Bengaluru": ["Bangalore", "bengaluru", "BENGALURU", "Bengaluru "],
                "Delhi": ["New Delhi", "delhi", " Delhi", "NEW DELHI"],
                "Mumbai": ["Bombay", "mumbai", "Mumbai "], "Gurugram": ["Gurgaon", "gurugram"],
                "Kolkata": ["Calcutta", "kolkata"], "Chennai": ["Madras", "chennai "]}
    for city, alts in variants.items():
        m = (c["city"] == city) & (rng.random(len(c)) < 0.25)
        c.loc[m, "city"] = rng.choice(alts, m.sum())
    # mixed date formats
    d = pd.to_datetime(c["signup_date"])
    fmt = rng.choice(["%Y-%m-%d", "%d/%m/%Y", "%d %b %Y"], len(c), p=[.7, .2, .1])
    c["signup_date"] = [x.strftime(f) for x, f in zip(d, fmt)]
    # emails: random upper-case, missing
    m = rng.random(len(c)) < 0.10
    c.loc[m, "email"] = c.loc[m, "email"].str.upper()
    c.loc[rng.random(len(c)) < 0.03, "email"] = np.nan
    c.loc[rng.random(len(c)) < 0.02, "acquisition_channel"] = np.nan
    c = c.drop(columns=["region"])
    # duplicate rows (exact + near-duplicates with trailing spaces in name)
    dup = c.sample(frac=0.02, random_state=SEED)
    near = c.sample(frac=0.01, random_state=SEED + 1).assign(first_name=lambda x: x["first_name"] + " ")
    c = pd.concat([c, dup, near]).sample(frac=1, random_state=SEED).reset_index(drop=True)

    o = orders.copy()
    m = rng.random(len(o))
    o.loc[m < 0.15, "status"] = o.loc[m < 0.15, "status"].str.upper()
    o.loc[(m >= 0.15) & (m < 0.25), "status"] = o.loc[(m >= 0.15) & (m < 0.25), "status"].str.lower() + " "
    pay_alt = {"Cash on Delivery": ["COD", "cod", "Cash On Delivery"], "UPI": ["upi", "Upi"],
               "Credit Card": ["credit card", "CC"], "Debit Card": ["debit card", "DC"]}
    for k, alts in pay_alt.items():
        mm = (o["payment_method"] == k) & (rng.random(len(o)) < 0.2)
        o.loc[mm, "payment_method"] = rng.choice(alts, mm.sum())
    o = pd.concat([o, o.sample(frac=0.01, random_state=SEED)]).sort_values("order_id").reset_index(drop=True)

    it = items.copy()
    idx = it.sample(n=40, random_state=SEED).index
    it.loc[idx, "quantity"] = -it.loc[idx, "quantity"]                # sign errors
    idx = it.sample(n=15, random_state=SEED + 2).index
    it.loc[idx, "unit_price"] = it.loc[idx, "unit_price"] * 100        # paise entered as rupees
    idx = it.sample(n=25, random_state=SEED + 3).index
    it.loc[idx, "unit_price"] = np.nan                                 # missing price
    it["discount"] = it["discount"].astype(object)
    it.loc[it["discount"] == 0, "discount"] = ""                      # blanks instead of 0
    return c, o, it


def main():
    CLEAN.mkdir(exist_ok=True)
    RAW.mkdir(exist_ok=True)
    products = make_products()
    customers = make_customers()
    orders, items = make_orders(customers, products)
    sessions = make_sessions(customers)
    experiment = make_experiment()
    employees = make_employees()

    tables = {"customers": customers, "products": products, "orders": orders,
              "order_items": items, "web_sessions": sessions,
              "checkout_experiment": experiment, "employees": employees}
    for name, df in tables.items():
        df.to_csv(CLEAN / f"{name}.csv", index=False, lineterminator="\n")

    c_raw, o_raw, i_raw = make_raw(customers, orders, items, products)
    c_raw.to_csv(RAW / "customers_raw.csv", index=False, lineterminator="\n")
    o_raw.to_csv(RAW / "orders_raw.csv", index=False, lineterminator="\n")
    i_raw.to_csv(RAW / "order_items_raw.csv", index=False, lineterminator="\n")
    products.to_csv(RAW / "products.csv", index=False, lineterminator="\n")

    if DB_PATH.exists():
        DB_PATH.unlink()
    con = sqlite3.connect(DB_PATH)
    schema = (ROOT / "schema.sql").read_text(encoding="utf-8")
    con.executescript(schema)
    for name, df in tables.items():
        df.to_sql(name, con, if_exists="append", index=False)
    con.commit()
    con.execute("VACUUM")
    con.close()

    for name, df in tables.items():
        print(f"{name:<20} {len(df):>7,} rows")
    print(f"\nWrote {CLEAN}, {RAW} and {DB_PATH}")


if __name__ == "__main__":
    main()
