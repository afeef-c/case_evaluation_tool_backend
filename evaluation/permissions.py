from rest_framework.permissions import BasePermission

class IsAgencyAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_superuser

class IsCompanyAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_staff

class IsCompanyAdminOrStaff(BasePermission):
    """
    Custom permission to allow access only to Company Admins or Staff.
    """

    def has_permission(self, request, view):
        user = request.user

        # Ensure the user is authenticated
        if not user or not user.is_authenticated:
            return False

        # Check if the user is a Company Admin (i.e., linked as an admin in the Company model)
        if hasattr(user, 'company') and user.company.admin == user:
            return True

        # Check if the user is a Company Staff
        if hasattr(user, 'staff_profile'):
            return True

        return False