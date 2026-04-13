# point of sale screen
from utils.auth import is_admin, is_cashier


class dashboard:
    def can_access(self):
        return is_admin() or is_cashier()

    def is_admin_view(self):
        return is_admin()

    def is_cashier_view(self):
        return is_cashier()

    def load_summary(self):
        if not self.can_access():
            raise PermissionError("Login required")

        if is_admin():
            return "Load admin dashboard summary (sales, inventory, users, reports)"
        return "Load cashier dashboard summary (POS, customers, quick sales)"
