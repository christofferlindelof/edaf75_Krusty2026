from bottle import get, post, run, request, response
import sqlite3
from urllib.parse import quote, unquote


db = sqlite3.connect('krusty.db')


@post('/reset')
def reset():
    c = db.cursor()
    sql_commands = open("schema.sql","r").read()
    c.executescript(sql_commands)
    db.commit()
    response.status = 205
    return {"location": "/"}


from bottle import post, request, response
from urllib.parse import quote
import sqlite3

@post('/customers')
def add_customer():
    c = db.cursor()  
    inData = request.json
    name = inData.get('name')
    address = inData.get('address')
    c.execute('''INSERT INTO customers (name, address) VALUES (?, ?)''', (name, address))
    db.commit()
    db.close()
    url_encoded_name = quote(name)
    response.status = 201
    return {"location": "/customers/" + url_encoded_name}

@get('/customers')
def get_customers():
    c = db.cursor()
    c.execute('''SELECT name, address FROM customers''')
    customers = c.fetchall()
    customer_list = []

    for line in customers: 
        d = {
            "name": line[0],
            "address": line[1]
        }
        customer_list.append(d)
    response.status = 200
    return{"data": customer_list}









