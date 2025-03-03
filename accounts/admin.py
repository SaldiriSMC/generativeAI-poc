from django.contrib import admin

from .models import User, UserAICreds,UserDocument

# Register your models here.

admin.site.register(UserDocument)
admin.site.register(User)
admin.site.register(UserAICreds)
