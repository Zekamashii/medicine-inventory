from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', include('inventory.urls')),
]

handler400 = 'inventory.views.handler400'
handler403 = 'inventory.views.handler403'
handler404 = 'inventory.views.handler404'
handler500 = 'inventory.views.handler500'
