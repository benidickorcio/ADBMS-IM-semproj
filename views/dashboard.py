import customtkinter as ctk
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['font.family'] = 'Arial'
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta
from database import get_connection
import numpy as np
import tkinter as tk
from tkinter import ttk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

BG        = "#111827"
CARD      = "#1f2937"
CARD2     = "#162032"
BORDER    = "#374151"
CYAN      = "#22d3ee"
PURPLE    = "#a78bfa"
PINK      = "#f472b6"
AMBER     = "#fbbf24"
BLUE      = "#60a5fa"
GREEN     = "#34d399"
RED       = "#f87171"
SUBTEXT   = "#6b7280"
TEXT      = "#f9fafb"

def get_total_customers():
    """Get total number of active customers from database"""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) AS total FROM customers WHERE is_deleted = FALSE")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result['total'] if result else 0
    except Exception as e:
        print(f"Error fetching customers: {e}")
        return 0

def get_total_products():
    """Get total number of products from database"""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) AS total FROM products")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result['total'] if result else 0
    except Exception as e:
        print(f"Error fetching products: {e}")
        return 0

def get_daily_revenue():
    """Get today's revenue"""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        today = datetime.now().strftime("%Y-%m-%d")
        cursor.execute(
            "SELECT COALESCE(SUM(total_amount), 0) AS revenue FROM sales WHERE DATE(sale_date) = %s AND status = 'PAID'",
            (today,)
        )
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return float(result['revenue']) if result else 0.0
    except Exception as e:
        print(f"Error fetching daily revenue: {e}")
        return 0.0

def get_monthly_revenue():
    """Get current month's revenue"""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        today = datetime.now()
        month_start = today.replace(day=1).strftime("%Y-%m-%d")
        cursor.execute(
            "SELECT COALESCE(SUM(total_amount), 0) AS revenue FROM sales WHERE DATE(sale_date) >= %s AND status = 'PAID'",
            (month_start,)
        )
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return float(result['revenue']) if result else 0.0
    except Exception as e:
        print(f"Error fetching monthly revenue: {e}")
        return 0.0

def get_yearly_revenue():
    """Get current year's revenue"""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        year = datetime.now().year
        cursor.execute(
            "SELECT COALESCE(SUM(total_amount), 0) AS revenue FROM sales WHERE YEAR(sale_date) = %s AND status = 'PAID'",
            (year,)
        )
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return float(result['revenue']) if result else 0.0
    except Exception as e:
        print(f"Error fetching yearly revenue: {e}")
        return 0.0

def get_transactions_log(limit=20):
    """Get recent transactions log from database"""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT 
                transaction_id,
                sale_id,
                created_by,
                transaction_date,
                status,
                message
            FROM transactions 
            ORDER BY transaction_date DESC 
            LIMIT %s
        """, (limit,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows
    except Exception as e:
        print(f"Error fetching transactions log: {e}")
        return []

def get_revenue_trend(days=7):
    """Get revenue trend for sparkline (last N days)"""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        data = []
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            cursor.execute(
                "SELECT COALESCE(SUM(total_amount), 0) AS revenue FROM sales WHERE DATE(sale_date) = %s AND status = 'PAID'",
                (date,)
            )
            result = cursor.fetchone()
            data.insert(0, float(result['revenue']) if result else 0.0)
        cursor.close()
        conn.close()
        return data
    except Exception as e:
        print(f"Error fetching revenue trend: {e}")
        return [0] * days

def date_and_time():
    """Return current date and time"""
    now = datetime.now()
    return now.strftime("%Y-%m-%d %I:%M:%S %p")

def show_total_customers():
    """Get total customers for mini action card"""
    return get_total_customers()

def show_total_products():
    """Get total products for mini action card"""
    return get_total_products()

def daily_revenue():
    """Get daily revenue for mini action card"""
    return get_daily_revenue()

def monthly_revenue():
    """Get monthly revenue for mini action card"""
    return get_monthly_revenue()

def yearly_revenue():
    """Get yearly revenue for mini action card"""
    return get_yearly_revenue()

def best_selling_products(parent, limit=3):
    """Create a best selling products table using CTE and RANK."""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT
                p.product_id,
                p.name,
                SUM(si.quantity) AS total_quantity,
                COUNT(si.sale_id) AS transaction_count,
                SUM(si.subtotal) AS total_revenue,
                RANK() OVER (ORDER BY SUM(si.quantity) DESC) AS sales_rank
            FROM sold_items si
            INNER JOIN products p ON p.product_id = si.product_id
            GROUP BY p.product_id, p.name
            ORDER BY sales_rank ASC, total_revenue DESC
            LIMIT %s
        """

        cursor.execute(query, (limit,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        if not rows:
            empty_label = ctk.CTkLabel(parent, text="No sales data available",
                                      text_color=SUBTEXT,
                                      font=ctk.CTkFont("Arial", 11))
            empty_label.pack(padx=14, pady=20)
            return

        columns = ("rank", "product", "units", "transactions", "revenue")
        tree = ttk.Treeview(parent, columns=columns, show="headings", height=6)
        tree.heading("rank", text="Rank", anchor="center")
        tree.heading("product", text="Product", anchor="center")
        tree.heading("units", text="Units", anchor="center")
        tree.heading("transactions", text="Transactions", anchor="center")
        tree.heading("revenue", text="Revenue", anchor="center")

        tree.column("rank", width=60, anchor="center")
        tree.column("product", width=240, anchor="center")
        tree.column("units", width=80, anchor="center")
        tree.column("transactions", width=110, anchor="center")
        tree.column("revenue", width=120, anchor="center")

        for row in rows:
            rank = row['sales_rank']
            name = row['name'] if len(row['name']) <= 30 else row['name'][:30] + "..."
            quantity = int(row['total_quantity'])
            transactions = int(row['transaction_count'])
            revenue = float(row['total_revenue'])

            tree.insert("", "end", values=(
                str(rank),
                name,
                quantity,
                transactions,
                f"₱{revenue:,.2f}"
            ))

        vsb = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
        tree.configure(yscroll=vsb.set)
        vsb.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)

    except Exception as e:
        print(f"Error fetching best selling products: {e}")
        error_label = ctk.CTkLabel(parent, text=f"Error loading data: {str(e)}",
                                   text_color=RED,
                                   font=ctk.CTkFont("Arial", 11))
        error_label.pack(padx=14, pady=14)

def show_transactions_log(parent, limit=15):
    """Create a transactions log table showing recent transactions."""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT 
                transaction_id,
                sale_id,
                created_by,
                transaction_date,
                status,
                message
            FROM transactions 
            ORDER BY transaction_date DESC 
            LIMIT %s
        """, (limit,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        if not rows:
            empty_label = ctk.CTkLabel(parent, text="No transactions yet",
                                      text_color=SUBTEXT,
                                      font=ctk.CTkFont("Arial", 11))
            empty_label.pack(padx=14, pady=20)
            return

        columns = ("id", "sale_id", "user", "date", "status", "message")
        tree = ttk.Treeview(parent, columns=columns, show="headings", height=6)
        tree.heading("id", text="ID", anchor="center")
        tree.heading("sale_id", text="Sale ID", anchor="center")
        tree.heading("user", text="User", anchor="center")
        tree.heading("date", text="Date", anchor="center")
        tree.heading("status", text="Status", anchor="center")
        tree.heading("message", text="Message", anchor="center")

        tree.column("id", width=50, anchor="center")
        tree.column("sale_id", width=70, anchor="center")
        tree.column("user", width=100, anchor="center")
        tree.column("date", width=150, anchor="center")
        tree.column("status", width=80, anchor="center")
        tree.column("message", width=250, anchor="w")

        for row in rows:
            trans_id = row['transaction_id']
            sale_id = row['sale_id'] if row['sale_id'] else "N/A"
            user = row['created_by']
            date = row['transaction_date'].strftime("%Y-%m-%d %H:%M") if row['transaction_date'] else ""
            status = row['status']
            message = row['message'] if row['message'] else ""
            
            # Truncate long messages
            if message and len(message) > 40:
                message = message[:40] + "..."
            
            # Color tag for status
            tag = "success" if status == "SUCCESS" else "failed"
            
            tree.insert("", "end", values=(
                trans_id,
                sale_id,
                user,
                date,
                status,
                message
            ), tags=(tag,))

        # Configure tag colors
        tree.tag_configure("success", foreground=GREEN)
        tree.tag_configure("failed", foreground=RED)

        vsb = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
        tree.configure(yscroll=vsb.set)
        vsb.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)

    except Exception as e:
        print(f"Error fetching transactions log: {e}")
        error_label = ctk.CTkLabel(parent, text=f"Error loading data: {str(e)}",
                                   text_color=RED,
                                   font=ctk.CTkFont("Arial", 11))
        error_label.pack(padx=14, pady=14)

# ── Mini Action Card Component ────────────────────────────
def create_mini_stat_card(parent, label, value, color, subtitle, sparkline_data):
    """Create a mini stat card widget"""
    f = ctk.CTkFrame(parent, fg_color=CARD,
                        corner_radius=12,
                        border_width=1, border_color=BORDER)
    f.pack(side="left", fill="both", expand=True, padx=(0, 12))

    # Top colored accent bar
    ctk.CTkFrame(f, fg_color=color,
                    height=2, corner_radius=0).pack(fill="x")

    # Label
    ctk.CTkLabel(f, text=label, text_color=SUBTEXT,
                    font=ctk.CTkFont("Arial", 9),
                    anchor="w").pack(fill="x", padx=14, pady=(12, 2))

    # Big value
    value_text = f"₱{value:,.0f}" if isinstance(value, (int, float)) and value > 100 else str(value)
    ctk.CTkLabel(f, text=value_text, text_color=color,
                    font=ctk.CTkFont("Arial", 28, "bold"),
                    anchor="w").pack(fill="x", padx=14, pady=2)

    # Subtitle
    ctk.CTkLabel(f, text=subtitle, text_color=SUBTEXT,
                    font=ctk.CTkFont("Arial", 8),
                    anchor="w").pack(fill="x", padx=14, pady=(2, 8))

    # Sparkline
    create_sparkline(f, sparkline_data, color)

    return f

def create_sparkline(parent, data, color, figsize=(2.8, 0.7), dpi=90):
    """Create a sparkline chart"""
    try:
        fig = plt.figure(figsize=figsize, dpi=dpi)
        fig.patch.set_facecolor(CARD)
        ax = fig.add_subplot(1, 1, 1)
        ax.set_facecolor(CARD)

        x = np.arange(len(data))
        ax.plot(x, data, color=color, linewidth=1.6, solid_capstyle="round")
        ax.fill_between(x, data, 0, color=color, alpha=0.15, linewidth=0)
        
        if len(data) > 0:
            ax.scatter([x[-1]], [data[-1]], color=color, s=18, zorder=5)

        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_ylim(bottom=0)
        ax.margins(x=0.04, y=0.2)
        fig.tight_layout(pad=0)

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="x", padx=10, pady=(2, 10))
        plt.close(fig)
    except Exception as e:
        print(f"Error creating sparkline: {e}")

def base_fig(figsize=(6, 3.2)):
    fig = plt.figure(figsize=figsize, dpi=100)
    fig.patch.set_facecolor(CARD)
    return fig


def style_axis(ax, title="", xlabel=True):
    ax.set_facecolor(CARD)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(BORDER)
    ax.spines['bottom'].set_color(BORDER)
    ax.tick_params(axis='y', colors=SUBTEXT, labelsize=8)
    ax.tick_params(axis='x', colors=SUBTEXT, labelsize=8)
    ax.grid(color=BORDER, alpha=0.4, linestyle='--', linewidth=0.5)
    ax.set_axisbelow(True)
    if title:
        ax.set_title(title, color=TEXT, fontsize=11,
                        fontweight="bold", pad=10)


def embed(fig, parent):
    c = FigureCanvasTkAgg(fig, master=parent)
    c.draw()
    c.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
    plt.close(fig)


def get_sales_history_data(days=12):
    """Return last N days sales totals for the line graph."""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT DATE(sale_date) AS sale_day, COALESCE(SUM(total_amount), 0) AS total_amount "
            "FROM sales WHERE status = 'PAID' AND sale_date >= DATE_SUB(CURDATE(), INTERVAL %s DAY) "
            "GROUP BY sale_day ORDER BY sale_day ASC",
            (days - 1,)
        )
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        sales_by_date = {row['sale_day'].strftime('%Y-%m-%d'): float(row['total_amount'] or 0.0) for row in rows}
        labels = []
        values = []
        for i in range(days - 1, -1, -1):
            date_str = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            labels.append(date_str[5:])
            values.append(sales_by_date.get(date_str, 0.0))
        return labels, values
    except Exception as e:
        print(f"Error fetching sales history: {e}")
        return [], []


def get_inventory_status_data(limit=6):
    """Return inventory product names and status values for the bar graph."""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT name, status FROM products ORDER BY quantity DESC LIMIT %s",
            (limit,)
        )
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        labels = []
        values = []
        colors = []
        status_map = {'IN STOCK': 3, 'LOW STOCK': 2, 'OUT OF STOCK': 1}
        color_map = {'IN STOCK': GREEN, 'LOW STOCK': AMBER, 'OUT OF STOCK': RED}

        for row in rows:
            labels.append(shorten_product_label(row['name']))
            values.append(status_map.get(row['status'], 0))
            colors.append(color_map.get(row['status'], SUBTEXT))

        return labels, values, colors
    except Exception as e:
        print(f"Error fetching inventory status: {e}")
        return [], [], []


def shorten_product_label(name, max_length=10):
    """Return a compact product label, preferring a size token when available."""
    import re
    size_match = re.search(r'(\d+(?:\.\d+)?\s*(?:kg|g|l|ml|pcs|pc|oz|lb|lbs))', name, re.I)
    if size_match:
        return size_match.group(1).strip().upper()

    cleaned = name.replace('-', ' ').replace('_', ' ')
    if len(cleaned) <= max_length:
        return cleaned

    parts = cleaned.split()
    if len(parts) >= 2:
        first = parts[0][:3].upper()
        second = parts[1][:3].upper()
        return f"{first}{second}"

    return cleaned[:max_length] + '...'


class DashboardScreen(ctk.CTkFrame):
    """Embedded dashboard frame for main application"""
    def __init__(self, parent):
        super().__init__(parent, fg_color=BG, corner_radius=0)
        
        # Clock updater
        self.clock_label = None
        self._build()
        self._update_clock()

    def _build(self):
        """Build the dashboard layout"""
        main = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        main.pack(fill="both", expand=True)

        topbar = ctk.CTkFrame(main, fg_color=CARD, corner_radius=0, height=50)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)

        ctk.CTkLabel(topbar, text="📊 Dashboard", text_color=TEXT,
                        font=ctk.CTkFont("Arial", 14, "bold"),
                        anchor="w").pack(side="left", padx=20, pady=14)

        self.clock_label = ctk.CTkLabel(topbar, text="",
                        text_color=CYAN,
                        font=ctk.CTkFont("Arial", 10, "bold"))
        self.clock_label.pack(side="right", padx=20, pady=14)

        body = ctk.CTkScrollableFrame(main, fg_color=BG, corner_radius=0)
        body.pack(fill="both", expand=True, padx=18, pady=14)

        self._create_mini_stats_row(body)

        self._create_charts_row(body)

        self._create_reserved_space(body)

    def _create_mini_stats_row(self, parent):
        """Create the mini stat cards row"""
        # Title
        ctk.CTkLabel(parent, text="OVERVIEW", text_color=TEXT,
                        font=ctk.CTkFont("Arial", 12, "bold"),
                        anchor="w").pack(fill="x", pady=(0, 12))

        # Mini stats container
        stats_row = ctk.CTkFrame(parent, fg_color=BG, corner_radius=0)
        stats_row.pack(fill="x", pady=(0, 20))

        # 1. Total Customers
        customers = show_total_customers()
        trend = [max(0, customers - 5 + i) for i in range(7)]
        create_mini_stat_card(stats_row, "Total Customers", customers, CYAN, 
                            "Active Customers", trend)

        # 2. Total Products
        products = show_total_products()
        trend = [max(0, products - 3 + i) for i in range(7)]
        create_mini_stat_card(stats_row, "Total Products", products, PURPLE,
                            "In inventory", trend)

        # 3. Daily Revenue
        daily_rev = daily_revenue()
        daily_trend = get_revenue_trend(7)
        create_mini_stat_card(stats_row, "Daily Revenue", daily_rev, GREEN,
                            "Today's sales", daily_trend)

        # 4. Monthly Revenue
        monthly_rev = monthly_revenue()
        monthly_trend = get_revenue_trend(7)
        create_mini_stat_card(stats_row, "Monthly Revenue", monthly_rev, AMBER,
                            "This month", monthly_trend)
        # 5. Yearly Revenue
        yearly_rev = yearly_revenue()
        yearly_trend = get_revenue_trend(7)
        create_mini_stat_card(stats_row, "Yearly Revenue", yearly_rev, PINK,
                            "This year", yearly_trend)

    def _create_charts_row(self, parent):
        """Create sales history and inventory status charts."""
        charts_frame = ctk.CTkFrame(parent, fg_color=BG, corner_radius=0)
        charts_frame.pack(fill="both", expand=True, pady=(0, 20))

        # Sales history line chart
        sales_card = ctk.CTkFrame(charts_frame, fg_color=CARD,
                                    corner_radius=12,
                                    border_width=1, border_color=BORDER)
        sales_card.pack(side="left", fill="both", expand=True, padx=(0, 8))
        ctk.CTkLabel(sales_card, text="Sales History", text_color=TEXT,
                    font=ctk.CTkFont("Arial", 12, "bold"),
                    anchor="w").pack(fill="x", padx=14, pady=(14, 0))
        self._line_chart(sales_card)

        # Inventory status bar chart
        inventory_card = ctk.CTkFrame(charts_frame, fg_color=CARD,
                                    corner_radius=12,
                                    border_width=1, border_color=BORDER)
        inventory_card.pack(side="left", fill="both", expand=True)
        ctk.CTkLabel(inventory_card, text="Inventory Status", text_color=TEXT,
                    font=ctk.CTkFont("Arial", 12, "bold"),
                    anchor="w").pack(fill="x", padx=14, pady=(14, 0))
        self._inventory_bar_chart(inventory_card)

    def _line_chart(self, parent):
        labels, values = get_sales_history_data(12)
        fig = base_fig((6, 3.2))
        ax = fig.add_subplot(1, 1, 1)
        style_axis(ax, title="Sales History")

        x = np.arange(len(labels))
        ax.plot(x, values, color=CYAN, linewidth=2.5, zorder=3)
        ax.fill_between(x, values, color=CYAN, alpha=0.12)
        ax.scatter(x, values, color=CYAN, s=30, zorder=4)

        ax.set_xticks(x)
        ax.set_xticklabels(labels, color=SUBTEXT, fontsize=8)
        ax.yaxis.set_major_formatter(
            plt.FuncFormatter(lambda v, _: f"₱{int(v):,}" if v else "₱0"))
        fig.tight_layout(pad=1.2)
        embed(fig, parent)

    def _inventory_bar_chart(self, parent):
        labels, values, colors = get_inventory_status_data(6)
        fig = base_fig((6, 3.2))
        ax = fig.add_subplot(1, 1, 1)
        style_axis(ax, title="Inventory Status")

        x = np.arange(len(labels))
        bars = ax.bar(x, values, color=colors, width=0.65, zorder=3, alpha=0.9)

        status_labels = {1: 'OUT', 2: 'LOW', 3: 'IN'}
        ax.set_yticks([1, 2, 3])
        ax.set_yticklabels(['Out of Stock', 'Low Stock', 'In Stock'], color=SUBTEXT, fontsize=8)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, color=SUBTEXT, fontsize=8)

        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2,
                    val + 0.08,
                    status_labels.get(val, ''),
                    ha="center", va="bottom",
                    color=TEXT, fontsize=8, fontweight="bold")

        fig.tight_layout(pad=1.2)
        embed(fig, parent)

    def _create_reserved_space(self, parent):
        """Create best selling products analytics table."""
        ctk.CTkLabel(parent, text="Additional Analytics - Best Selling Products", text_color=TEXT,
                     font=ctk.CTkFont("Arial", 12, "bold"),
                     anchor="w").pack(fill="x", pady=(20, 12))

        best_selling_products(parent, limit=15)

        # Transactions Log Section
        ctk.CTkLabel(parent, text="Transactions Log", text_color=TEXT,
                     font=ctk.CTkFont("Arial", 12, "bold"),
                     anchor="w").pack(fill="x", pady=(20, 12))

        show_transactions_log(parent, limit=15)

    def _update_clock(self):
        """Update the clock display"""
        if self.clock_label:
            self.clock_label.configure(text=date_and_time())
        self.after(1000, self._update_clock)


if __name__ == "__main__":
    class DashboardView(ctk.CTk):
        def __init__(self):
            super().__init__()
            self.title("ERMITA LPG Refilling Station - Dashboard")
            self.geometry("1200x800")
            self.minsize(1000, 700)
            self.configure(fg_color=BG)
            
            self.dashboard = DashboardScreen(self)
            self.dashboard.pack(fill="both", expand=True)
    
    app = DashboardView()
    app.mainloop()
