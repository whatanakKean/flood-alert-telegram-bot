import sqlite3

class UserManager:
    def __init__(self, db_path='database.db'):
        """Initialize the UserManager with SQLite database."""
        self.db_path = db_path
        self._init_sqlite()

    def _init_sqlite(self):
        """Initialize SQLite database and create users and subscriptions tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                first_name TEXT,
                username TEXT,
                chat_id INTEGER
            )
        ''')

        # Create subscriptions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subscriptions (
                user_id INTEGER,
                station TEXT,
                PRIMARY KEY (user_id, station),
                FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
            )
        ''')

        conn.commit()
        conn.close()

    def save_user(self, user_id, first_name, username, chat_id):
        """Save or update user info in the SQLite database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO users (user_id, first_name, username, chat_id)
            VALUES (?, ?, ?, ?)
        ''', (user_id, first_name, username, chat_id))
        conn.commit()
        conn.close()

    def get_user(self, user_id):
        """Retrieve a single user's data from the SQLite database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()
        if user:
            return {
                'user_id': user[0],
                'first_name': user[1],
                'username': user[2],
                'chat_id': user[3]
            }
        return None

    def get_all_users(self):
        """Retrieve all users' data from the SQLite database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users')
        users = cursor.fetchall()
        conn.close()

        # Convert the list of tuples to a dictionary
        user_dict = {}
        for user in users:
            user_dict[user[0]] = {
                'first_name': user[1],
                'username': user[2],
                'chat_id': user[3],
            }
        return user_dict

    def delete_user(self, user_id):
        """Delete a user from the SQLite database by their user ID."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
        conn.commit()
        conn.close()

    def update_user_chat_id(self, user_id, new_chat_id):
        """Update a user's chat_id in the SQLite database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users
            SET chat_id = ?
            WHERE user_id = ?
        ''', (new_chat_id, user_id))
        conn.commit()
        conn.close()

    def subscribe_user(self, user_id, station):
        """Subscribe the user to a station."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO subscriptions (user_id, station)
            VALUES (?, ?)
        ''', (user_id, station))
        conn.commit()
        conn.close()

    def unsubscribe_user(self, user_id, station):
        """Unsubscribe the user from a station."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM subscriptions WHERE user_id = ? AND station = ?', (user_id, station))
        conn.commit()
        conn.close()

    def get_subscribed_users(self):
        """Retrieve all subscribed users with their stations."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT u.user_id, u.first_name, u.username, u.chat_id, s.station
            FROM users u
            JOIN subscriptions s ON u.user_id = s.user_id
        ''')
        users = cursor.fetchall()
        conn.close()

        # Structure data for easy access
        subscribed_users = {}
        for user in users:
            user_id = user[0]
            if user_id not in subscribed_users:
                subscribed_users[user_id] = {
                    'first_name': user[1],
                    'username': user[2],
                    'chat_id': user[3],
                    'stations': []
                }
            subscribed_users[user_id]['stations'].append(user[4])
        return subscribed_users

    def get_user_stations(self, user_id):
        """Get all subscribed stations for a user."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT station FROM subscriptions WHERE user_id = ?', (user_id,))
        stations = cursor.fetchall()
        conn.close()
        return [station[0] for station in stations]

    def is_user_subscribed(self, user_id, station):
        """Check if the user is subscribed to a specific station."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'SELECT 1 FROM subscriptions WHERE user_id = ? AND station = ?',
            (user_id, station)
        )
        is_subscribed = cursor.fetchone() is not None  # True if subscription exists, else False
        conn.close()
        return is_subscribed