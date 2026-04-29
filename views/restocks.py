# add stock screen
import customtkinter as ctk
from models.restock import restock_product, get_all_restock
from models.product import view_products
from tkinter import messagebox, ttk

class RestockScreen():
    def __init__(self, parent):
        self.parent = parent
        self.build_ui()
        self.load_restock_history()

    def build_ui(self):
        # Title
        self.title_label = ctk.CTkLabel(self.parent, text="Restock Management", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.pack(pady=10)

        # Buttons
        self.btn_frame = ctk.CTkFrame(self.parent)
        self.btn_frame.pack(fill="x", padx=20, pady=5)

        self.add_btn = ctk.CTkButton(self.btn_frame, text="Restock product", command=self.add_restock)
        self.add_btn.pack(side="left", padx=10,pady=10)

        self.refresh_btn = ctk.CTkButton(self.btn_frame, text="Refresh", command=self.load_restock_history)
        self.refresh_btn.pack(side="left")

        # Treeview
        self.tree_frame = ctk.CTkFrame(self.parent)
        self.tree_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.tree = ttk.Treeview(self.tree_frame, columns=("ID", "Product", "Quantity", "Unit Cost", "Total Cost", "Date"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Product", text="Product")
        self.tree.heading("Quantity", text="Quantity")
        self.tree.heading("Unit Cost", text="Unit Cost")
        self.tree.heading("Total Cost", text="Total Cost")
        self.tree.heading("Date", text="Date")

        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Product", width=150, anchor="center")
        self.tree.column("Quantity", width=100, anchor="center")
        self.tree.column("Unit Cost", width=100, anchor="center")
        self.tree.column("Total Cost", width=100, anchor="center")
        self.tree.column("Date", width=150, anchor="center")

        self.tree.pack(side="left", fill="both", expand=True)

        self.vsb = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.vsb.set)
        self.vsb.pack(side="right", fill="y")

    def load_restock_history(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        restocks = get_all_restock()
        for r in restocks:
            total = float(r['quantity']) * float(r['unit_cost'])
            self.tree.insert("", "end", values=(r['restock_id'], r['product_name'], r['quantity'], f"₱{r['unit_cost']:.2f}", f"₱{total:.2f}", r['restock_date']))

    def add_restock(self):
        self.form_window = ctk.CTkToplevel(self.parent)
        self.form_window.title("Add Restock")
        self.form_window.geometry("400x450")
        self.form_window.resizable(False, False)
        self.form_window.grab_set()

        # Product option menu
        ctk.CTkLabel(self.form_window, text="Product:").pack(pady=5)
        products = view_products()
        self.product_options = {p['name']: p['product_id'] for p in products}
        self.product_var = ctk.StringVar()
        if products:
            self.product_var.set(products[0]['name'])
        self.product_menu = ctk.CTkOptionMenu(self.form_window, variable=self.product_var, values=list(self.product_options.keys()))
        self.product_menu.pack(pady=5)

        # Quantity
        ctk.CTkLabel(self.form_window, text="Quantity:").pack(pady=5)
        self.qty_entry = ctk.CTkEntry(self.form_window)
        self.qty_entry.pack(pady=5)

        # Unit Cost
        ctk.CTkLabel(self.form_window, text="Unit Cost:").pack(pady=5)
        self.cost_entry = ctk.CTkEntry(self.form_window)
        self.cost_entry.pack(pady=5)

        # Buttons
        btn_frame = ctk.CTkFrame(self.form_window)
        btn_frame.pack(pady=20)
        save_btn = ctk.CTkButton(btn_frame, text="Save", command=self.save_restock)
        save_btn.pack(side="left", padx=10)
        cancel_btn = ctk.CTkButton(btn_frame, text="Cancel", command=self.form_window.destroy)
        cancel_btn.pack(side="right", padx=10)

    def save_restock(self):
        product_name = self.product_var.get()
        if not product_name:
            messagebox.showerror("Error", "Select a product")
            return
        product_id = self.product_options[product_name]
        qty_str = self.qty_entry.get().strip()
        cost_str = self.cost_entry.get().strip()
        try:
            qty = int(qty_str)
            cost = float(cost_str)
        except ValueError:
            messagebox.showerror("Error", "Invalid quantity or cost")
            return
        if qty <= 0 or cost < 0:
            messagebox.showerror("Error", "Quantity must be positive, cost non-negative")
            return
        restock_product(product_id, qty, cost)
        self.form_window.destroy()
        self.load_restock_history()