from rest_framework import permissions

class IsSalesPersonOrAdmin(permissions.BasePermission):
    """
    Custom permission to allow only salespersons or admin users to access the view.
    """

    def has_permission(self, request, view):
        
        if request.user and request.user.is_staff:
            return True

       
        return request.user.groups.filter(name="Salesperson").exists()
