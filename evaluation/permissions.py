from rest_framework.permissions import BasePermission

class IsAgencyAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_superuser

class IsCompanyAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_staff

class IsCompanyAdminOrStaff(BasePermission):

    def has_permission(self, request, view):
        user = request.user
        # Check if the user is authenticated
        if user.companies.exists():  # Related name in ManyToManyField (Company.admins)
            return True

        # Check if the user is a Company Staff
        if hasattr(user, 'staff_profile'):
            return True
        # Allow if the user is a company admin or staff
        return False