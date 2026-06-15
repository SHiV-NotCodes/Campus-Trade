import os
import uuid
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

import models

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-12345')
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB file upload limit

# Resolve database path
db_path = os.getenv('DATABASE_PATH', 'database.db')
if not os.path.isabs(db_path):
    db_path = os.path.join(app.root_path, db_path)
app.config['DATABASE_PATH'] = db_path

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'login'  # Redirect target for unauthenticated users
login_manager.login_message_category = 'danger'
login_manager.init_app(app)

# User Model class for Flask-Login
class User(UserMixin):
    def __init__(self, id, username, email, name):
        self.id = id
        self.username = username
        self.email = email
        self.name = name

@login_manager.user_loader
def load_user(user_id):
    """
    Loads user from SQLite DB using their integer user ID.
    """
    db_user = models.get_user_by_id(app.config['DATABASE_PATH'], int(user_id))
    if db_user:
        return User(
            id=db_user['id'],
            username=db_user['username'],
            email=db_user['email'],
            name=db_user['name']
        )
    return None

# Initialize DB on start
with app.app_context():
    models.init_db(app.config['DATABASE_PATH'])


# --- USER AUTHENTICATION ROUTES ---

@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Sign Up page. Validates user input, hashes password, and saves user to SQLite.
    """
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        name = request.form.get('name', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validation
        errors = []
        if not all([username, email, name, password, confirm_password]):
            errors.append("All fields are required.")
            
        if len(password) < 6:
            errors.append("Password must be at least 6 characters long.")
            
        if password != confirm_password:
            errors.append("Passwords do not match.")
            
        if errors:
            return render_template('register.html', errors=errors, form_data=request.form)
            
        # Hash password and save user
        password_hash = generate_password_hash(password)
        try:
            models.create_user(
                app.config['DATABASE_PATH'],
                username=username,
                email=email,
                password_hash=password_hash,
                name=name
            )
            flash("Registration successful! Please sign in.", "success")
            return redirect(url_for('login'))
        except ValueError as e:
            return render_template('register.html', errors=[str(e)], form_data=request.form)
            
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Sign In page. Validates login credentials and starts user session.
    """
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    errors = []
    if request.method == 'POST':
        identifier = request.form.get('identifier', '').strip()
        password = request.form.get('password', '')
        
        if not identifier or not password:
            errors.append("All fields are required.")
        else:
            db_user = models.get_user_by_email_or_username(app.config['DATABASE_PATH'], identifier)
            if db_user and check_password_hash(db_user['password_hash'], password):
                # Login user session
                user_obj = User(
                    id=db_user['id'],
                    username=db_user['username'],
                    email=db_user['email'],
                    name=db_user['name']
                )
                login_user(user_obj)
                
                # Check for redirect parameter
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('index'))
            else:
                errors.append("Invalid username/email or password.")
                
    return render_template('login.html', errors=errors)

@app.route('/logout')
@login_required
def logout():
    """
    Logs out the user and clears the session.
    """
    logout_user()
    flash("You have logged out successfully.", "success")
    return redirect(url_for('index'))


# --- HTML TEMPLATE PAGE ROUTES ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/listings')
def listings_page():
    return render_template('listings.html')

@app.route('/listings/<int:listing_id>')
def listing_detail_page(listing_id):
    return render_template('listing_detail.html', listing_id=listing_id)

@app.route('/create-listing')
@login_required
def create_listing_page():
    return render_template('create_listing.html')

@app.route('/edit-listing/<int:listing_id>')
@login_required
def edit_listing_page(listing_id):
    # Verify user owns the listing before rendering the edit page
    listing = models.get_listing_by_id(app.config['DATABASE_PATH'], listing_id)
    if not listing:
        flash("Listing not found.", "danger")
        return redirect(url_for('listings_page'))
    if listing['seller_id'] != current_user.id:
        flash("You are not authorized to edit this listing.", "danger")
        return redirect(url_for('listings_page'))
        
    return render_template('edit_listing.html', listing_id=listing_id)

@app.route('/my-listings')
@login_required
def my_listings_page():
    return render_template('my_listings.html')

@app.route('/profile')
@login_required
def profile_page():
    return render_template('profile.html')


# --- REST API ENDPOINTS ---

@app.route('/api/listings', methods=['GET'])
def get_all_listings():
    """
    Fetches all listings with optional category, search, or seller filters.
    """
    category = request.args.get('category')
    search = request.args.get('search')
    seller = request.args.get('seller')  # Seller user ID
    
    if category == 'all' or category == '':
        category = None
        
    try:
        listings = models.get_listings(
            app.config['DATABASE_PATH'],
            category=category,
            search_query=search,
            seller_id=seller
        )
        return jsonify(listings)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/listings/<int:listing_id>', methods=['GET'])
def get_single_listing(listing_id):
    """
    Fetches a single listing by ID.
    """
    try:
        listing = models.get_listing_by_id(app.config['DATABASE_PATH'], listing_id)
        if not listing:
            return jsonify({"error": "Listing not found"}), 404
        return jsonify(listing)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/listings', methods=['POST'])
def add_new_listing():
    """
    Creates a new listing. Protects endpoint and associates it with the logged-in user.
    """
    if not current_user.is_authenticated:
        return jsonify({"error": "Authentication required to post listing"}), 401
        
    title = request.form.get('title')
    description = request.form.get('description')
    price = request.form.get('price')
    category = request.form.get('category')
    contact_info = request.form.get('contact_info')
    
    if not all([title, description, price, category, contact_info]):
        return jsonify({"error": "All fields are required"}), 400
        
    try:
        price_val = float(price)
        if price_val < 0:
            return jsonify({"error": "Price cannot be negative"}), 400
    except ValueError:
        return jsonify({"error": "Invalid price format"}), 400
        
    # Handle image upload
    image_path = None
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename != '':
            ext = os.path.splitext(file.filename)[1].lower()
            if ext not in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                return jsonify({"error": "Allowed image extensions are jpg, jpeg, png, gif, webp"}), 400
                
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(save_path)
            image_path = f"/static/uploads/{unique_filename}"
            
    try:
        listing_id = models.create_listing(
            app.config['DATABASE_PATH'],
            title=title,
            description=description,
            price=price_val,
            category=category,
            contact_info=contact_info,
            image_path=image_path,
            seller_id=current_user.id
        )
        return jsonify({"success": True, "listing_id": listing_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/listings/<int:listing_id>', methods=['PUT'])
def edit_existing_listing(listing_id):
    """
    Edits a listing. Verifies ownership.
    """
    if not current_user.is_authenticated:
        return jsonify({"error": "Authentication required"}), 401
        
    title = request.form.get('title')
    description = request.form.get('description')
    price = request.form.get('price')
    category = request.form.get('category')
    contact_info = request.form.get('contact_info')
    
    if not all([title, description, price, category, contact_info]):
        return jsonify({"error": "All fields are required"}), 400
        
    try:
        price_val = float(price)
        if price_val < 0:
            return jsonify({"error": "Price cannot be negative"}), 400
    except ValueError:
        return jsonify({"error": "Invalid price format"}), 400
        
    # Handle image upload
    image_path = None
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename != '':
            ext = os.path.splitext(file.filename)[1].lower()
            if ext not in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                return jsonify({"error": "Allowed image extensions are jpg, jpeg, png, gif, webp"}), 400
                
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(save_path)
            image_path = f"/static/uploads/{unique_filename}"
            
    try:
        # Delete old image if updating
        if image_path:
            old_listing = models.get_listing_by_id(app.config['DATABASE_PATH'], listing_id)
            if old_listing and old_listing['image_path']:
                old_file = old_listing['image_path'].lstrip('/')
                full_path = os.path.join(app.root_path, old_file)
                if os.path.exists(full_path):
                    try:
                        os.remove(full_path)
                    except Exception as e:
                        print(f"Failed to delete old image file: {e}")
                        
        models.update_listing(
            app.config['DATABASE_PATH'],
            listing_id=listing_id,
            title=title,
            description=description,
            price=price_val,
            category=category,
            contact_info=contact_info,
            image_path=image_path,
            seller_id=current_user.id
        )
        return jsonify({"success": True})
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/listings/<int:listing_id>', methods=['DELETE'])
def remove_listing(listing_id):
    """
    Deletes a listing. Verifies ownership.
    """
    if not current_user.is_authenticated:
        return jsonify({"error": "Authentication required"}), 401
        
    try:
        image_path = models.delete_listing(
            app.config['DATABASE_PATH'],
            listing_id,
            current_user.id
        )
        
        if image_path:
            rel_path = image_path.lstrip('/')
            full_path = os.path.join(app.root_path, rel_path)
            if os.path.exists(full_path):
                try:
                    os.remove(full_path)
                except Exception as e:
                    print(f"Failed to delete file from disk: {e}")
                    
        return jsonify({"success": True})
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/listings/<int:listing_id>/sold', methods=['PATCH'])
def toggle_listing_sold(listing_id):
    """
    Toggles is_sold status. Verifies ownership.
    """
    if not current_user.is_authenticated:
        return jsonify({"error": "Authentication required"}), 401
        
    data = request.json or {}
    is_sold = data.get('is_sold', 1)
    
    if is_sold not in [0, 1]:
        return jsonify({"error": "Invalid sold status"}), 400
        
    try:
        models.mark_listing_as_sold(
            app.config['DATABASE_PATH'],
            listing_id,
            current_user.id,
            is_sold
        )
        return jsonify({"success": True})
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/profile', methods=['GET'])
def get_profile_data():
    """
    Gets profile statistics for current user.
    """
    if not current_user.is_authenticated:
        return jsonify({"error": "Authentication required"}), 401
        
    try:
        stats = models.get_user_stats(app.config['DATABASE_PATH'], current_user.id)
        if not stats:
            return jsonify({"error": "Profile not found"}), 404
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
