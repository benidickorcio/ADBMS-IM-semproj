import customtkinter as ctk
from views.login import CTKLoginWindow
from views.pos import POSScreen
from views.customers_ui import CustomersScreen
from views.inventory import InventoryAndRestockScreen
from views.sales import SalesReportView
from views.dashboard import DashboardScreen
from views.settings import SettingsWindow
from utils.auth import logout as auth_logout, set_current_user
from utils.colors import get_color
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")


class CTKMainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("ERMITA LPG Refilling Station Login")

        self.login_window = CTKLoginWindow(self, on_success=self.on_login_success)
        self.login_window.pack(fill="both", expand=True)

    def on_login_success(self, user):
        self.current_user = user
        self.title("ERMITA LPG Refilling Station")

        if hasattr(self.login_window, "fullscreen") and self.login_window.fullscreen:
            self.attributes("-fullscreen", True)
        else:
            self.attributes("-fullscreen", False)

        self.login_window.destroy()
        self._setup_layout()


    def _setup_layout(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.header_frame = ctk.CTkFrame(self, height=60, corner_radius=10, fg_color=get_color("bg_secondary"))
        self.header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=20, pady=(20, 10))

        self.header_label = ctk.CTkLabel(
            self.header_frame,
            text="ERMITA LPG Refilling Station",
            text_color=get_color("primary"),
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.header_label.pack(pady=12)

        self.sidebar_frame = ctk.CTkFrame(self, width=300, corner_radius=10, fg_color=get_color("bg_secondary"))
        self.sidebar_frame.grid(row=1, column=0, sticky="nsw", padx=(20, 10), pady=(10, 20))

        self.panel_frame = ctk.CTkFrame(self, corner_radius=15, fg_color=get_color("bg_primary"))
        self.panel_frame.grid(row=1, column=1, sticky="nsew", padx=(10, 20), pady=(10, 20))

        role     = self.current_user.get("role",     "CASHIER")
        username = self.current_user.get("username", "ADMIN")

        title_text = f"{role.title()} [{username}]"
        title = ctk.CTkLabel(
            self.sidebar_frame,
            text=title_text,
            text_color=get_color("primary"),
            font=ctk.CTkFont(size=20, weight="bold"),
            fg_color="transparent"
        )
        title.pack(pady=(24, 20))

        self.pos_btn = ctk.CTkButton(self.sidebar_frame, text="💻Point of Sales", font=ctk.CTkFont(size=15, weight="bold"), command=self.show_pos, width=200, fg_color=get_color("bg_secondary"), hover_color=get_color("button_primary_dark"), height=40)
        self.settings_btn = ctk.CTkButton(self.sidebar_frame, text="⚙️SETTINGS", font=ctk.CTkFont(size=15, weight="bold"), command=self.show_settings, width=200, fg_color=get_color("bg_secondary"), hover_color=get_color("button_primary_dark"), height=40)
        self.customers_btn = ctk.CTkButton(self.sidebar_frame, text="👥Customers", font=ctk.CTkFont(size=15, weight="bold"), command=self.show_customers, width=200, fg_color=get_color("bg_secondary"), hover_color=get_color("button_primary_dark"), height=40)
        self.logout_btn = ctk.CTkButton(self.sidebar_frame, text="🔚Logout",font=ctk.CTkFont(size=15, weight="bold"), command=self._logout, fg_color=get_color("bg_secondary"), hover_color=get_color("status_error_dark"), width=200,height=40)


        if role == "CASHIER":
            self.operations_label = ctk.CTkLabel(self.sidebar_frame, text="OPERATIONS ───────", text_color=get_color("primary"), font=ctk.CTkFont(size=13, weight="bold"), fg_color="transparent")
            self.operations_label.pack(anchor="w", padx=10)
            self.pos_btn.pack(pady=8, padx=10)
            self.customers_btn.pack(pady=8, padx=10)
            
            self.system_label = ctk.CTkLabel(self.sidebar_frame, text="SYSTEM ─────────", text_color=get_color("primary"), font=ctk.CTkFont(size=13, weight="bold"), fg_color="transparent")
            self.system_label.pack(anchor="w", padx=10)
            self.settings_btn.pack(pady=8, padx=10)
            self.logout_btn.pack(pady=8, padx=10)
            self.show_pos()

            return

        # Admin gets full access
        self.operations_label = ctk.CTkLabel(self.sidebar_frame, text="OPERATIONS ───────", text_color=get_color("primary"), font=ctk.CTkFont(size=13, weight="bold"), fg_color="transparent")
        self.operations_label.pack(anchor="w", padx=10)
        self.dashboard_btn = ctk.CTkButton(self.sidebar_frame, text="📈Dashboard",font=ctk.CTkFont(size=15, weight="bold"), command=self.show_dashboard,fg_color=get_color("bg_secondary"), hover_color=get_color("button_primary_dark"), width=200, height=40)
        self.dashboard_btn.pack(pady=8, padx=10)
        self.sales_btn = ctk.CTkButton(self.sidebar_frame, text="💰Sales History",font=ctk.CTkFont(size=15, weight="bold"), command=self.show_sales, width=200,fg_color=get_color("bg_secondary"), hover_color=get_color("button_primary_dark"), height=40)
        self.sales_btn.pack(pady=8, padx=10)
        self.pos_btn.pack(pady=8, padx=10)
        
        self.management_label = ctk.CTkLabel(self.sidebar_frame, text="MANAGEMENT ──────", text_color=get_color("primary"), font=ctk.CTkFont(size=13, weight="bold"), fg_color="transparent")
        self.management_label.pack(anchor="w", padx=10)
        self.customers_btn = ctk.CTkButton(self.sidebar_frame, text="👥Customers",font=ctk.CTkFont(size=15, weight="bold"), command=self.show_customers,fg_color=get_color("bg_secondary"), hover_color=get_color("button_primary_dark"), width=200, height=40)
        self.customers_btn.pack(pady=8, padx=10)
        
        
        self.inventory_btn = ctk.CTkButton(self.sidebar_frame, text="📚Inventory",font=ctk.CTkFont(size=15, weight="bold"), command=self.show_inventory,fg_color=get_color("bg_secondary"), hover_color=get_color("button_primary_dark"), width=200, height=40)
        self.inventory_btn.pack(pady=8, padx=10)
        self.system_label = ctk.CTkLabel(self.sidebar_frame,text="SYSTEM ─────────", text_color=get_color("primary"), font=ctk.CTkFont(size=13, weight="bold"), fg_color="transparent")
        self.system_label.pack(anchor="w", padx=10)
        self.settings_btn = ctk.CTkButton(self.sidebar_frame, text="⚙️Settings",font=ctk.CTkFont(size=15, weight="bold"), command=self.show_settings,fg_color=get_color("bg_secondary"), hover_color=get_color("button_primary_dark"), width=200, height=40)
        self.settings_btn.pack(pady=8, padx=10)
        self.logout_btn.pack(pady=8, padx=10)
        self.show_dashboard()

    def clear_content(self):
        for widget in self.panel_frame.winfo_children():
            widget.destroy()

    def show_dashboard(self):
        self.clear_content()
        self.dashboard_screen = DashboardScreen(self.panel_frame)
        self.dashboard_screen.pack(fill="both", expand=True)

    def show_inventory(self):
        self.clear_content()
        self.inventory_screen = InventoryAndRestockScreen(self.panel_frame)

    def show_sales(self):
        self.clear_content()
        self.sales_screen = SalesReportView(self.panel_frame)

    def show_pos(self):
        self.clear_content()
        self.pos_screen = POSScreen(self.panel_frame, on_checkout=self._refresh_views_after_checkout)

    def _refresh_views_after_checkout(self, sale_id):
        if getattr(self, "sales_screen", None):
            try:
                self.sales_screen.load_sales_data()
            except Exception:
                pass
        if getattr(self, "inventory_screen", None):
            try:
                self.inventory_screen.load_inventory()
            except Exception:
                pass

    def show_customers(self):
        self.clear_content()
        self.customers_screen = CustomersScreen(self.panel_frame)


    def show_settings(self):
        # Clear current content
        self.clear_content()
        
        # Create settings window as a frame in the panel with callbacks
        self.settings_window = SettingsWindow(
            self.panel_frame,
            on_delete_own_account=self._logout,
            parent_app=self
        )
        self.settings_window.pack(fill="both", expand=True, padx=20, pady=20)

    def _update_stats(self, text):
        for widget in self.stats_card.winfo_children():
            widget.destroy()
        self.stat_label = ctk.CTkLabel(self.stats_card, text=text, font=ctk.CTkFont(size=14))
        self.stat_label.pack(anchor="w", padx=16, pady=10)

    def _logout(self):
        auth_logout()
        set_current_user(None)

        # Clear current dynamic widgets from previous session
        for child in self.winfo_children():
            child.destroy()

        self.title("ERMITA LPG Refilling Station Login")
        self.login_window = CTKLoginWindow(self, on_success=self.on_login_success)
        self.login_window.pack(fill="both", expand=True)

        


if __name__ == "__main__":
    window = CTKMainApp()
    window.mainloop()
