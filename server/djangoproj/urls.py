# djangoproj/urls.py
"""djangoproj URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.views.generic import TemplateView
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('djangoapp/', include('djangoapp.urls')),
    # Serve React frontend build entry point for root and routes handled by React Router
    # Ensure this TemplateView serves your main index.html from the React build
    path('', TemplateView.as_view(template_name="index.html")),
    path('about/', TemplateView.as_view(template_name="index.html")), # Assume React handles routing
    path('contact/', TemplateView.as_view(template_name="index.html")), # Assume React handles routing
    path('login/', TemplateView.as_view(template_name="index.html")), # Assume React handles routing
    path('register/', TemplateView.as_view(template_name="index.html")), # Assume React handles routing
    path('dealers/', TemplateView.as_view(template_name="index.html")), # Assume React handles routing
    path(
        'dealer/<int:dealer_id>',
        TemplateView.as_view(template_name="index.html") # Assume React handles routing
    ),
    path(
        'postreview/<int:dealer_id>',
        TemplateView.as_view(template_name="index.html") # Assume React handles routing
    ),
]

# Serve static files during development ONLY if DEBUG is True
if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT
    )
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )

# Note: Serving static/media files this way is not suitable for production.
# In production, your web server (like Nginx or Apache) should handle this.