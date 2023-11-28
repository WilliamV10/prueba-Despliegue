from rolepermissions.roles import AbstractUserRole

class Admin(AbstractUserRole):
    available_permissions = {
        'can_view_admin_page': True,
        'create_user': True,
        'delete_user': True,
        'edit_user': True,
        
    }

class Estudiante(AbstractUserRole):
    available_permissions = {
        'create_user': False,
        'delete_user': False,
        'can_view_user_page': True,
    }