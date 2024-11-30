from rest_framework.permissions import BasePermission


# rides/permissions.py

class IsAdminUser(BasePermission):
    """
    Allows access only to users with the 'admin' role.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            print("Permission denied: User not authenticated.")
            return False

        user_role = getattr(request.user, 'role', None)
        print(f"Authenticated user: {request.user.username}, Role: {user_role}")

        if user_role == 'admin':
            return True

        print("Permission denied: User is not an admin.")
        return False




