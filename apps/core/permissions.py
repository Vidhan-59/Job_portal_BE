from rest_framework import permissions

class IsStudentOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.role == 'student'

class IsHROrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.role in ['recruiting_hr', 'hr_team_member', 'main_hr']

class IsRecruitingHR(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role in ['recruiting_hr', 'main_hr']