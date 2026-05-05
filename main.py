from views.app import CTKMainApp
from database import initialize_db

if __name__ == "__main__":
    try:
        initialize_db()
        app = CTKMainApp()
        app.mainloop()
    except Exception:
        print(f"\n\nStart the xampp first and make sure the database is properly set up\n\n")