# Supermarket Billing System

A simple desktop application built with **Python and Tkinter** for managing supermarket products and generating customer bills. Product data is stored in a JSON file, and every bill can be saved as a text file.

## Project Objectives

- Build a complete desktop application using core Python concepts.
- Practise lists, dictionaries, file handling, functions and exception handling.
- Create a clean, beginner-friendly graphical interface with Tkinter.
- Keep inventory accurate by updating stock after every sale.

## Features

- **Product management:** add products (ID, name, price, quantity), view all products, search by ID or name.
- **Shopping cart:** pick a product, enter a quantity, add or remove cart items.
- **Billing:** item-wise totals, subtotal, optional tax (default 5%, editable) and grand total.
- **Unique bill numbers** such as `BILL-20261023-153045`.
- **Save and print bills:** bills are saved in the `bills/` folder; printing is supported where the system allows it.
- **Inventory control:** stock is reduced after billing, purchases above available stock are blocked, and changes are saved to `products.json`.
- **Input validation and error messages** for negative quantities, invalid prices, duplicate IDs and more.
- **Safe file handling:** a missing or damaged `products.json` does not crash the program.

## Technologies Used

- Python 3.8 or newer
- Tkinter (GUI)
- JSON (data storage)

## Python Concepts Used and Where They Appear

| Concept | Where it appears in `main.py` |
|---|---|
| Lists | `self.products` (all products), `self.cart` (cart items), search results |
| Dictionaries | every product, cart item and bill (`id`, `name`, `price`, `quantity`, `total`) |
| File handling | `load_products()`, `save_products()`, `save_bill_to_file()` |
| Functions | one small function per task, grouped in numbered parts of the file |
| Exception handling | `load_products()`, `validate_product_input()`, `add_to_cart()`, `save_bill()`, `print_bill()` |
| Loops and conditions | `calculate_totals()`, `add_item_to_cart()`, `reduce_stock()`, `search_products()` |
| Tkinter widgets | `BillingApp` class: Frame, Label, Entry, Button, Treeview, Text, Checkbutton |

## Folder Structure

```
Supermarket-Billing-System/
├── main.py            # complete application
├── products.json      # product / inventory data
├── README.md
├── requirements.txt
├── .gitignore
├── bills/             # generated bills are saved here
│   └── .gitkeep
└── screenshots/       # add your screenshots here
    └── .gitkeep
```

## Installation Requirements

- Python 3.8 or newer ([python.org](https://www.python.org/downloads/))
- Tkinter (included with Python on Windows and macOS)
- On Ubuntu/Debian, if Tkinter is missing: `sudo apt install python3-tk`

No packages need to be installed with pip.

## How to Run

1. Download or clone the project and open a terminal in the project folder.
2. Check Python: `python --version` (or `python3 --version`).
3. Start the application:
   ```
   python main.py
   ```
   (use `python3 main.py` on macOS/Linux).

## How to Use the Billing System

1. **Add a product:** fill in ID, Name, Price and Quantity, then click **Add Product**.
2. **Search:** type an ID or name and click **Search Product**; click **Show All** to reset.
3. **Add to cart:** click a product row (its ID is filled in automatically), enter a quantity, click **Add to Cart**.
4. **Remove an item:** select it in the cart and click **Remove Selected**.
5. **Tax:** tick **Apply tax** and edit the percentage if needed.
6. **Generate Bill:** creates the bill, shows it on screen, reduces stock and saves `products.json`.
7. **Save Bill:** writes the bill to the `bills/` folder.
8. **Print Bill:** sends the saved bill to the printer (see below).
9. **Clear:** resets the cart, bill display and input fields.

### Printing limitations

- **Windows:** uses the default text editor's print action.
- **macOS / Linux:** uses the `lp` command and needs a configured printer.
- If printing fails, the bill is still saved in `bills/`, so you can open and print it manually.

## Example Bill Output

```
====================================================
             SUPERMARKET BILLING SYSTEM             
====================================================
Bill No : BILL-20261023-153045
Date    : 23-10-2026 15:30:45
----------------------------------------------------
No  Item                   Qty   Price       Total
----------------------------------------------------
1   Basmati Rice 1kg         2   85.00      170.00
2   Milk 1L                  3   56.00      168.00
3   Biscuits Pack            5   10.00       50.00
----------------------------------------------------
Subtotal                                      388.00
Tax (5%)                                       19.40
GRAND TOTAL                                   407.40
====================================================
          Thank you for shopping with us!           
====================================================
```

## Sample Screenshots

Screenshots are not included. To add your own:

1. Run the application and perform a sale.
2. Take screenshots (Windows: `Win + Shift + S`; macOS: `Cmd + Shift + 4`).
3. Save them in the `screenshots/` folder, for example `main-window.png` and `generated-bill.png`.
4. Add them here:
   ```
   ![Main window](screenshots/main-window.png)
   ![Generated bill](screenshots/generated-bill.png)
   ```

## Future Enhancements

- Edit and delete products.
- Customer name and phone number on bills.
- Low-stock warnings.
- Sales reports and daily totals.
- Database storage (SQLite) instead of JSON.
- PDF bills and barcode scanning.
- User login for cashier and admin roles.

## Learning Outcomes

- Using lists and dictionaries to model real-world data.
- Reading and writing JSON files safely.
- Building a GUI with Tkinter and handling user events.
- Validating input and handling exceptions.
- Structuring a program into small, reusable functions.
- Preparing a project for GitHub.

## Author

- **Name:** YOUR NAME
- **College:** YOUR COLLEGE NAME
- **Course:** YOUR COURSE / BRANCH
