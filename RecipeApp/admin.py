from django.contrib import admin
from .models import Recipe

# register the Recipe model in admin site, to perform CRUD operations through the admin panel
admin.site.register(Recipe)
