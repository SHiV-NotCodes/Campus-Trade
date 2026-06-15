import sqlite3
import os

def get_db_connection(db_path):
    """
    Creates and returns a connection to the SQLite database.
    Configures row factory to return dictionary-like row objects.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    # Enable foreign key support
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db(db_path):
    """
    Initializes the database by creating the users and listings tables if they don't exist.
    If an older schema is detected (e.g. from the Clerk implementation), it recreates the DB.
    """
    # Ensure parent directory exists for database file
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
        
    # Check if database has old schema (lacking password_hash column)
    if os.path.exists(db_path):
        conn = get_db_connection(db_path)
        cursor = conn.cursor()
        try:
            # Check if password_hash column exists in users
            cursor.execute("SELECT password_hash FROM users LIMIT 1")
            conn.close()
        except sqlite3.OperationalError:
            conn.close()
            print("Old Clerk-based schema detected. Re-initializing database for local authentication...")
            try:
                if os.path.exists(db_path):
                    os.remove(db_path)
            except Exception as e:
                print(f"Could not remove old database file: {e}")

    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    
    # Create users table with local authentication fields
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        name TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    # Create listings table referencing users
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS listings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        price REAL NOT NULL,
        category TEXT NOT NULL,
        contact_info TEXT NOT NULL,
        image_path TEXT,
        seller_id INTEGER NOT NULL,
        is_sold INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (seller_id) REFERENCES users (id) ON DELETE CASCADE
    );
    """)
    
    conn.commit()
    conn.close()
    print("Database tables initialized successfully.")

def create_user(db_path, username, email, password_hash, name):
    """
    Registers a new student user in the database.
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, email, password_hash, name) VALUES (?, ?, ?, ?)",
            (username.lower().strip(), email.lower().strip(), password_hash, name.strip())
        )
        conn.commit()
        user_id = cursor.lastrowid
        return user_id
    except sqlite3.IntegrityError as e:
        # Detect unique constraint violations (username or email already exists)
        err_msg = str(e).lower()
        if "username" in err_msg:
            raise ValueError("Username is already taken.")
        elif "email" in err_msg:
            raise ValueError("Email is already registered.")
        else:
            raise ValueError("Username or Email already exists.")
    finally:
        conn.close()

def get_user_by_id(db_path, user_id):
    """
    Retrieves a user row by their database ID.
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    user = dict(row) if row else None
    conn.close()
    return user

def get_user_by_email_or_username(db_path, identifier):
    """
    Retrieves a user row by their username or email address (case-insensitive).
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE LOWER(username) = ? OR LOWER(email) = ?",
        (identifier.lower().strip(), identifier.lower().strip())
    )
    row = cursor.fetchone()
    user = dict(row) if row else None
    conn.close()
    return user

def create_listing(db_path, title, description, price, category, contact_info, image_path, seller_id):
    """
    Inserts a new listing into the database.
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO listings (title, description, price, category, contact_info, image_path, seller_id, is_sold)
        VALUES (?, ?, ?, ?, ?, ?, ?, 0)
        """,
        (title, description, float(price), category, contact_info, image_path, seller_id)
    )
    conn.commit()
    listing_id = cursor.lastrowid
    conn.close()
    return listing_id

def get_listings(db_path, category=None, search_query=None, seller_id=None):
    """
    Retrieves listings from the database with optional filters.
    Includes the seller's name.
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    
    query = """
        SELECT l.*, u.name as seller_name
        FROM listings l
        JOIN users u ON l.seller_id = u.id
        WHERE 1=1
    """
    params = []
    
    if category:
        query += " AND l.category = ?"
        params.append(category)
        
    if search_query:
        query += " AND (l.title LIKE ? OR l.description LIKE ?)"
        search_param = f"%{search_query}%"
        params.append(search_param)
        params.append(search_param)
        
    if seller_id:
        query += " AND l.seller_id = ?"
        params.append(int(seller_id))
        
    # Order by newest first
    query += " ORDER BY l.created_at DESC"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    listings = [dict(row) for row in rows]
    conn.close()
    return listings

def get_listing_by_id(db_path, listing_id):
    """
    Retrieves a single listing by its ID, including seller information.
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    
    cursor.execute(
        """
        SELECT l.*, u.name as seller_name, u.email as seller_email
        FROM listings l
        JOIN users u ON l.seller_id = u.id
        WHERE l.id = ?
        """,
        (listing_id,)
    )
    row = cursor.fetchone()
    listing = dict(row) if row else None
    conn.close()
    return listing

def update_listing(db_path, listing_id, title, description, price, category, contact_info, image_path, seller_id):
    """
    Updates an existing listing. Verifies that the request comes from the listing owner.
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    
    # Verify ownership
    cursor.execute(
        "SELECT id FROM listings WHERE id = ? AND seller_id = ?",
        (listing_id, seller_id)
    )
    if not cursor.fetchone():
        conn.close()
        raise PermissionError("User is not authorized to edit this listing.")
        
    if image_path:
        cursor.execute(
            """
            UPDATE listings
            SET title = ?, description = ?, price = ?, category = ?, contact_info = ?, image_path = ?
            WHERE id = ?
            """,
            (title, description, float(price), category, contact_info, image_path, listing_id)
        )
    else:
        cursor.execute(
            """
            UPDATE listings
            SET title = ?, description = ?, price = ?, category = ?, contact_info = ?
            WHERE id = ?
            """,
            (title, description, float(price), category, contact_info, listing_id)
        )
        
    conn.commit()
    conn.close()
    return True

def delete_listing(db_path, listing_id, seller_id):
    """
    Deletes a listing from the database. Verifies ownership.
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    
    # Verify ownership
    cursor.execute(
        "SELECT id, image_path FROM listings WHERE id = ? AND seller_id = ?",
        (listing_id, seller_id)
    )
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise PermissionError("User is not authorized to delete this listing.")
        
    image_path = row['image_path']
    
    # Delete from database
    cursor.execute("DELETE FROM listings WHERE id = ?", (listing_id,))
    conn.commit()
    conn.close()
    
    return image_path

def mark_listing_as_sold(db_path, listing_id, seller_id, is_sold=1):
    """
    Updates the is_sold field of a listing. Verifies ownership.
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    
    # Verify ownership
    cursor.execute(
        "SELECT id FROM listings WHERE id = ? AND seller_id = ?",
        (listing_id, seller_id)
    )
    if not cursor.fetchone():
        conn.close()
        raise PermissionError("User is not authorized to modify this listing status.")
        
    cursor.execute(
        "UPDATE listings SET is_sold = ? WHERE id = ?",
        (is_sold, listing_id)
    )
    conn.commit()
    conn.close()
    return True

def get_user_stats(db_path, user_id):
    """
    Calculates statistics for a specific user: name, email, active/sold counts.
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    
    # Get user profile information
    cursor.execute("SELECT name, email, created_at FROM users WHERE id = ?", (user_id,))
    user_row = cursor.fetchone()
    if not user_row:
        conn.close()
        return None
        
    # Get active listings count (is_sold = 0)
    cursor.execute("SELECT COUNT(*) as active_count FROM listings WHERE seller_id = ? AND is_sold = 0", (user_id,))
    active_count = cursor.fetchone()['active_count']
    
    # Get sold listings count (is_sold = 1)
    cursor.execute("SELECT COUNT(*) as sold_count FROM listings WHERE seller_id = ? AND is_sold = 1", (user_id,))
    sold_count = cursor.fetchone()['sold_count']
    
    conn.close()
    
    return {
        "name": user_row['name'],
        "email": user_row['email'],
        "created_at": user_row['created_at'],
        "active_listings": active_count,
        "sold_listings": sold_count
    }
