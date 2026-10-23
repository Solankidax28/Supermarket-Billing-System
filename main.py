"""
Supermarket Billing System
--------------------------
A beginner-friendly desktop application built with Python and Tkinter.

Python concepts demonstrated:
    * Lists        -> the product list and the shopping cart
    * Dictionaries -> every product, cart item and bill is a dictionary
    * File handling-> products.json (inventory) and the bills/ folder
    * Tkinter      -> window, frames, labels, entries, buttons, tables
    * Functions    -> each task has its own small function
    * Exceptions   -> try/except for file errors and invalid input
    * Loops/if     -> used in validation and billing calculations
"""

import json
import os
import subprocess
import sys
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

# ---------------------------------------------------------------------------
# Paths (all relative to the folder that contains main.py)
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PRODUCTS_FILE = os.path.join(BASE_DIR, "products.json")
BILLS_DIR = os.path.join(BASE_DIR, "bills")

DEFAULT_TAX_RATE = 5.0  # percent, used when the tax option is ticked
STORE_NAME = "JHOLA BAZAR"


# ===========================================================================
# PART 1: FILE HANDLING FUNCTIONS
# ===========================================================================
def load_products():
    """Read products.json and return a list of product dictionaries.

    If the file is missing or damaged, an empty list is returned so the
    program never crashes. Invalid entries inside the file are skipped.
    """
    products = []
    try:
        with open(PRODUCTS_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        return products          # first run: no file yet
    except (json.JSONDecodeError, OSError):
        return products          # damaged or unreadable file

    if not isinstance(data, list):
        return products

    for item in data:            # loop: keep only valid entries
        try:
            product = {
                "id": str(item["id"]).strip().upper(),
                "name": str(item["name"]).strip(),
                "price": float(item["price"]),
                "quantity": int(item["quantity"]),
            }
        except (KeyError, TypeError, ValueError):
            continue             # skip a bad entry
        if product["id"] and product["name"] and product["price"] >= 0 \
                and product["quantity"] >= 0:
            products.append(product)
    return products


def save_products(products):
    """Write the product list to products.json. Returns True if it worked."""
    try:
        with open(PRODUCTS_FILE, "w", encoding="utf-8") as file:
            json.dump(products, file, indent=4)
        return True
    except OSError:
        return False


def generate_bill_number():
    """Create a unique bill number such as BILL-20261023-153045.

    If a bill with the same number already exists, a counter is added.
    """
    base_number = "BILL-" + datetime.now().strftime("%Y%m%d-%H%M%S")
    bill_number = base_number
    counter = 1
    while os.path.exists(os.path.join(BILLS_DIR, bill_number + ".txt")):
        counter += 1
        bill_number = "{}-{}".format(base_number, counter)
    return bill_number


def save_bill_to_file(bill_number, bill_text):
    """Save the bill text in the bills/ folder. Returns the file path."""
    os.makedirs(BILLS_DIR, exist_ok=True)
    file_path = os.path.join(BILLS_DIR, bill_number + ".txt")
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(bill_text)
    return file_path


def print_bill_file(file_path):
    """Send a saved bill to the default printer (platform dependent).

    Windows : uses the 'print' action of the default text editor.
    macOS / Linux : uses the 'lp' command (needs a configured printer).
    """
    if sys.platform.startswith("win"):
        os.startfile(file_path, "print")  # only exists on Windows
    else:
        subprocess.run(["lp", file_path], check=True)


# ===========================================================================
# PART 2: PRODUCT FUNCTIONS
# ===========================================================================
def validate_product_input(product_id, name, price_text, quantity_text):
    """Check the 'Add Product' form.

    Returns (product_dictionary, None) when valid,
    or (None, error_message) when something is wrong.
    """
    product_id = product_id.strip().upper()
    name = name.strip()

    if not product_id:
        return None, "Product ID cannot be empty."
    if not name:
        return None, "Product name cannot be empty."

    try:
        price = float(price_text)
    except ValueError:
        return None, "Price must be a number (example: 45.50)."
    if price <= 0:
        return None, "Price must be greater than zero."

    try:
        quantity = int(quantity_text)
    except ValueError:
        return None, "Quantity must be a whole number (example: 20)."
    if quantity < 0:
        return None, "Quantity cannot be negative."

    product = {
        "id": product_id,
        "name": name,
        "price": round(price, 2),
        "quantity": quantity,
    }
    return product, None


def find_product_by_id(products, product_id):
    """Return the product dictionary with this ID, or None."""
    product_id = product_id.strip().upper()
    for product in products:
        if product["id"] == product_id:
            return product
    return None


def search_products(products, keyword):
    """Return a list of products whose ID or name contains the keyword."""
    keyword = keyword.strip().lower()
    matches = []
    for product in products:
        if keyword in product["id"].lower() or keyword in product["name"].lower():
            matches.append(product)
    return matches


def update_product(products, product_id, price_text, quantity_text):
    """Change the price and/or the stock of an existing product.

    Leave a field empty to keep its current value.
    Returns an error message, or None when the product was updated.
    """
    product = find_product_by_id(products, product_id)
    if product is None:
        return "Product ID not found."

    price_text = price_text.strip()
    quantity_text = quantity_text.strip()
    if not price_text and not quantity_text:
        return "Enter a new price, a new stock quantity, or both."

    new_price = None
    new_quantity = None

    if price_text:
        try:
            new_price = float(price_text)
        except ValueError:
            return "Price must be a number (example: 45.50)."
        if new_price <= 0:
            return "Price must be greater than zero."

    if quantity_text:
        try:
            new_quantity = int(quantity_text)
        except ValueError:
            return "Stock must be a whole number (example: 20)."
        if new_quantity < 0:
            return "Stock cannot be negative."

    # Apply changes only after everything is valid
    if new_price is not None:
        product["price"] = round(new_price, 2)
    if new_quantity is not None:
        product["quantity"] = new_quantity
    return None


def sync_cart_with_product(cart, product):
    """Keep the cart correct after a product's price or stock changed.

    Returns a warning message if an item had to be removed, else None.
    """
    for item in cart:
        if item["id"] == product["id"]:
            if item["quantity"] > product["quantity"]:
                cart.remove(item)
                return ("'{}' was removed from the cart because the new stock "
                        "is lower than the cart quantity.".format(product["name"]))
            item["price"] = product["price"]
            item["total"] = round(item["quantity"] * item["price"], 2)
            return None
    return None


# ===========================================================================
# PART 3: CART AND BILLING FUNCTIONS
# ===========================================================================
def quantity_in_cart(cart, product_id):
    """How many units of this product are already in the cart."""
    for item in cart:
        if item["id"] == product_id:
            return item["quantity"]
    return 0


def add_item_to_cart(cart, product, quantity):
    """Add a product to the cart list (or increase its quantity).

    Returns an error message, or None when the item was added.
    """
    if quantity <= 0:
        return "Quantity must be at least 1."

    already_in_cart = quantity_in_cart(cart, product["id"])
    if already_in_cart + quantity > product["quantity"]:
        available = product["quantity"] - already_in_cart
        return "Only {} unit(s) of '{}' can still be added.".format(
            max(available, 0), product["name"])

    for item in cart:
        if item["id"] == product["id"]:
            item["quantity"] += quantity
            item["total"] = round(item["quantity"] * item["price"], 2)
            return None

    cart.append({
        "id": product["id"],
        "name": product["name"],
        "price": product["price"],
        "quantity": quantity,
        "total": round(quantity * product["price"], 2),
    })
    return None


def calculate_totals(cart, apply_tax, tax_rate):
    """Return a dictionary with subtotal, tax and grand total."""
    subtotal = 0.0
    for item in cart:                       # loop through every cart item
        subtotal += item["total"]

    tax = 0.0
    if apply_tax:                           # conditional: tax is optional
        tax = subtotal * tax_rate / 100

    return {
        "subtotal": round(subtotal, 2),
        "tax_rate": tax_rate if apply_tax else 0.0,
        "tax": round(tax, 2),
        "grand_total": round(subtotal + tax, 2),
    }


def create_bill(cart, totals):
    """Build the bill dictionary from the cart and the totals."""
    return {
        "bill_number": generate_bill_number(),
        "date": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
        "items": [dict(item) for item in cart],   # copy of the cart list
        "subtotal": totals["subtotal"],
        "tax_rate": totals["tax_rate"],
        "tax": totals["tax"],
        "grand_total": totals["grand_total"],
    }


def format_bill(bill):
    """Turn the bill dictionary into readable text."""
    line = "=" * 52
    thin = "-" * 52
    lines = [
        line,
        STORE_NAME.center(52),
        line,
        "Bill No : " + bill["bill_number"],
        "Date    : " + bill["date"],
        thin,
        "{:<4}{:<20}{:>6}{:>8}{:>12}".format("No", "Item", "Qty", "Price", "Total"),
        thin,
    ]
    for number, item in enumerate(bill["items"], start=1):
        lines.append("{:<4}{:<20}{:>6}{:>8.2f}{:>12.2f}".format(
            number, item["name"][:19], item["quantity"],
            item["price"], item["total"]))
    lines.append(thin)
    lines.append("{:<40}{:>12.2f}".format("Subtotal", bill["subtotal"]))
    if bill["tax_rate"] > 0:
        lines.append("{:<40}{:>12.2f}".format(
            "Tax ({:g}%)".format(bill["tax_rate"]), bill["tax"]))
    lines.append("{:<40}{:>12.2f}".format("GRAND TOTAL", bill["grand_total"]))
    lines.append(line)
    lines.append("Thank you for shopping with us!".center(52))
    lines.append(line)
    return "\n".join(lines) + "\n"


def reduce_stock(products, cart):
    """Subtract the purchased quantities from the product list."""
    for item in cart:
        product = find_product_by_id(products, item["id"])
        if product is not None:
            product["quantity"] -= item["quantity"]


# ===========================================================================
# PART 4: THE GUI (TKINTER)
# ===========================================================================
class BillingApp:
    """The main window of the application."""

    def __init__(self, root):
        self.root = root
        self.root.title("Supermarket Billing System")
        self.root.geometry("1150x700")
        self.root.minsize(1000, 640)

        # Application data
        self.products = load_products()    # list of dictionaries
        self.cart = []                     # list of dictionaries
        self.current_bill = None           # dictionary of the last bill
        self.current_bill_text = ""
        self.saved_file_path = None

        # Tkinter variables linked to input widgets
        self.id_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.price_var = tk.StringVar()
        self.qty_var = tk.StringVar()
        self.search_var = tk.StringVar()
        self.cart_id_var = tk.StringVar()
        self.cart_qty_var = tk.StringVar(value="1")
        self.tax_var = tk.BooleanVar(value=False)
        self.tax_rate_var = tk.StringVar(value=str(DEFAULT_TAX_RATE))

        self.build_layout()
        self.refresh_product_table(self.products)
        self.refresh_cart_table()

        if not self.products:
            messagebox.showinfo(
                "No products",
                "No products were loaded from products.json.\n"
                "Use 'Add Product' to create your inventory.")

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------
    def build_layout(self):
        """Create all frames and widgets."""
        title = tk.Label(self.root, text=STORE_NAME, bg="#1f4e79", fg="white",
                         font=("Arial", 18, "bold"), pady=8)
        title.pack(fill="x")

        main_frame = tk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=8, pady=8)
        main_frame.columnconfigure(0, weight=3)
        main_frame.columnconfigure(1, weight=2)
        main_frame.rowconfigure(0, weight=1)

        left = tk.Frame(main_frame)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        right = tk.Frame(main_frame)
        right.grid(row=0, column=1, sticky="nsew")

        self.build_product_section(left)
        self.build_cart_section(right)
        self.build_bill_section(right)

    def build_product_section(self, parent):
        """Left side: product form, search and product table."""
        form = ttk.LabelFrame(parent, text="Product Management")
        form.pack(fill="x")

        labels = ["Product ID", "Name", "Price", "Quantity"]
        variables = [self.id_var, self.name_var, self.price_var, self.qty_var]
        for column, (text, variable) in enumerate(zip(labels, variables)):
            tk.Label(form, text=text).grid(row=0, column=column, padx=5, pady=(5, 0))
            tk.Entry(form, textvariable=variable, width=16).grid(
                row=1, column=column, padx=5, pady=5)

        tk.Button(form, text="Add Product", bg="#2e7d32", fg="white",
                  command=self.add_product).grid(row=1, column=4, padx=5)
        tk.Button(form, text="Clear Form",
                  command=self.clear_product_form).grid(row=1, column=5, padx=5)
        tk.Button(form, text="Update Product", bg="#ef6c00", fg="white",
                  command=self.update_product_action).grid(row=1, column=6, padx=5)
        tk.Label(form, fg="gray",
                 text="To update: click a product, change Price and/or Quantity "
                      "(the new stock), then click Update Product."
                 ).grid(row=2, column=0, columnspan=7, sticky="w", padx=5, pady=(0, 5))

        search_frame = ttk.LabelFrame(parent, text="Search Product (ID or Name)")
        search_frame.pack(fill="x", pady=6)
        tk.Entry(search_frame, textvariable=self.search_var, width=30).pack(
            side="left", padx=5, pady=5)
        tk.Button(search_frame, text="Search Product",
                  command=self.search_product).pack(side="left", padx=5)
        tk.Button(search_frame, text="Show All",
                  command=self.show_all_products).pack(side="left", padx=5)

        table_frame = ttk.LabelFrame(parent, text="Available Products")
        table_frame.pack(fill="both", expand=True)

        columns = ("id", "name", "price", "quantity")
        self.product_table = ttk.Treeview(table_frame, columns=columns,
                                          show="headings", height=14)
        headings = {"id": "ID", "name": "Name", "price": "Price",
                    "quantity": "Stock"}
        widths = {"id": 80, "name": 220, "price": 90, "quantity": 80}
        for column in columns:
            self.product_table.heading(column, text=headings[column])
            self.product_table.column(column, width=widths[column],
                                      anchor="w" if column == "name" else "center")
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical",
                                  command=self.product_table.yview)
        self.product_table.configure(yscrollcommand=scrollbar.set)
        self.product_table.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        # Clicking a row copies its ID into the cart form
        self.product_table.bind("<<TreeviewSelect>>", self.on_product_select)

    def build_cart_section(self, parent):
        """Right side (top): cart form, cart table, tax and bill buttons."""
        cart_frame = ttk.LabelFrame(parent, text="Shopping Cart")
        cart_frame.pack(fill="x")

        entry_row = tk.Frame(cart_frame)
        entry_row.pack(fill="x", pady=5)
        tk.Label(entry_row, text="Product ID").pack(side="left", padx=5)
        tk.Entry(entry_row, textvariable=self.cart_id_var, width=10).pack(side="left")
        tk.Label(entry_row, text="Qty").pack(side="left", padx=5)
        tk.Entry(entry_row, textvariable=self.cart_qty_var, width=6).pack(side="left")
        tk.Button(entry_row, text="Add to Cart", bg="#1565c0", fg="white",
                  command=self.add_to_cart).pack(side="left", padx=8)
        tk.Button(entry_row, text="Remove Selected",
                  command=self.remove_from_cart).pack(side="left")

        columns = ("name", "quantity", "price", "total")
        self.cart_table = ttk.Treeview(cart_frame, columns=columns,
                                       show="headings", height=6)
        headings = {"name": "Item", "quantity": "Qty", "price": "Price",
                    "total": "Total"}
        widths = {"name": 150, "quantity": 50, "price": 70, "total": 80}
        for column in columns:
            self.cart_table.heading(column, text=headings[column])
            self.cart_table.column(column, width=widths[column],
                                   anchor="w" if column == "name" else "center")
        self.cart_table.pack(fill="x", padx=5)

        self.total_label = tk.Label(cart_frame, text="Subtotal: 0.00",
                                    font=("Arial", 11, "bold"))
        self.total_label.pack(anchor="e", padx=8, pady=2)

        tax_row = tk.Frame(cart_frame)
        tax_row.pack(fill="x", pady=2)
        tk.Checkbutton(tax_row, text="Apply tax", variable=self.tax_var,
                       command=self.refresh_cart_table).pack(side="left", padx=5)
        tk.Label(tax_row, text="Tax %").pack(side="left")
        tax_entry = tk.Entry(tax_row, textvariable=self.tax_rate_var, width=6)
        tax_entry.pack(side="left", padx=3)
        tax_entry.bind("<KeyRelease>", lambda event: self.refresh_cart_table())

        button_row = tk.Frame(cart_frame)
        button_row.pack(fill="x", pady=6)
        tk.Button(button_row, text="Generate Bill", bg="#2e7d32", fg="white",
                  command=self.generate_bill).pack(side="left", padx=5)
        tk.Button(button_row, text="Save Bill",
                  command=self.save_bill).pack(side="left", padx=5)
        tk.Button(button_row, text="Print Bill",
                  command=self.print_bill).pack(side="left", padx=5)
        tk.Button(button_row, text="Clear", bg="#c62828", fg="white",
                  command=self.clear_all).pack(side="left", padx=5)

    def build_bill_section(self, parent):
        """Right side (bottom): the bill display area."""
        bill_frame = ttk.LabelFrame(parent, text="Bill")
        bill_frame.pack(fill="both", expand=True, pady=(6, 0))
        self.bill_text = tk.Text(bill_frame, width=54, height=14,
                                 font=("Courier New", 9), state="disabled")
        scrollbar = ttk.Scrollbar(bill_frame, orient="vertical",
                                  command=self.bill_text.yview)
        self.bill_text.configure(yscrollcommand=scrollbar.set)
        self.bill_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    # ------------------------------------------------------------------
    # Helper methods
    # ------------------------------------------------------------------
    def refresh_product_table(self, product_list):
        """Show the given list of products in the product table."""
        for row in self.product_table.get_children():
            self.product_table.delete(row)
        for product in product_list:
            self.product_table.insert("", "end", values=(
                product["id"], product["name"],
                "{:.2f}".format(product["price"]), product["quantity"]))

    def get_tax_rate(self):
        """Read the tax percentage. Returns None if it is invalid."""
        try:
            rate = float(self.tax_rate_var.get())
        except ValueError:
            return None
        if rate < 0 or rate > 100:
            return None
        return rate

    def refresh_cart_table(self):
        """Redraw the cart table and update the total label."""
        for row in self.cart_table.get_children():
            self.cart_table.delete(row)
        for item in self.cart:
            self.cart_table.insert("", "end", iid=item["id"], values=(
                item["name"], item["quantity"],
                "{:.2f}".format(item["price"]), "{:.2f}".format(item["total"])))

        rate = self.get_tax_rate()
        apply_tax = self.tax_var.get() and rate is not None
        totals = calculate_totals(self.cart, apply_tax, rate if rate else 0.0)
        if apply_tax:
            self.total_label.config(text="Subtotal: {:.2f}   Tax: {:.2f}   "
                                    "Total: {:.2f}".format(
                                        totals["subtotal"], totals["tax"],
                                        totals["grand_total"]))
        else:
            self.total_label.config(
                text="Subtotal: {:.2f}".format(totals["subtotal"]))

    def show_bill_text(self, text):
        """Display text in the (read-only) bill area."""
        self.bill_text.config(state="normal")
        self.bill_text.delete("1.0", "end")
        self.bill_text.insert("end", text)
        self.bill_text.config(state="disabled")

    def on_product_select(self, event):
        """Copy the ID of the clicked product row into the cart form."""
        selected = self.product_table.selection()
        if selected:
            values = self.product_table.item(selected[0], "values")
            self.cart_id_var.set(values[0])
            # Also fill the product form so it can be edited and updated
            self.id_var.set(values[0])
            self.name_var.set(values[1])
            self.price_var.set(values[2])
            self.qty_var.set(values[3])

    # ------------------------------------------------------------------
    # Product button actions
    # ------------------------------------------------------------------
    def add_product(self):
        """Validate the form and add a new product to the inventory."""
        product, error = validate_product_input(
            self.id_var.get(), self.name_var.get(),
            self.price_var.get(), self.qty_var.get())
        if error:
            messagebox.showerror("Invalid input", error)
            return

        if find_product_by_id(self.products, product["id"]) is not None:
            messagebox.showerror("Duplicate ID",
                                 "A product with ID '{}' already exists."
                                 .format(product["id"]))
            return

        self.products.append(product)
        if save_products(self.products):
            messagebox.showinfo("Success", "Product '{}' added."
                                .format(product["name"]))
        else:
            messagebox.showwarning("Not saved",
                                   "Product added, but products.json could "
                                   "not be saved.")
        self.clear_product_form()
        self.refresh_product_table(self.products)

    def clear_product_form(self):
        """Empty the product input fields."""
        for variable in (self.id_var, self.name_var, self.price_var, self.qty_var):
            variable.set("")

    def update_product_action(self):
        """Update the price and/or stock of the product in the form."""
        product_id = self.id_var.get()
        error = update_product(self.products, product_id,
                               self.price_var.get(), self.qty_var.get())
        if error:
            messagebox.showerror("Update failed", error)
            return

        product = find_product_by_id(self.products, product_id)
        warning = sync_cart_with_product(self.cart, product)

        if save_products(self.products):
            messagebox.showinfo("Success", "Product '{}' updated."
                                .format(product["name"]))
        else:
            messagebox.showwarning("Not saved",
                                   "Product updated, but products.json could "
                                   "not be saved.")
        if warning:
            messagebox.showwarning("Cart updated", warning)

        self.clear_product_form()
        self.refresh_cart_table()
        self.refresh_product_table(self.products)

    def search_product(self):
        """Filter the product table by ID or name."""
        keyword = self.search_var.get().strip()
        if not keyword:
            messagebox.showwarning("Search", "Please type an ID or a name.")
            return
        matches = search_products(self.products, keyword)
        self.refresh_product_table(matches)
        if not matches:
            messagebox.showinfo("Search", "No product found for '{}'."
                                .format(keyword))

    def show_all_products(self):
        """Reset the search and show every product."""
        self.search_var.set("")
        self.refresh_product_table(self.products)

    # ------------------------------------------------------------------
    # Cart and bill button actions
    # ------------------------------------------------------------------
    def add_to_cart(self):
        """Add the chosen product and quantity to the cart."""
        product = find_product_by_id(self.products, self.cart_id_var.get())
        if product is None:
            messagebox.showerror("Not found",
                                 "Enter or select a valid product ID.")
            return

        try:
            quantity = int(self.cart_qty_var.get())
        except ValueError:
            messagebox.showerror("Invalid quantity",
                                 "Quantity must be a whole number.")
            return
        if quantity <= 0:
            messagebox.showerror("Invalid quantity",
                                 "Quantity must be at least 1.")
            return

        error = add_item_to_cart(self.cart, product, quantity)
        if error:
            messagebox.showerror("Stock problem", error)
            return
        self.refresh_cart_table()
        self.cart_qty_var.set("1")

    def remove_from_cart(self):
        """Remove the selected row from the cart."""
        selected = self.cart_table.selection()
        if not selected:
            messagebox.showwarning("Remove", "Select an item in the cart first.")
            return
        product_id = selected[0]
        self.cart = [item for item in self.cart if item["id"] != product_id]
        self.refresh_cart_table()

    def generate_bill(self):
        """Finish the sale: build the bill, reduce stock and save inventory."""
        if not self.cart:
            messagebox.showwarning("Empty cart", "Add items to the cart first.")
            return

        rate = self.get_tax_rate()
        if self.tax_var.get() and rate is None:
            messagebox.showerror("Invalid tax",
                                 "Tax must be a number between 0 and 100.")
            return

        # Double-check stock (protects against changes after adding to cart)
        for item in self.cart:
            product = find_product_by_id(self.products, item["id"])
            if product is None or item["quantity"] > product["quantity"]:
                messagebox.showerror("Stock problem",
                                     "Not enough stock for '{}'."
                                     .format(item["name"]))
                return

        totals = calculate_totals(self.cart, self.tax_var.get(), rate or 0.0)
        self.current_bill = create_bill(self.cart, totals)
        self.current_bill_text = format_bill(self.current_bill)
        self.saved_file_path = None

        reduce_stock(self.products, self.cart)
        if not save_products(self.products):
            messagebox.showwarning("Inventory not saved",
                                   "The bill was created but products.json "
                                   "could not be updated.")

        self.show_bill_text(self.current_bill_text)
        self.cart = []
        self.refresh_cart_table()
        self.refresh_product_table(self.products)
        messagebox.showinfo("Bill generated",
                            "Bill {} created.\nStock has been updated."
                            .format(self.current_bill["bill_number"]))

    def save_bill(self):
        """Save the current bill as a text file in the bills/ folder."""
        if self.current_bill is None:
            messagebox.showwarning("No bill", "Generate a bill first.")
            return
        try:
            self.saved_file_path = save_bill_to_file(
                self.current_bill["bill_number"], self.current_bill_text)
        except OSError as error:
            messagebox.showerror("Save failed",
                                 "Could not save the bill:\n{}".format(error))
            return
        messagebox.showinfo("Bill saved",
                            "Saved to:\n{}".format(self.saved_file_path))

    def print_bill(self):
        """Save the bill if needed, then send it to the printer."""
        if self.current_bill is None:
            messagebox.showwarning("No bill", "Generate a bill first.")
            return
        try:
            if self.saved_file_path is None:
                self.saved_file_path = save_bill_to_file(
                    self.current_bill["bill_number"], self.current_bill_text)
            print_bill_file(self.saved_file_path)
        except (OSError, subprocess.SubprocessError) as error:
            messagebox.showerror(
                "Print failed",
                "Could not print. The bill is saved in the bills folder, "
                "so you can print it manually.\n\nDetails: {}".format(error))
            return
        messagebox.showinfo("Print", "The bill was sent to the printer.")

    def clear_all(self):
        """Clear the cart, bill display and input fields."""
        self.cart = []
        self.current_bill = None
        self.current_bill_text = ""
        self.saved_file_path = None
        self.cart_id_var.set("")
        self.cart_qty_var.set("1")
        self.refresh_cart_table()
        self.show_bill_text("")
        self.clear_product_form()
        self.show_all_products()


# ===========================================================================
# PART 5: PROGRAM START
# ===========================================================================
def main():
    """Create the window and start the application."""
    root = tk.Tk()
    BillingApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()