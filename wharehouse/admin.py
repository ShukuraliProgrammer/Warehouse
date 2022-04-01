from django.contrib import admin
from .models import *


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')


@admin.register(ProductMaterial)
class ProductMaterial(admin.ModelAdmin):
    list_display = ('product', 'material', 'value')
    filter = ('product', 'material')
    search_fields = ("product__name", "product__code")
    autocomplete_fields = ('product', 'material')


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'measure_type')
    filter = ('measure_type',)
    search_fields = ('name',)


@admin.register(PartyMaterial)
class PartyMaterialAdmin(admin.ModelAdmin):
    list_display = ('material', 'party', 'value')
    autocomplete_fields = ('material', 'party')
    filter = ('warehouse',)
    search_fields = ('material__name',)


@admin.register(Party)
class PartyAdmin(admin.ModelAdmin):
    list_display = ('arrived_at', 'warehouse')
    filter = ('arrived_at',)

    search_fields = ('warehouse__party__party_material__material__name',)
    autocomplete_fields = ('warehouse',)


@admin.register(WareHouse)
class WareHouseAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
