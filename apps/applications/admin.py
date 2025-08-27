from django.contrib import admin


from .models import Application, ApplicationHistory

# Register your models here.
admin.site.register(Application)
admin.site.register(ApplicationHistory)
