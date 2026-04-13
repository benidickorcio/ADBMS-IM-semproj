import customtkinter as ctk
from tkinter import ttk, messagebox
from models.customer import *
from utils.receipt import get_payment_receipt_data, generate_receipt, save_payment_receipt


class CustomersScreen:
    def __init__(self, parent):
        self.parent = parent
        self.frame = ctk.CTkFrame(parent, corner_radius=12)
        self.frame.pack(expand=True, fill="both", padx=10, pady=10)

        self.build_ui()
        self.load_customers()

    def build_ui(self):
        header = ctk.CTkLabel(self.frame, text="Customers", font=ctk.CTkFont(size=20, weight="bold"))
        header.pack(pady=12)

        search_frame = ctk.CTkFrame(self.frame)
        search_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Search by name, contact, address...", width=320)
        self.search_entry.pack(side="left", padx=8)
        self.search_entry.bind("<KeyRelease>", lambda e: self.on_search())

        self.refresh_btn = ctk.CTkButton(search_frame, text="Refresh", width=100, command=self.load_customers)
        self.refresh_btn.pack(side="left", pady=8)

        columns = ("customer_id", "name", "contact_number", "address", "current_balance")
        self.tree_frame = ctk.CTkFrame(self.frame)
        self.tree_frame.pack(fill="both", expand=True, padx=10, pady=8)

        self.customers_tv = ttk.Treeview(self.tree_frame, columns=columns, show="headings", height=12)
        headings = {
            "customer_id": "ID",
            "name": "Name",
            "contact_number": "Contact",
            "address": "Address",
            "current_balance": "Balance"
        }
        for col in columns:
            self.customers_tv.heading(col, text=headings[col])
            self.customers_tv.column(col, width=120 if col != "address" else 180)

        self.customers_tv.pack(side="left", fill="both", expand=True)
        self.customers_tv.bind("<<TreeviewSelect>>", self.on_customer_select)

        self.vsb = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.customers_tv.yview)
        self.customers_tv.configure(yscrollcommand=self.vsb.set)
        self.vsb.pack(side="right", fill="y")

        actions = ctk.CTkFrame(self.frame)
        actions.pack(fill="x", padx=10, pady=(0, 10))

        self.add_btn = ctk.CTkButton(actions, text="Add Customer", width=120, command=self.open_add_customer)
        self.add_btn.pack(side="left", padx=8)

        self.edit_btn = ctk.CTkButton(actions, text="Edit Selected", width=120, command=self.open_edit_customer, state="disabled")
        self.edit_btn.pack(side="left", padx=8)

        self.delete_btn = ctk.CTkButton(actions, text="Delete Selected", width=120, command=self.delete_selected_customer, state="disabled")
        self.delete_btn.pack(side="left", padx=8)

        self.mark_paid_btn = ctk.CTkButton(
            actions,
            text="Mark as Paid",
            width=140,
            command=self.mark_selected_paid,
            state="disabled",
            fg_color="#16a34a",
            hover_color="#15803d"
        )
        self.mark_paid_btn.pack(side="left", padx=8)

    def load_customers(self):
        self.customers_tv.delete(*self.customers_tv.get_children())
        rows = get_all_customers() or []
        for c in rows:
            balance = f"₱{float(c.get('current_balance', 0.0)):.2f}"
            self.customers_tv.insert("", "end", values=(c.get("customer_id"), c.get("name"), c.get("contact_number"), c.get("address"), balance))
        self.edit_btn.configure(state="disabled")
        self.delete_btn.configure(state="disabled")
        self.mark_paid_btn.configure(state="disabled")

    def on_search(self):
        keyword = self.search_entry.get().strip()
        if not keyword:
            self.load_customers()
            return

        self.customers_tv.delete(*self.customers_tv.get_children())
        rows = search_customer(keyword) or []
        for c in rows:
            balance = f"₱{float(c.get('current_balance', 0.0)):.2f}"
            self.customers_tv.insert("", "end", values=(c.get("customer_id"), c.get("name"), c.get("contact_number"), c.get("address"), balance))

    def on_customer_select(self, event=None):
        selected = self.customers_tv.selection()
        if selected:
            self.edit_btn.configure(state="normal")
            self.delete_btn.configure(state="normal")
            item = self.customers_tv.item(selected[0])
            customer_id = item["values"][0]
            customer = get_customer_by_id(customer_id)
            if customer and float(customer.get("current_balance", 0) or 0) > 0:
                self.mark_paid_btn.configure(state="normal")
            else:
                self.mark_paid_btn.configure(state="disabled")
        else:
            self.edit_btn.configure(state="disabled")
            self.delete_btn.configure(state="disabled")
            self.mark_paid_btn.configure(state="disabled")

    def open_add_customer(self):
        self.open_customer_form("Add Customer")

    def open_edit_customer(self):
        selected = self.customers_tv.selection()
        if not selected:
            return

        item = self.customers_tv.item(selected[0])
        customer_id = item["values"][0]
        customer = get_customer_by_id(customer_id)
        if not customer:
            messagebox.showwarning("Not found", "Selected customer could not be loaded.")
            return

        self.open_customer_form("Edit Customer", customer)

    def open_customer_form(self, title, customer=None):
        self.form_window = ctk.CTkToplevel(self.frame)
        self.form_window.title(title)
        self.form_window.geometry("420x380")
        self.form_window.resizable(False, False)
        self.form_window.grab_set()

        ctk.CTkLabel(self.form_window, text="Customer Name", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=20, pady=(20, 4))
        name_entry = ctk.CTkEntry(self.form_window, placeholder_text="Customer Name")
        name_entry.pack(fill="x", padx=20, pady=(0, 12))

        ctk.CTkLabel(self.form_window, text="Address", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=20, pady=(0, 4))
        address_entry = ctk.CTkEntry(self.form_window, placeholder_text="Address")
        address_entry.pack(fill="x", padx=20, pady=(0, 12))

        ctk.CTkLabel(self.form_window, text="Contact Number", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=20, pady=(0, 4))
        contact_entry = ctk.CTkEntry(self.form_window, placeholder_text="Enter 11-digit contact number")
        contact_entry.pack(fill="x", padx=20, pady=(0, 16))

        # Real-time validation to prevent non-digit characters from being entered
        def on_key_press(event):
            # Allow control keys: backspace, delete, arrow keys, home, end, tab, etc.
            if event.keysym in ('BackSpace', 'Delete', 'Left', 'Right', 'Home', 'End', 'Tab'):
                return
            # Reject non-digit characters immediately
            if not event.char.isdigit():
                return 'break'
            # Reject if already at 11 digits
            if len(contact_entry.get()) >= 11:
                return 'break'

        # Validation function to clean any pasted non-digit content and enforce 11-digit limit
        def validate_contact(*args):
            current_value = contact_entry.get()
            filtered_value = ''.join(c for c in current_value if c.isdigit())[:11]
            if current_value != filtered_value:
                contact_entry.delete(0, ctk.END)
                contact_entry.insert(0, filtered_value)

        contact_entry.bind("<KeyPress>", on_key_press)
        contact_entry.bind("<KeyRelease>", validate_contact)

        if customer is not None:
            name_entry.insert(0, customer.get("name", ""))
            contact_entry.insert(0, customer.get("contact_number", ""))
            address_entry.insert(0, customer.get("address", ""))

        def submit_customer():
            name = name_entry.get().strip()
            address = address_entry.get().strip()
            contact = contact_entry.get().strip()

            if not name:
                messagebox.showerror("Missing Information", "Please fill in customer name.")
                return

            # Contact number must be exactly 11 digits if provided
            if contact and len(contact) != 11:
                messagebox.showerror("Invalid Contact Number", "Contact number must be exactly 11 digits.")
                return

            if customer is None:
                add_customer(name, address, contact)
                messagebox.showinfo("Customer Added", f"Customer '{name}' has been added.")
            else:
                update_customer(
                    customer["customer_id"],
                    name=name,
                    address=address,
                    contact_number=contact
                )
                messagebox.showinfo("Customer Updated", f"Customer '{name}' has been updated.")
            
            self.form_window.destroy()
            self.load_customers()

        save_text = "Add" if customer is None else "Update"
        submit_btn = ctk.CTkButton(self.form_window, text=save_text, fg_color="#16a34a", hover_color="#15803d", command=submit_customer)
        submit_btn.pack(padx=20, pady=(0, 20))


    def delete_selected_customer(self):
        selected = self.customers_tv.selection()
        if not selected:
            return

        item = self.customers_tv.item(selected[0])
        customer_id = item["values"][0]

        if messagebox.askyesno(
            "Confirm Delete",
            "This will delete the customer and all their linked sales history.\n\nDo you want to continue?"
        ):
            from models.customer import delete_customer
            deleted = delete_customer(customer_id)
            if deleted:
                messagebox.showinfo("Removed", "Customer and related sales history deleted successfully.")
            else:
                messagebox.showwarning(
                    "Unable to Delete",
                    "The customer could not be deleted. Please try again or check the database constraints."
                )
            self.load_customers()

    def mark_selected_paid(self):
        selected = self.customers_tv.selection()
        if not selected:
            return

        item = self.customers_tv.item(selected[0])
        customer_id = item["values"][0]
        customer = get_customer_by_id(customer_id)
        if not customer:
            messagebox.showwarning("Not Found", "Selected customer could not be loaded.")
            return

        balance = float(customer.get("current_balance", 0.0) or 0.0)
        if balance <= 0:
            messagebox.showinfo("No Balance", "This customer has no outstanding balance.")
            return

        if not messagebox.askyesno(
            "Confirm Payment",
            f"Mark {customer['name']} as paid?\n\nThis will clear the outstanding balance of ₱{balance:.2f}"
            " and update all unpaid sales to PAID."
        ):
            return

        from models.customer import mark_customer_paid_balance
        payment_sale_id = mark_customer_paid_balance(customer_id)
        if payment_sale_id:
            messagebox.showinfo("Marked Paid", f"{customer['name']}'s balance has been cleared.")
            self.show_payment_receipt(customer, balance, payment_sale_id)
        else:
            messagebox.showerror("Error", "Failed to mark customer as paid.")

        self.load_customers()

    def show_payment_receipt(self, customer, amount_paid, payment_sale_id=None):
        receipt_window = ctk.CTkToplevel(self.frame)
        receipt_window.title("Payment Receipt")
        receipt_window.geometry("500x700")
        receipt_window.grab_set()

        try:
            payment_data = get_payment_receipt_data(customer, amount_paid, sale_id=payment_sale_id)
            receipt_img = generate_receipt(payment_data)
            ctk_image = ctk.CTkImage(light_image=receipt_img, dark_image=receipt_img, size=(receipt_img.width, receipt_img.height))

            img_label = ctk.CTkLabel(receipt_window, image=ctk_image, text="")
            img_label.image = ctk_image
            img_label.pack(padx=10, pady=10, fill="both", expand=True)

            btn_frame = ctk.CTkFrame(receipt_window)
            btn_frame.pack(fill="x", padx=10, pady=10)

            def save_receipt_file():
                filename = save_payment_receipt(payment_data)
                if filename:
                    messagebox.showinfo("Success", f"Receipt saved as:\n{filename}")
                else:
                    messagebox.showerror("Error", "Failed to save receipt")

            save_btn = ctk.CTkButton(
                btn_frame,
                text="Save Receipt",
                fg_color="#27c260",
                hover_color="#1a6937",
                command=save_receipt_file
            )
            save_btn.pack(side="left", padx=5)

            close_btn = ctk.CTkButton(
                btn_frame,
                text="Close",
                fg_color="#6b7280",
                hover_color="#4b5563",
                command=receipt_window.destroy
            )
            close_btn.pack(side="left", padx=5)

        except Exception as e:
            messagebox.showerror("Error", f"Error generating receipt: {str(e)}")
            receipt_window.destroy()
