# ==========================================
# FILE: main.py
# PURPOSE: The entry point and console menu for CAMPUS-TRADE
# ==========================================

# Import our custom functions and variables from users.py
from users import register_user, login_user, users_list
# Import our custom functions from products.py
from products import add_product, get_all_products, search_products_by_name

def display_products(products):
    """
    Helper function to display a list of products in a clean, readable format.
    
    Parameters:
    - products (list): A list of product dictionaries to display.
    """
    if len(products) == 0:
        print("\nNo products found matching your search.")
        return
        
    print(f"\n--- PRODUCTS LISTING ({len(products)} found) ---")
    for index, prod in enumerate(products, start=1):
        print(f"\nProduct #{index}")
        print(f"Name:        {prod['name']}")
        print(f"Price:       Rs. {prod['price']}")
        print(f"Description: {prod['description']}")
        print(f"Seller:      {prod['seller_name']}")
        print(f"Contact:     {prod['contact']}")
        print("-" * 30)

def main():
    """
    Main function that runs the CAMPUS-TRADE interactive menu.
    Tracks the logged-in student in a variable called 'current_user'.
    """
    current_user = None
    
    print("=========================================")
    print("     WELCOME TO CAMPUS-TRADE (MIET)      ")
    print("=========================================")
    
    while True:
        if current_user is None:
            # --- LOGGED OUT MENU ---
            print("\n--- MENU (Logged Out) ---")
            print("1. Register")
            print("2. Login")
            print("3. View All Products")
            print("4. Search Products")
            print("5. Exit")
            
            choice = input("Enter your choice (1-5): ").strip()
            
            if choice == "1":
                print("\n--- USER REGISTRATION ---")
                name = input("Enter your full name: ")
                email = input("Enter your college email (must end with @miet.ac.in): ")
                password = input("Enter your password: ")
                
                success, message = register_user(name, email, password)
                
                print("\n-----------------------------------------")
                print(message)
                print("-----------------------------------------")
                
            elif choice == "2":
                print("\n--- USER LOGIN ---")
                email = input("Enter your college email: ")
                password = input("Enter your password: ")
                
                user = login_user(email, password)
                
                if user is not None:
                    current_user = user
                    print("\n-----------------------------------------")
                    print(f"Login successful! Welcome back, {current_user['name']}.")
                    print("-----------------------------------------")
                else:
                    print("\n-----------------------------------------")
                    print("Login failed! Invalid email or password.")
                    print("-----------------------------------------")
                    
            elif choice == "3":
                all_prods = get_all_products()
                display_products(all_prods)
                
            elif choice == "4":
                print("\n--- SEARCH PRODUCTS ---")
                query = input("Enter product name to search: ")
                matched_prods = search_products_by_name(query)
                display_products(matched_prods)
                
            elif choice == "5":
                print("\nThank you for using Campus-Trade. Goodbye!")
                break
                
            else:
                print("\nInvalid choice! Please enter a number between 1 and 5.")
                
        else:
            # --- LOGGED IN MENU ---
            print(f"\nLogged in as: {current_user['name']} ({current_user['email']})")
            print("--- MENU (Logged In) ---")
            print("1. Add Product for Sale")
            print("2. View All Products")
            print("3. Search Products")
            print("4. Logout")
            print("5. Exit")
            
            choice = input("Enter your choice (1-5): ").strip()
            
            if choice == "1":
                print("\n--- ADD NEW PRODUCT ---")
                prod_name = input("Enter product name (e.g. Lab Coat, Book): ")
                
                try:
                    price_input = input("Enter price in Rs.: ")
                    price = float(price_input)
                except ValueError:
                    print("\nError: Price must be a valid number!")
                    continue
                    
                description = input("Enter product description: ")
                contact = input("Enter your contact number: ")
                
                success, message = add_product(prod_name, price, description, current_user['name'], contact)
                
                print("\n-----------------------------------------")
                print(message)
                print("-----------------------------------------")
                
            elif choice == "2":
                all_prods = get_all_products()
                display_products(all_prods)
                
            elif choice == "3":
                print("\n--- SEARCH PRODUCTS ---")
                query = input("Enter product name to search: ")
                matched_prods = search_products_by_name(query)
                display_products(matched_prods)
                
            elif choice == "4":
                print("\n-----------------------------------------")
                print(f"Logged out successfully. Goodbye, {current_user['name']}!")
                print("-----------------------------------------")
                current_user = None
                
            elif choice == "5":
                print("\nThank you for using Campus-Trade. Goodbye!")
                break
                
            else:
                print("\nInvalid choice! Please enter a number between 1 and 5.")

# This line ensures the main() function runs when we execute this file
if __name__ == "__main__":
    main()
