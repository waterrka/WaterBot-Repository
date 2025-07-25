import sqlite3

OWNER_ID = {679722204144992262, 748212381347479743}

class BalanceService:
    def __init__(self, db_path='economy.db'):
        self.db = sqlite3.connect(db_path)
        self.cursor = self.db.cursor()
        self._init_db()

    def _init_db(self):
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS balances (
            user_id INTEGER PRIMARY KEY,
            balance INTEGER NOT NULL DEFAULT 0
        )
        ''')
        self.db.commit()

    def get_balance(self, user_id: int) -> int:
        if user_id in OWNER_ID:
            return float('inf')

        self.cursor.execute("SELECT balance FROM balances WHERE user_id = ?", (user_id,))
        result = self.cursor.fetchone()
        return result[0] if result else 0

    def update_balance(self, user_id: int, amount: int) -> int:
        if user_id in OWNER_ID:
            return float('inf')

        current_balance = self.get_balance(user_id)
        new_balance = max(current_balance + amount, 0)

        self.cursor.execute(
            "INSERT OR REPLACE INTO balances (user_id, balance) VALUES (?, ?)",
            (user_id, new_balance)
        )
        self.db.commit()
        return new_balance

    def get_all_users(self):
        self.cursor.execute(
            "SELECT user_id FROM balances WHERE user_id NOT IN ({})"
            .format(','.join(['?'] * len(OWNER_ID))),
            tuple(OWNER_ID)
        )
        return [row[0] for row in self.cursor.fetchall()]
    
    def get_all_balances_except_owners(self):
        self.cursor.execute(
            "SELECT user_id, balance FROM balances WHERE user_id NOT IN ({seq}) ORDER BY balance DESC"
            .format(seq=','.join(['?'] * len(OWNER_ID))),
            tuple(OWNER_ID)
        )
        return self.cursor.fetchall()