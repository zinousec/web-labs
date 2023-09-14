from flask_login import current_user

class UsersPolicy:
    def __init__(self, record):
        self.record = record
    
    def assign_role(self):
        return current_user.is_admin()

    def show(self):
        #return True
        if current_user.is_admin():
            return True
        
        if str(current_user.id) == str(self.record.id):
            return True
            
        return False

    def delete(self):
        return current_user.is_admin()

    def create(self):
        return current_user.is_admin()

    def edit(self):
        if current_user.is_admin():
            return True
        
        if str(current_user.id) == str(self.record.id):
            return True
            
        return False
    
    def show_stat(self):
        return current_user.is_admin()