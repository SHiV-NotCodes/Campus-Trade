# ==========================================
# FILE: users.py
# PURPOSE: Handles user registration and storage
# ==========================================

# This list will act as our "database" to store registered users.
# Each user will be stored as a dictionary.
# For easy testing, we pre-populate it with two sample students:
users_list = [
    { "name": "Aditya Kumar", "email": "aditya@miet.ac.in", "password": "password123" },
    { "name": "Rohan Sharma", "email": "rohan@miet.ac.in", "password": "rohanpass" }
]


def register_user(name, email, password):
    """
    Registers a new user after validation.
    
    Parameters:
    - name (str): The name of the student.
    - email (str): The student's college email.
    - password (str): The password chosen by the student.
    
    Returns:
    - tuple: (bool, str) -> (True/False representing success, a message explaining the result)
    """
    
    # Clean the email input (remove extra spaces and make it lowercase for consistent validation)
    email = email.strip().lower()
    
    # 1. Validation check: Email must end with "@miet.ac.in"
    # We use python's built-in .endswith() method for this.
    if not email.endswith("@miet.ac.in"):
        return False, "Registration failed! Only MIET college emails (@miet.ac.in) are allowed."
        
    # 2. Validation check: Ensure the name, email, or password is not empty
    if not name.strip() or not password.strip():
        return False, "Registration failed! Name, email, and password cannot be empty."
        
    # 3. Duplicate check: Ensure this email is not already registered.
    # We loop through all users in users_list and check if any user has the same email.
    for user in users_list:
        if user["email"] == email:
            return False, "Registration failed! This email is already registered."
            
    # 4. Save the user: Create a new dictionary and append it to our list.
    new_user = {
        "name": name.strip(),
        "email": email,
        "password": password.strip()
    }
    
    # Add the dictionary to our list of users
    users_list.append(new_user)
    
    # Return success
    return True, f"Registration successful! Welcome, {name}."

def login_user(email, password):
    """
    Validates user credentials for logging in.
    
    Parameters:
    - email (str): The college email entered by the user.
    - password (str): The password entered by the user.
    
    Returns:
    - dict: The user dictionary if login is successful.
    - None: If login fails (email not found or password incorrect).
    """
    # Clean the email input
    email = email.strip().lower()
    
    # Loop through the list of registered users
    for user in users_list:
        # Check if both email and password match
        if user["email"] == email and user["password"] == password.strip():
            return user # Return the matching user dictionary
            
    # If the loop finishes and no match is found, return None
    return None
