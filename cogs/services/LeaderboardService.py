import sqlite3

class LeaderboardService:
    def __init__(self, db_path='economy.db'):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    def get_leaderboard(self, page=1, per_page=10, exclude_user_ids=None):
        offset = (page - 1) * per_page
        exclude_user_ids = exclude_user_ids or []

        query = "SELECT user_id, balance FROM balances"
        params = []

        if exclude_user_ids:
            placeholders = ",".join("?" for _ in exclude_user_ids)
            query += f" WHERE user_id NOT IN ({placeholders})"
            params.extend(exclude_user_ids)

        query += " ORDER BY balance DESC LIMIT ? OFFSET ?"
        params.extend([per_page, offset])

        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def get_total_count(self, exclude_user_ids=None):
        exclude_user_ids = exclude_user_ids or []
        query = "SELECT COUNT(*) FROM balances"
        params = []

        if exclude_user_ids:
            placeholders = ",".join("?" for _ in exclude_user_ids)
            query += f" WHERE user_id NOT IN ({placeholders})"
            params.extend(exclude_user_ids)

        self.cursor.execute(query, params)
        return self.cursor.fetchone()[0]