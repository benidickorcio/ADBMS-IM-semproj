import customtkinter as ctk
from database import get_all_users, delete_user_by_username, update_username, update_password, add_user, get_admin_count, verify_password
from utils.auth import get_current_user, is_admin
import hashlib
import tkinter as tk
from tkinter import messagebox


class SettingsWindow(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        
        # Get current user
        self.current_user = get_current_user()
        self.role = self.current_user.get("role", "CASHIER") if self.current_user else "CASHIER"
        
        self._setup_ui()
    
    def _show_message(self, title, message, msg_type="info"):
        """Show a messagebox dialog."""
        if msg_type == "error":
            messagebox.showerror(title, message)
        elif msg_type == "success":
            messagebox.showinfo(title, message)
        elif msg_type == "warning":
            messagebox.showwarning(title, message)
        else:
            messagebox.showinfo(title, message)
    
    def _hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _setup_ui(self):
        # Title
        title = ctk.CTkLabel(
            self,
            text="⚙️ Settings",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=20)
        
        # Role indicator
        role_label = ctk.CTkLabel(
            self,
            text=f"Logged in as: {self.role}",
            font=ctk.CTkFont(size=14),
            text_color="#37E9FD"
        )
        role_label.pack(pady=(0, 20))
        
        # Create notebook/tabview for different settings
        self.tabview = ctk.CTkTabview(self, width=700, height=500)
        self.tabview.pack(pady=10, padx=20, fill="both", expand=True)
        
        # Add tabs based on role
        if self.role == "ADMIN":
            self._setup_admin_tabs()
        else:
            self._setup_cashier_tabs()
    
    def _setup_admin_tabs(self):
        # ========== ACCOUNTS TAB ==========
        self.accounts_tab = self.tabview.add("👥 Accounts")
        
        # Frame for accounts list
        list_frame = ctk.CTkFrame(self.accounts_tab)
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Label
        ctk.CTkLabel(
            list_frame,
            text="All User Accounts",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=10)
        
        # Scrollable frame for accounts
        self.accounts_scroll = ctk.CTkScrollableFrame(list_frame, label_text="Accounts")
        self.accounts_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Refresh button
        refresh_btn = ctk.CTkButton(
            list_frame,
            text="🔄 Refresh",
            command=self._load_accounts,
            width=150
        )
        refresh_btn.pack(pady=10)
        
        # ========== ADD ACCOUNT TAB ==========
        self.add_tab = self.tabview.add("➕ Add Account")
        self._setup_add_account_tab()
        
        # ========== DELETE ACCOUNT TAB ==========
        self.delete_tab = self.tabview.add("🗑️ Delete Account")
        self._setup_delete_account_tab()
        
        # ========== CHANGE USERNAME TAB ==========
        self.username_tab = self.tabview.add("📝 Change Username")
        self._setup_change_username_tab()
        
        # ========== CHANGE PASSWORD TAB ==========
        self.password_tab = self.tabview.add("🔑 Change Password")
        self._setup_change_password_tab()
        
        # Load accounts
        self._load_accounts()
    
    def _setup_add_account_tab(self):
        frame = ctk.CTkFrame(self.add_tab)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            frame,
            text="Add New Account",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=20)
        
        # Form container using grid
        form_frame = ctk.CTkFrame(frame, fg_color="transparent")
        form_frame.pack(pady=10)
        
        # Name row
        ctk.CTkLabel(form_frame, text="Full Name:", width=100, anchor="e").grid(row=0, column=0, pady=10, padx=5)
        self.add_name_entry = ctk.CTkEntry(form_frame, placeholder_text="Enter full name", width=250)
        self.add_name_entry.grid(row=0, column=1, pady=10, padx=5)
        
        # Username row
        ctk.CTkLabel(form_frame, text="Username:", width=100, anchor="e").grid(row=1, column=0, pady=10, padx=5)
        self.add_username_entry = ctk.CTkEntry(form_frame, placeholder_text="Enter username", width=250)
        self.add_username_entry.grid(row=1, column=1, pady=10, padx=5)
        
        # Password row
        ctk.CTkLabel(form_frame, text="Password:", width=100, anchor="e").grid(row=2, column=0, pady=10, padx=5)
        self.add_password_entry = ctk.CTkEntry(form_frame, show="*", placeholder_text="Enter password", width=250)
        self.add_password_entry.grid(row=2, column=1, pady=10, padx=5)
        
        # Role row
        ctk.CTkLabel(form_frame, text="Role:", width=100, anchor="e").grid(row=3, column=0, pady=10, padx=5)
        self.add_role_var = tk.StringVar(value="CASHIER")
        role_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        role_frame.grid(row=3, column=1, pady=10, padx=5, sticky="w")
        ctk.CTkRadioButton(role_frame, text="ADMIN", variable=self.add_role_var, value="ADMIN").pack(side="left", padx=10)
        ctk.CTkRadioButton(role_frame, text="CASHIER", variable=self.add_role_var, value="CASHIER").pack(side="left", padx=10)
        
        # Add button
        add_btn = ctk.CTkButton(
            frame,
            text="➕ Add Account",
            command=self._add_account,
            width=200,
            height=40
        )
        add_btn.pack(pady=20)
        
        # Message label
        self.add_msg = ctk.CTkLabel(frame, text="", text_color="red", font=ctk.CTkFont(size=12))
        self.add_msg.pack(pady=5)
    
    def _add_account(self):
        name = self.add_name_entry.get().strip()
        username = self.add_username_entry.get().strip()
        password = self.add_password_entry.get().strip()
        role = self.add_role_var.get()
        
        # Validation
        if not name or not username or not password:
            self._show_message("Error", "Please fill all fields", "error")
            return
        
        if len(username) < 3:
            self._show_message("Error", "Username must be at least 3 characters", "error")
            return
        
        if len(password) < 4:
            self._show_message("Error", "Password must be at least 4 characters", "error")
            return
        
        try:
            result = add_user(name, username, password, role)
            if result:
                self._show_message("Success", "Account added successfully!", "success")
                self.add_name_entry.delete(0, "end")
                self.add_username_entry.delete(0, "end")
                self.add_password_entry.delete(0, "end")
                self._load_accounts()
            else:
                self._show_message("Error", "Failed to add account", "error")
        except Exception as e:
            self._show_message("Error", f"Error: {str(e)}", "error")
    
    def _setup_delete_account_tab(self):
        frame = ctk.CTkFrame(self.delete_tab)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            frame,
            text="Delete Account",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=20)
        
        # ========== DELETE OTHER ACCOUNT SECTION ==========
        ctk.CTkLabel(
            frame,
            text="Select account to delete:",
            font=ctk.CTkFont(size=12)
        ).pack(pady=5)
        
        # Get all users for the dropdown
        all_users = get_all_users()
        # Filter out default admin accounts
        deletable_users = [u for u in all_users if u["username"] not in ["rnel"]]
        
        # Create dropdown options
        self.delete_user_var = tk.StringVar()
        user_options = []
        self.user_map = {}  # username -> user dict
        
        for user in deletable_users:
            display_name = f"{user['name']} ({user['role']})"
            user_options.append(display_name)
            self.user_map[display_name] = user
        
        if user_options:
            self.delete_user_var.set(user_options[0])
            self.delete_optmenu = ctk.CTkOptionMenu(
                frame,
                variable=self.delete_user_var,
                values=user_options,
                width=300
            )
            self.delete_optmenu.pack(pady=10)
        else:
            ctk.CTkLabel(frame, text="No deletable accounts", text_color="gray").pack(pady=10)
        
        delete_btn = ctk.CTkButton(
            frame,
            text="🗑️ Delete Account",
            command=self._delete_other_account,
            fg_color="#dc2626",
            width=200,
            height=40
        )
        delete_btn.pack(pady=10)
        
    
    def _delete_other_account(self):
        selected = self.delete_user_var.get()
        
        if not selected or selected not in self.user_map:
            messagebox.showerror("Error", "Please select an account")
            return
        
        user = self.user_map[selected]
        username = user["username"]
        fullname = user["name"]
        role = user["role"]
        
        # Check if trying to delete an admin when only 1 admin exists
        if role == "ADMIN":
            admin_count = get_admin_count()
            if admin_count <= 1:
                messagebox.showerror("Error", "Cannot delete the last admin account. At least 1 admin must remain in the system.")
                return
        
        # Show confirmation messagebox
        confirm_popup = ctk.CTkToplevel(self)
        confirm_popup.title("Confirm Delete")
        confirm_popup.geometry("400x180")
        
        ctk.CTkLabel(
            confirm_popup,
            text=f"Are you sure you want to delete\n\"{fullname}\" account?",
            font=ctk.CTkFont(size=14)
        ).pack(pady=30)
        
        btn_frame = ctk.CTkFrame(confirm_popup, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        ctk.CTkButton(
            btn_frame,
            text="Yes, Delete",
            fg_color="#dc2626",
            command=lambda: self._confirm_delete_other(username, confirm_popup),
            width=120
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=confirm_popup.destroy,
            width=120
        ).pack(side="left", padx=10)
    
    def _confirm_delete_other(self, username, popup):
        try:
            result = delete_user_by_username(username)
            if result:
                messagebox.showinfo("Success", "Account deleted successfully!")
                # Refresh the dropdown
                self._refresh_delete_dropdown()
                popup.destroy()
            else:
                messagebox.showerror("Error", "Cannot delete this account, atleast 1 admin must remain in the system.")
                popup.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Error: {str(e)}")
            popup.destroy()
    
    def _refresh_delete_dropdown(self):
        all_users = get_all_users()
        deletable_users = [u for u in all_users if u["username"] not in ["rnel"]]
        
        user_options = []
        self.user_map = {}
        
        for user in deletable_users:
            display_name = f"{user['name']} ({user['role']})"
            user_options.append(display_name)
            self.user_map[display_name] = user
        
        if user_options:
            self.delete_optmenu.configure(values=user_options)
            self.delete_user_var.set(user_options[0])
    
    def _delete_own_account(self):
        """Open a top-level dialog to delete own account with password confirmation"""
        # Check if admin - must have at least 1 admin remaining
        if self.role == "ADMIN":
            admin_count = get_admin_count()
            if admin_count <= 1:
                messagebox.showerror("Cannot Delete", "Cannot delete your account. At least 1 admin must remain in the system.")
                return
        
        # Create top-level dialog
        delete_dialog = ctk.CTkToplevel(self)
        delete_dialog.title("Delete Account - Password Confirmation")
        delete_dialog.geometry("450x300")
        delete_dialog.resizable(False, False)
        delete_dialog.grab_set()
        
        current_name = self.current_user.get("name", "") if self.current_user else ""
        
        # Title
        ctk.CTkLabel(
            delete_dialog,
            text="Delete Your Account",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#dc2626"
        ).pack(pady=15)
        
        # Warning message
        ctk.CTkLabel(
            delete_dialog,
            text=f"You are about to delete your account: {current_name}",
            font=ctk.CTkFont(size=12),
            text_color="#FFEE07"
        ).pack(pady=10)
        
        # Password label and entry
        ctk.CTkLabel(
            delete_dialog,
            text="Enter your password to confirm:",
            font=ctk.CTkFont(size=11)
        ).pack(pady=(20, 5))
        
        password_entry = ctk.CTkEntry(
            delete_dialog,
            show="*",
            placeholder_text="Enter your password",
            width=300
        )
        password_entry.pack(pady=10)
        
        # Button frame
        btn_frame = ctk.CTkFrame(delete_dialog, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        def verify_and_delete():
            password = password_entry.get()
            
            if not password:
                messagebox.showerror("Error", "Please enter your password")
                return
            
            current_username = self.current_user.get("username", "") if self.current_user else ""
            
            # Verify password
            if not verify_password(current_username, password):
                messagebox.showerror("Error", "Incorrect password. Please try again.")
                password_entry.delete(0, "end")
                return
            
            # Show final confirmation
            delete_dialog.destroy()
            
            confirm_popup = ctk.CTkToplevel(self)
            confirm_popup.title("Confirm Deletion")
            confirm_popup.geometry("450x200")
            confirm_popup.resizable(False, False)
            confirm_popup.grab_set()
            
            ctk.CTkLabel(
                confirm_popup,
                text="Are you sure?",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color="#dc2626"
            ).pack(pady=20)
            
            ctk.CTkLabel(
                confirm_popup,
                text=f"Your account '{current_name}' will be permanently deleted.\nThis action cannot be undone.",
                font=ctk.CTkFont(size=12),
                text_color="#FFEE07",
                justify="center"
            ).pack(pady=15)
            
            btn_frame2 = ctk.CTkFrame(confirm_popup, fg_color="transparent")
            btn_frame2.pack(pady=20)
            
            ctk.CTkButton(
                btn_frame2,
                text="Yes, Delete Permanently",
                fg_color="#dc2626",
                hover_color="#a41e2f",
                command=lambda: self._confirm_delete_own(confirm_popup),
                width=140
            ).pack(side="left", padx=10)
            
            ctk.CTkButton(
                btn_frame2,
                text="Cancel",
                command=confirm_popup.destroy,
                width=140
            ).pack(side="left", padx=10)
        
        # Delete button
        ctk.CTkButton(
            btn_frame,
            text="Verify & Delete",
            fg_color="#dc2626",
            hover_color="#a41e2f",
            command=verify_and_delete,
            width=140
        ).pack(side="left", padx=10)
        
        # Cancel button
        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=delete_dialog.destroy,
            width=140
        ).pack(side="left", padx=10)
    
    def _confirm_delete_own(self, popup):
        """Permanently delete the own account after password confirmation"""
        current_username = self.current_user.get("username", "") if self.current_user else ""
        
        try:
            result = delete_user_by_username(current_username)
            if result:
                popup.destroy()
                messagebox.showinfo("Account Deleted", "Your account has been permanently deleted.")
                # Redirect to login window
                self._logout_and_show_login()
            else:
                messagebox.showerror("Error", "Cannot delete your account")
        except Exception as e:
            messagebox.showerror("Error", f"Error: {str(e)}")
    
    def _logout_and_show_login(self):
        # Get the main app window
        main_window = self.winfo_toplevel()
        
        # Clear all widgets
        for widget in main_window.winfo_children():
            widget.destroy()
        
        # Reinitialize the login window
        from views.login import CTKLoginWindow
        main_window.title("Petron Gasul Login")
        login_window = CTKLoginWindow(main_window, on_success=main_window.on_login_success)
        login_window.pack(fill="both", expand=True)
    
    def _setup_cashier_tabs(self):
        # ========== CHANGE USERNAME TAB ==========
        self.username_tab = self.tabview.add("📝 Change Username")
        self._setup_change_username_tab()
        
        # ========== CHANGE PASSWORD TAB ==========
        self.password_tab = self.tabview.add("🔑 Change Password")
        self._setup_change_password_tab()
    
    def _setup_change_username_tab(self):
        frame = ctk.CTkFrame(self.username_tab)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            frame,
            text="Change My Username",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=20)
        
        # Current username (display only)
        current_username = self.current_user.get("username", "") if self.current_user else ""
        ctk.CTkLabel(frame, text=f"Current: {current_username}").pack(pady=5)
        
        # New username entry
        self.new_username_entry = ctk.CTkEntry(frame, placeholder_text="Enter new username", width=300)
        self.new_username_entry.pack(pady=10)
        
        # Change button
        change_btn = ctk.CTkButton(
            frame,
            text="✅ Update Username",
            command=self._change_username,
            width=200
        )
        change_btn.pack(pady=10)
    
    def _setup_change_password_tab(self):
        frame = ctk.CTkFrame(self.password_tab)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            frame,
            text="Change My Password",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=20)
        
        # Current password
        ctk.CTkLabel(frame, text="Current Password:").pack(pady=5)
        self.current_password_entry = ctk.CTkEntry(frame, show="*", placeholder_text="Enter current password", width=300)
        self.current_password_entry.pack(pady=5)
        
        # New password
        ctk.CTkLabel(frame, text="New Password:").pack(pady=5)
        self.new_password_entry = ctk.CTkEntry(frame, show="*", placeholder_text="Enter new password", width=300)
        self.new_password_entry.pack(pady=5)
        
        # Confirm new password
        ctk.CTkLabel(frame, text="Confirm New Password:").pack(pady=5)
        self.confirm_password_entry = ctk.CTkEntry(frame, show="*", placeholder_text="Confirm new password", width=300)
        self.confirm_password_entry.pack(pady=5)
        
        # Change button
        change_btn = ctk.CTkButton(
            frame,
            text="✅ Update Password",
            command=self._change_password,
            width=200
        )
        change_btn.pack(pady=10)
    
    def _load_accounts(self):
        # Clear existing widgets in scroll frame
        for widget in self.accounts_scroll.winfo_children():
            widget.destroy()
        
        try:
            users = get_all_users()
            
            # Header
            header_frame = ctk.CTkFrame(self.accounts_scroll, fg_color="transparent")
            header_frame.pack(fill="x", pady=5)
            
            ctk.CTkLabel(header_frame, text="ID", width=50, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
            ctk.CTkLabel(header_frame, text="Role", width=80, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
            ctk.CTkLabel(header_frame, text="Name", width=150, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
            ctk.CTkLabel(header_frame, text="Username", width=120, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
            ctk.CTkLabel(header_frame, text="Password", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
            
            # Separator
            ctk.CTkFrame(self.accounts_scroll, height=2, fg_color="#37E9FD").pack(fill="x", pady=5)
            
            # User rows
            for user in users:
                row_frame = ctk.CTkFrame(self.accounts_scroll, fg_color="transparent")
                row_frame.pack(fill="x", pady=2)
                
                pwd_hash = user["password_hash"]
                
                ctk.CTkLabel(row_frame, text=str(user["user_id"]), width=50).pack(side="left", padx=5)
                ctk.CTkLabel(row_frame, text=user["role"], width=80).pack(side="left", padx=5)
                ctk.CTkLabel(row_frame, text=user["name"], width=150).pack(side="left", padx=5)
                ctk.CTkLabel(row_frame, text=user["username"], width=120).pack(side="left", padx=5)
                ctk.CTkLabel(row_frame, text=pwd_hash, font=ctk.CTkFont(size=10)).pack(side="left", padx=5)
        
        except Exception as e:
            ctk.CTkLabel(self.accounts_scroll, text=f"Error loading accounts: {str(e)}", text_color="red").pack()
    
    def _change_username(self):
        new_username = self.new_username_entry.get().strip()
        
        if not new_username:
            messagebox.showerror("Error", "Please enter a new username")
            return
        
        if len(new_username) < 3:
            messagebox.showerror("Error", "Username must be at least 3 characters")
            return
        
        current_username = self.current_user.get("username", "") if self.current_user else ""
        
        try:
            result = update_username(current_username, new_username)
            if result:
                messagebox.showinfo("Success", "Username updated successfully! Please re-login.")
                self.new_username_entry.delete(0, "end")
                # Update current user session
                self.current_user["username"] = new_username
            else:
                messagebox.showerror("Error", "Failed to update username")
        except Exception as e:
            messagebox.showerror("Error", f"Error: {str(e)}")
    
    def _change_password(self):
        current_password = self.current_password_entry.get()
        new_password = self.new_password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        
        # Validation
        if not current_password or not new_password or not confirm_password:
            messagebox.showerror("Error", "Please fill all fields")
            return
        
        if new_password != confirm_password:
            messagebox.showerror("Error", "New passwords do not match")
            return
        
        if len(new_password) < 4:
            messagebox.showerror("Error", "Password must be at least 4 characters")
            return
        
        # Verify current password
        current_username = self.current_user.get("username", "") if self.current_user else ""
        current_hash = self._hash_password(current_password)
        new_hash = self._hash_password(new_password)
        
        # Check if current password is correct
        from database import get_connection
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT user_id FROM users WHERE username = %s AND password_hash = %s", (current_username, current_hash))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not result:
            messagebox.showerror("Error", "Current password is incorrect")
            return
        
        # Update password
        try:
            result = update_password(current_username, new_hash)
            if result:
                messagebox.showinfo("Success", "Password updated successfully!")
                self.current_password_entry.delete(0, "end")
                self.new_password_entry.delete(0, "end")
                self.confirm_password_entry.delete(0, "end")
            else:
                messagebox.showerror("Error", "Failed to update password")
        except Exception as e:
            messagebox.showerror("Error", f"Error: {str(e)}")