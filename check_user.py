import sqlite3

connection = sqlite3.connect("shop.db")

users = connection.execute(
    "SELECT user_id, name, email, password FROM users"
).fetchall()

print(users)

connection.close()