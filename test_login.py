import sqlite3

email = "navya@example.com"
password = "navya123@"

connection = sqlite3.connect("shop.db")

user = connection.execute(
    "SELECT user_id, name, email FROM users WHERE email = ? AND password = ?",
    (email, password)
).fetchone()

print("LOGIN RESULT:", user)

connection.close()
