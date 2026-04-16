import customtkinter as ctk
from tkinter import ttk
from models.sales import get_sales_history, get_money_flow_history


class SalesReportView(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.pack(fill="both", expand=True, padx=10, pady=10)
        self.current_view = "sales"
        self.build_ui()
        self.set_view("sales")

    def build_ui(self):
        # Header
        self.header = ctk.CTkLabel(self, text="Sales History", font=ctk.CTkFont(size=20, weight="bold"))
        self.header.pack(pady=12)

        # Separate frame for view buttons
        view_frame = ctk.CTkFrame(self)
        view_frame.pack(fill="x", padx=10, pady=(0, 2))

        view_sales_btn = ctk.CTkButton(
            view_frame,
            text="View Sales",
            width=120,
            command=lambda: self.set_view("sales")
        )
        view_sales_btn.pack(side="left", padx=8, pady=8)

        view_money_flow_btn = ctk.CTkButton(
            view_frame,
            text="View Money Flow",
            width=120,
            command=lambda: self.set_view("money_flow")
        )
        view_money_flow_btn.pack(side="left", pady=8)

        sales_frame = ctk.CTkFrame(self, corner_radius=12)
        sales_frame.pack(fill="both", expand=True, padx=10, pady=(0, 2))

        self.sales_tv = ttk.Treeview(sales_frame, columns=(), show="headings", height=14)

        scrollbar = ttk.Scrollbar(sales_frame, orient="vertical", command=self.sales_tv.yview)
        self.sales_tv.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.sales_tv.pack(fill="both", expand=True, padx=5, pady=5)

        # Bottom frame for status and total
        bottom_frame = ctk.CTkFrame(self)
        bottom_frame.pack(fill="x", pady=(4, 0))

        self.status_label = ctk.CTkLabel(bottom_frame, text="", text_color="#cbd5e1", font=ctk.CTkFont(size=12))
        self.status_label.pack(anchor="w", side="left")

        self.total_label = ctk.CTkLabel(bottom_frame, text="Total Sales: ₱0.00", text_color="#fbbf24", font=ctk.CTkFont(size=12, weight="bold"))
        self.total_label.pack(anchor="e", side="right")

    def set_view(self, view_type):
        self.current_view = view_type
        if view_type == "sales":
            self.header.configure(text="Sales History")
            self.total_label.configure(text="Total Sales: ₱0.00")
            columns = ("sale_id", "product_name", "unit_price", "quantity", "subtotal", "sale_date", "payment_method", "status", "customer_name")
            headings = [
                ("sale_id", "Sale ID", 70),
                ("product_name", "Product", 180),
                ("unit_price", "Unit Price", 100),
                ("quantity", "Qty", 60),
                ("subtotal", "Subtotal", 100),
                ("sale_date", "Date", 150),
                ("payment_method", "Payment", 100),
                ("status", "Status", 90),
                ("customer_name", "Customer", 160),
            ]
        elif view_type == "money_flow":
            self.header.configure(text="Money Flow History")
            self.total_label.configure(text="Total Flow: ₱0.00")
            columns = ("transaction_type", "date", "product_name", "quantity", "amount")
            headings = [
                ("transaction_type", "Type", 100),
                ("date", "Date", 150),
                ("product_name", "Product", 180),
                ("quantity", "Qty", 60),
                ("amount", "Amount", 100),
            ]
        
        self.sales_tv["columns"] = columns
        for col, title_text, width in headings:
            self.sales_tv.heading(col, text=title_text)
            self.sales_tv.column(col, width=width, anchor="center")
        
        self.sales_tv.delete(*self.sales_tv.get_children())
        if view_type == "sales":
            self.load_sales_data()
        elif view_type == "money_flow":
            self.load_money_flow_data()

    def load_sales_data(self):
        sales_rows = get_sales_history() or []
        total_sales = 0
        for sale in sales_rows:
            sale_date = sale.get("sale_date")
            if sale_date is not None:
                sale_date = sale_date.strftime("%Y-%m-%d %H:%M") if hasattr(sale_date, "strftime") else str(sale_date)
            subtotal = float(sale.get('subtotal', 0))
            total_sales += subtotal
            self.sales_tv.insert(
                "",
                "end",
                values=(
                    sale.get("sale_id"),
                    sale.get("product_name"),
                    f"₱{float(sale.get('unit_price', 0)):.2f}",
                    sale.get("quantity"),
                    f"₱{subtotal:.2f}",
                    sale_date,
                    sale.get("payment_method"),
                    sale.get("status"),
                    sale.get("customer_name") or "Walk-in",
                ),
            )
        self.total_label.configure(text=f"Total Sales: ₱{total_sales:.2f}")
        self.status_label.configure(text=f"Loaded {len(sales_rows)} sales records")

    def load_money_flow_data(self):
        money_flow_rows = get_money_flow_history() or []
        total_flow = 0
        for row in money_flow_rows:
            date = row.get("date")
            if date is not None:
                date = date.strftime("%Y-%m-%d %H:%M") if hasattr(date, "strftime") else str(date)
            amount = float(row.get('amount', 0))
            # For restock, make amount negative to show outflow
            if row.get("transaction_type") == "RESTOCK":
                amount = -amount
            total_flow += amount
            self.sales_tv.insert(
                "",
                "end",
                values=(
                    row.get("transaction_type"),
                    date,
                    row.get("product_name"),
                    row.get("quantity"),
                    f"₱{amount:.2f}",
                ),
            )
        self.total_label.configure(text=f"Total Flow: ₱{total_flow:.2f}")
        self.status_label.configure(text=f"Loaded {len(money_flow_rows)} transactions")
