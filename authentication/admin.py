from django.contrib import admin
from .models import User, Account, Address

# Register your models here.
admin.site.register(User)
admin.site.register(Account)
admin.site.register(Address)
