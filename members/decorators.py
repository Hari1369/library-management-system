from django.shortcuts import redirect
from django.contrib import messages

def role_required(allowed_roles):
    def decorator(view):
        def check_role(request):
            role = request.session.get("role")
            if role in allowed_roles:
                return view(request)
            messages.error(request, "Access Denied")
            return redirect("dashboard_page")
        return check_role
    return decorator