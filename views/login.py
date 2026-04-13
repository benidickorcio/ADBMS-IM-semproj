import customtkinter as ctk
from utils.auth import login, set_current_user

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")


class CTKLoginWindow(ctk.CTkFrame):
    def __init__(self, parent, on_success=None):
        super().__init__(parent)
        self.parent = parent
        self.on_success = on_success

        parent.title("Login | Petron Gasul")
        parent.geometry("1100x700")
        parent.resizable(True, True)

        self.fullscreen = False
        parent.bind("<F11>", self.toggle_fullscreen)
        parent.bind("<Escape>", self.exit_fullscreen)

        self.header = ctk.CTkLabel(self, text="Petron LPG Refilling Station", font=ctk.CTkFont(size=28, weight="bold"))
        self.header.pack(pady=(200, 8))

        self.subtitle = ctk.CTkLabel(self, text="Sign in to continue to your workstation", font=ctk.CTkFont(size=14), text_color="#94a3b8")
        self.subtitle.pack(pady=(0, 20))

        self.username_entry = ctk.CTkEntry(self, placeholder_text="Username", width=380, height=42, corner_radius=10)
        self.username_entry.pack(pady=(6, 10))

        self.password_entry = ctk.CTkEntry(self, placeholder_text="Password", width=380, height=42, corner_radius=10, show="*")
        self.password_entry.pack(pady=(6, 18))

        self.signin_btn = ctk.CTkButton(self, text="Sign In", width=380, height=42, corner_radius=10, fg_color="#2563eb", hover_color="#1d4ed8", command=self.sign_in)
        self.signin_btn.pack(pady=(6, 12))

        self.status_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12, weight="bold"))
        self.status_label.pack(pady=(8, 0))

    def sign_in(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            self.status_label.configure(text="Enter both username and password", text_color="#f87171")
            return

        user = login(username, password)
        if not user:
            self.status_label.configure(text="Invalid credentials", text_color="#f87171")
            return

        set_current_user(user)
        self.status_label.configure(text=f"Successfully signed in as {user['username']}", text_color="#34d399")

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


