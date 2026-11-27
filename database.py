
import sqlite3
import hashlib
import secrets
import hmac
from contextlib import contextmanager


class Database:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)

        return cls._instance

    def __init__(self):
        if not hasattr(self, "db_name"):
            self.db_name = "support.db"

    @contextmanager
    def connect(self):
        conn = sqlite3.connect(self.db_name)
        conn.execute("PRAGMA foreign_keys = ON")

        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def create_tables(self):
        with self.connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    role TEXT NOT NULL
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS tickets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    category TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    status TEXT DEFAULT 'Open',
                    user_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)

    def hash_password(self, password, salt=None):
        if salt is None:
            salt = secrets.token_hex(16)

        password_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            100000
        ).hex()

        return password_hash, salt

    def add_user(self, username, password, role):
        password_hash, salt = self.hash_password(password)

        with self.connect() as conn:
            conn.execute("""
                INSERT INTO users
                (username, password_hash, salt, role)
                VALUES (?, ?, ?, ?)
            """, (username, password_hash, salt, role))

    def verify_user(self, username, password):
        with self.connect() as conn:
            user = conn.execute("""
                SELECT id, username, password_hash, salt, role
                FROM users
                WHERE username = ?
            """, (username,)).fetchone()

        if user is None:
            return None

        password_hash, _ = self.hash_password(password, user[3])

        if hmac.compare_digest(password_hash, user[2]):
            return {
                "id": user[0],
                "username": user[1],
                "role": user[4]
            }

        return None

    def initialize(self):
        self.create_tables()

        with self.connect() as conn:
            count = conn.execute(
                "SELECT COUNT(*) FROM users"
            ).fetchone()[0]

        if count == 0:
            self.add_user("admin", "admin123", "Admin")
            self.add_user("user", "user123", "User")
            self.add_user("support", "support123", "IT Support")

    def create_ticket(
        self, title, description, category, priority, user_id
    ):
        with self.connect() as conn:
            conn.execute("""
                INSERT INTO tickets
                (title, description, category, priority, user_id)
                VALUES (?, ?, ?, ?, ?)
            """, (title, description, category, priority, user_id))

    def get_tickets(self, user_id, role):
        with self.connect() as conn:
            if role in ["Admin", "IT Support"]:
                tickets = conn.execute("""
                    SELECT id, title, description, category,
                           priority, status, user_id
                    FROM tickets
                    ORDER BY id DESC
                """).fetchall()
            else:
                tickets = conn.execute("""
                    SELECT id, title, description, category,
                           priority, status, user_id
                    FROM tickets
                    WHERE user_id = ?
                    ORDER BY id DESC
                """, (user_id,)).fetchall()

        return tickets

    def get_ticket(self, ticket_id):
        with self.connect() as conn:
            return conn.execute("""
                   SELECT id, title, description, category,
                          priority, status, user_id
                   FROM tickets
                   WHERE id = ?
               """, (ticket_id,)).fetchone()

    def update_ticket_status(self, ticket_id, status):
        allowed_statuses = ["Open", "In Progress", "Closed"]

        if status not in allowed_statuses:
            raise ValueError("Invalid ticket status")

        with self.connect() as conn:
            conn.execute("""
                UPDATE tickets
                SET status = ?
                WHERE id = ?
            """, (status, ticket_id))

    def get_ticket_stats(self, user_id, role):
        with self.connect() as conn:
            if role in ["Admin", "IT Support"]:
                tickets = conn.execute("""
                    SELECT status, COUNT(*)
                    FROM tickets
                    GROUP BY status
                """).fetchall()
            else:
                tickets = conn.execute("""
                    SELECT status, COUNT(*)
                    FROM tickets
                    WHERE user_id = ?
                    GROUP BY status
                """, (user_id,)).fetchall()

        stats = {
            "total": 0,
            "open": 0,
            "progress": 0,
            "closed": 0
        }

        for status, count in tickets:
            stats["total"] += count

            if status == "Open":
                stats["open"] = count
            elif status == "In Progress":
                stats["progress"] = count
            elif status == "Closed":
                stats["closed"] = count

        return stats

    def get_recent_tickets(self, user_id, role):
        with self.connect() as conn:
            if role in ["Admin", "IT Support"]:
                tickets = conn.execute("""
                    SELECT id, title, category, status
                    FROM tickets
                    ORDER BY id DESC
                    LIMIT 5
                """).fetchall()
            else:
                tickets = conn.execute("""
                    SELECT id, title, category, status
                    FROM tickets
                    WHERE user_id = ?
                    ORDER BY id DESC
                    LIMIT 5
                """, (user_id,)).fetchall()

        return tickets
