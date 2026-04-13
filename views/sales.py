import customtkinter as ctk
from tkinter import ttk
from models.sales import get_sales_history


class SalesReportView(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.pack(fill="both", expand=True, padx=10, pady=10)
        self.build_ui()
        self.load_sales()

    def build_ui(self):
        # Header - separated and centered like other windows
        header = ctk.CTkLabel(self, text="Sales History", font=ctk.CTkFont(size=20, weight="bold"))
        header.pack(pady=12)

        # Separate frame for refresh button
        refresh_frame = ctk.CTkFrame(self)
        refresh_frame.pack(fill="x", padx=10, pady=(0, 2))

        refresh_btn = ctk.CTkButton(
            refresh_frame,
            text="Refresh",
            width=100,
            command=self.load_sales
        )
        refresh_btn.pack(side="right", padx=8, pady=8)

        sales_frame = ctk.CTkFrame(self, corner_radius=12)
        sales_frame.pack(fill="both", expand=True, padx=10, pady=(0, 2))

        columns = (
            "sale_id",
            "product_name",
            "unit_price",
            "quantity",
            "subtotal",
            "sale_date",
            "payment_method",
            "status",
            "customer_name",
        )
        self.sales_tv = ttk.Treeview(sales_frame, columns=columns, show="headings", height=14)
        heading_info = [
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

        for col, title_text, width in heading_info:
            self.sales_tv.heading(col, text=title_text)
            self.sales_tv.column(col, width=width, anchor="center")

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

    def load_sales(self):
        self.sales_tv.delete(*self.sales_tv.get_children())
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
        self.status_label.configure(text=f"{len(sales_rows)} sale records loaded.")
        self.total_label.configure(text=f"Total Sales: ₱{total_sales:.2f}")
