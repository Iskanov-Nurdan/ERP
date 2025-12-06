from django.contrib import admin
from .models import RawMaterial, RawMaterialMovement, FinishedProduct
# Register your models here.
admin.site.register(RawMaterial)
admin.site.register(RawMaterialMovement)
admin.site.register(FinishedProduct)