def is_admin(request):
    return {'is_admin': request.user.is_authenticated and request.user.is_superuser}
