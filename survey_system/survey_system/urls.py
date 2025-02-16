"""
URL configuration for survey_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView
from inventory import views
from django.conf import settings
from django.conf.urls.static import static
from inventory.views import request_equipment

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.request_equipment, name='/'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('create-user/', views.create_user, name='create_user'),
    path('inventory/', include('inventory.urls')),
    path('api/equipment/in-store/', views.equipment_in_store, name='equipment_in_store'),
    path('api/equipment/in-field/', views.equipment_in_field, name='equipment_in_field'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
