import psycopg2

# Database connection details (Using your Railway PostgreSQL)
DB_URL = "postgresql://postgres:vVMyqWjrqgVhEnwyFifTQxkDtPjQutGb@interchange.proxy.rlwy.net:30451/railway"

def connect_db():
    """Connects to the PostgreSQL database and returns the connection."""
    try:
        conn = psycopg2.connect(DB_URL)
        return conn
    except Exception as e:
        print("Database connection failed:", e)
        return None

def create_table():
    """Creates the users table if it doesn't exist and adds joined_channel column if missing."""
    conn = connect_db()
    if conn:
        try:
            cur = conn.cursor()

            # ✅ Create the users table (if not exists) with joined_channel column
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    chat_id BIGINT NOT NULL,
                    name TEXT NOT NULL,
                    username TEXT NOT NULL,
                    contact TEXT NOT NULL,
                    email TEXT NOT NULL,
                    joined_channel BOOLEAN DEFAULT FALSE  -- ✅ New column added
                );
            """)

            conn.commit()
            cur.close()
            conn.close()
            print("Table created/updated successfully.")
        except Exception as e:
            print("Error creating/updating table:", e)

def update_channel_status(user_id, joined_channel):
    """Updates the user's channel membership status in the database."""
    conn = connect_db()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("UPDATE users SET joined_channel = %s WHERE user_id = %s;", (joined_channel, user_id))
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            print("Error updating channel status:", e)

def get_user_status(user_id):
    """Retrieves user's channel membership status from the database."""
    conn = connect_db()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT joined_channel FROM users WHERE user_id = %s;", (user_id,))
            result = cur.fetchone()
            cur.close()
            conn.close()
            return result[0] if result else False  # Default to False if no record found
        except Exception as e:
            print("Error fetching user status:", e)
            return False


# Run this function once to create/update the table
if __name__ == "__main__":
    create_table()
