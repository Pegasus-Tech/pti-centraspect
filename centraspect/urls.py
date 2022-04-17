"""centraspect URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.conf.urls import include
from django.contrib import admin
from django.urls import path, re_path
from authentication.views import registration_view, login_view, logout_view, forgot_password_view
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView, PasswordResetCompleteView
from authentication.api_view import get_auth_token
from dashboard.views import DashboardView
from .views import LandingPage
from rest_framework import permissions
# from drf_yasg.views import get_schema_view
# from drf_yasg import openapi

# schema_view = get_schema_view(
#     openapi.Info(
#         title="Centraspect API",
#         default_version='v1',
#         description="Centraspect API endpoint documentation",
#     ),
#     public=True,
#     permission_classes=(permissions.AllowAny,))

urlpatterns = [
    path('', LandingPage.as_view(), name="landing_page"),
    path('centra/admin/', admin.site.urls),
    path('register/', registration_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('forgot_password/', forgot_password_view, name='forgot_password'),
    path('reset/<uidb64>/<token>', PasswordResetConfirmView.as_view(), name='reset_password_confirm'),
    path('reset/done', PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('api/auth/', include('authentication.urls', namespace='api_auth')),
    
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('dashboard/users/', include('authentication.urls', namespace="users")),
    path('dashboard/inspection-items/', include('inspection_items.urls', namespace="inspection_items")),
    path('dashboard/inspection-calendar', include('inspection_calendar.urls', namespace="inspection_calendar")),
    path('dashboard/form-builder', include('inspection_forms.urls', namespace="inspection_forms")),
    path('dashboard/inspections', include('inspections.urls', namespace='inspections')),
    
    # path('api/docs', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/', include('api_backend.urls', namespace='api'))
]
