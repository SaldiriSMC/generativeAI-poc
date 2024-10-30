"""
URL configuration for generativeAI-poc project.

The `urlpatterns` list routes URLs to views.py. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views.py
    1. Add an import:  from my_app import views.py
    2. Add a URL to urlpatterns:  path('', views.py.home, name='home')
Class-based views.py
    1. Add an import:  from other_app.views.py import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from .views import gen_ai_chat

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', gen_ai_chat, name='gen_ai_chat'),
    path('accounts/', include('accounts.urls')),
]

# Development-only static and media URLs
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
