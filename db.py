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
    """Creates the users table if it doesn't exist."""
    conn = connect_db()
    if conn:
        try:
            cur = conn.cursor()

            # ✅ Create the users table (if not exists) without the 'joined_channel' column
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    chat_id BIGINT NOT NULL,
                    name TEXT NOT NULL,
                    username TEXT NOT NULL,
                    contact TEXT NOT NULL,
                    email TEXT NOT NULL
                );
            """)

            conn.commit()
            cur.close()
            conn.close()
            print("Table created/updated successfully.")
        except Exception as e:
            print("Error creating/updating table:", e)

def get_user_status(user_id):
    """Retrieves user's status from the database (checks if the user exists)."""
    conn = connect_db()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT 1 FROM users WHERE user_id = %s;", (user_id,))
            result = cur.fetchone()
            cur.close()
            conn.close()
            return result is not None  # Returns True if user exists, otherwise False
        except Exception as e:
            print("Error fetching user status:", e)
            return False

# Run this function once to create/update the table
if __name__ == "__main__":
    create_table()
