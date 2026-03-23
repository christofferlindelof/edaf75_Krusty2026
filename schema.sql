PRAGMA foreign_keys = ON;
DROP TABLE IF EXISTS order_lines;
DROP TABLE IF EXISTS pallets;
DROP TABLE IF EXISTS recipes;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS ingredients;
DROP TABLE IF EXISTS cookies;

CREATE TABLE ingredients(
    ingredient TEXT PRIMARY KEY,
    unit TEXT,
    quantity INTEGER DEFAULT 0 
);

CREATE TABLE customers(
    name TEXT PRIMARY KEY,
    address TEXT
);

CREATE TABLE orders(
    id TEXT DEFAULT (lower(hex(randomblob(16)))) PRIMARY KEY,
    customer_name TEXT,
    FOREIGN KEY (customer_name) REFERENCES customers(name)
);

CREATE TABLE cookies(
    name TEXT PRIMARY KEY
);

CREATE TABLE recipes(
    cookie_name TEXT,
    ingredient_name TEXT,
    amount INTEGER,
    PRIMARY KEY (cookie_name, ingredient_name),
    FOREIGN KEY (cookie_name) REFERENCES cookies(name),
    FOREIGN KEY (ingredient_name) REFERENCES ingredients(ingredient)
);

CREATE TABLE pallets(
    id TEXT DEFAULT (lower(hex(randomblob(16)))) PRIMARY KEY, 
    cookie_name TEXT,
    creation_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    blocked INTEGER DEFAULT 0, 
    delivered DATETIME,
    order_id TEXT,
    location TEXT,
    FOREIGN KEY (cookie_name) REFERENCES cookies(name),
    FOREIGN KEY (order_id) REFERENCES orders(id)
);

CREATE TABLE order_lines(
    order_id TEXT,
    cookie_name TEXT,
    quantity INTEGER,
    PRIMARY KEY (order_id, cookie_name),
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (cookie_name) REFERENCES cookies(name)
);



CREATE TRIGGER enough_ingredients(
    BEFORE INSERT ON pallets
    WHEN(

    )
)



-- Triggers, före och efter insert på pallets. 
