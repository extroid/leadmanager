from django.contrib import admin
from models import LeadConsumer
from forms import LeadConsumerForm

class LeadConsumerAdmin(admin.ModelAdmin):
    form = LeadConsumerForm

admin.site.register(LeadConsumer, LeadConsumerAdmin)
