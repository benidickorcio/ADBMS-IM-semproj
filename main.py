from views.app import CTKMainApp
from database import initialize_db

if __name__ == "__main__":
    initialize_db()
    app = CTKMainApp()
    app.mainloop()                                  