from django.contrib import admin, auth
from django.urls import path, include
from compiler.views import register
from .views import profile
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include(("django.contrib.auth.urls", "auth"), namespace="accounts")),
    path('accounts/password_reset/done/', auth.views.PasswordResetDoneView.as_view(), name="password_reset_done",),
    path('accounts/reset/done', auth.views.PasswordResetCompleteView.as_view(), name="password_reset_complete",),
    path('accounts/profile/', profile , name='profile'),
    path('register/', register, name='register'),
    path('', TemplateView.as_view(template_name="index.html")),
    path('', include("compiler.urls"))
]
