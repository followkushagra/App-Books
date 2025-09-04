import sqlite3

class BookDB:
    def __init__(self, db_path="books.db"):
        self.conn = sqlite3.connect(db_path)
        self.create_table()

    def create_table(self):
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS books(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            path TEXT
        )
        """)
        self.conn.commit()

    def add_book(self, title, path):
        self.conn.execute("INSERT INTO books (title, path) VALUES (?, ?)", (title, path))
        self.conn.commit()

    def get_books(self):
        return self.conn.execute("SELECT * FROM books").fetchall()