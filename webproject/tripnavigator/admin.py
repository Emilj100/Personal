from django.contrib import admin

from .models import User, TravelPlan, Document, Expense, Activity

# Register your models here.
admin.site.register(User)
admin.site.register(TravelPlan)
admin.site.register(Document)
admin.site.register(Expense)
admin.site.register(Activity)