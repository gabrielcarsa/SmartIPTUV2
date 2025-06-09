from django.contrib import admin

from debits.models import Block, Enterprise, Lot

# Register your models here.
admin.site.register(Enterprise)
admin.site.register(Block)
admin.site.register(Lot)


