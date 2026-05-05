import customtkinter as ctk
from utils.auth import login, set_current_user
from utils.colors import get_color

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")


class CTKLoginWindow(ctk.CTkFrame):
    def __init__(self, parent, on_success=None):
        super().__init__(parent)
        self.parent = parent
        self.on_success = on_success

        parent.title("Login | ERMITA LPG Refilling Station")
        parent.geometry("1100x700")
        parent.resizable(True, True)
        parent.configure(fg_color=get_color("bg_primary"))

        self.fullscreen = False
        parent.bind("<F11>", self.toggle_fullscreen)
        parent.bind("<Escape>", self.exit_fullscreen)

        self.header = ctk.CTkLabel(self, text="ERMITA LPG Refilling Station", font=ctk.CTkFont(size=28, weight="bold"), text_color=get_color("primary"))
        self.header.pack(pady=(200, 8))

        self.subtitle = ctk.CTkLabel(self, text="Sign in to continue to your workstation", font=ctk.CTkFont(size=14), text_color=get_color("text_secondary"))
        self.subtitle.pack(pady=(0, 20))

        self.username_entry = ctk.CTkEntry(self, placeholder_text="Username", width=380, height=42, corner_radius=10, fg_color=get_color("bg_secondary"), border_color=get_color("border"), text_color=get_color("text_primary"))
        self.username_entry.pack(pady=(6, 10))

        self.password_entry = ctk.CTkEntry(self, placeholder_text="Password", width=380, height=42, corner_radius=10, show="*", fg_color=get_color("bg_secondary"), border_color=get_color("border"), text_color=get_color("text_primary"))
        self.password_entry.pack(pady=(6, 18))

        self.signin_btn = ctk.CTkButton(self, text="Sign In", width=380, height=42, corner_radius=10, fg_color=get_color("button_primary"), hover_color=get_color("button_primary_dark"), command=self.sign_in, text_color=get_color("text_primary"))
        self.signin_btn.pack(pady=(6, 12))

        self.status_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12, weight="bold"))
        self.status_label.pack(pady=(8, 0))

    def sign_in(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            self.status_label.configure(text="Enter both username and password", text_color=get_color("status_error"))
            return

        user = login(username, password)
        if not user:
            self.status_label.configure(text="Invalid credentials", text_color=get_color("status_error"))
            return

        set_current_user(user)
        self.status_label.configure(text=f"Successfully signed in as {user['username']}", text_color=get_color("status_success"))

        if self.on_success:
            self.after(300, lambda: self.on_success(user))

    def toggle_fullscreen(self, event=None):
        self.fullscreen = not self.fullscreen
        self.parent.attributes("-fullscreen", self.fullscreen)

    def exit_fullscreen(self, event=None):
        self.fullscreen = False
        self.parent.attributes("-fullscreen", False)

    def close_window(self):
        self.parent.destroy()


