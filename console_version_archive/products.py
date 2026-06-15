# ==========================================
# FILE: products.py
# PURPOSE: Handles product addition, storage, and retrieval
# ==========================================

# This list will store our products.
# Each product will be stored as a dictionary.
# For easy testing, we pre-populate it with two sample products:
products_list = [
    {
        "name": "Engineering Physics Book",
        "price": 250.0,
        "description": "First-year textbook, brand new condition.",
        "seller_name": "Aditya Kumar",
        "contact": "9876543210"
    },
    {
        "name": "White Lab Coat",
        "price": 150.0,
        "description": "Size L, white lab coat, washed and clean.",
        "seller_name": "Rohan Sharma",
        "contact": "9123456789"
    }
]


def add_product(name, price, description, seller_name, contact):
    """
    Adds a new product to the marketplace.
    
    Parameters:
    - name (str): The name of the product.
    - price (float): The price of the product.
    - description (str): Short description of the product.
    - seller_name (str): Name of the student selling the product.
    - contact (str): Phone number or contact info of the seller.
    
    Returns:
    - tuple: (bool, str) -> (True/False representing success, a message explaining the result)
    """
    
    # 1. Validation check: Ensure the fields are not empty
    if not name.strip() or not description.strip() or not contact.strip():
        return False, "Failed to add product! Name, description, and contact info cannot be empty."
        
    # 2. Validation check: Ensure price is positive
    if price <= 0:
        return False, "Failed to add product! Price must be greater than zero."
        
    # 3. Create the product dictionary
    new_product = {
        "name": name.strip(),
        "price": price,
        "description": description.strip(),
        "seller_name": seller_name.strip(),
        "contact": contact.strip()
    }
    
    # Add the product dictionary to our list of products
    products_list.append(new_product)
    
    return True, f"Product '{name}' added successfully!"

def get_all_products():
    """
    Returns the list of all products in the marketplace.
    
    Returns:
    - list: The list containing all product dictionaries.
    """
    return products_list

def search_products_by_name(query):
    """
    Searches products by their name.
    
    Parameters:
    - query (str): The search query entered by the user.
    
    Returns:
    - list: A list of products that match the search query.
    """
    # Clean the query (make it lowercase for case-insensitive matching)
    query = query.strip().lower()
    
    # Initialize an empty list to store matched products
    matched_products = []
    
    # Loop through all products
    for prod in products_list:
        # Check if the query is part of the product name
        if query in prod["name"].lower():
            matched_products.append(prod)
            
    return matched_products

