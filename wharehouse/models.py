from django.db import models
from django.utils.translation import gettext_lazy as _


class Product(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=100, unique=True)
    materials = models.ManyToManyField('wharehouse.Material', through='wharehouse.ProductMaterial')

    def __str__(self):
        return f'{self.name} | {self.code}'

    class Meta:
        ordering = ('name',)


class ProductMaterial(models.Model):
    product = models.ForeignKey('wharehouse.Product', on_delete=models.CASCADE, related_name='product_material')
    material = models.ForeignKey('wharehouse.Material', on_delete=models.CASCADE, related_name='product_material')
    value = models.FloatField()

    def __str__(self):
        return f"{self.product} - {self.material}"

    class Meta:
        ordering = ('product__name', 'material__name',)
        unique_together = ('product', 'material')


class Material(models.Model):
    KG = 1
    METR = 2
    METR2 = 3
    COUNT = 4
    MEASURE_TYPES = (
        (KG, _("Kilogram")),
        (METR, _("Metr")),
        (METR2, _("Metr kvadrat")),
        (COUNT, _("Soni"))
    )
    measure_type = models.IntegerField(choices=MEASURE_TYPES)
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)


class PartyMaterial(models.Model):
    party = models.ForeignKey('wharehouse.Party', on_delete=models.CASCADE, related_name='party_material')
    material = models.ForeignKey(Material, on_delete=models.SET_NULL, null=True, related_name='party_material')
    value = models.FloatField()

    class Meta:
        ordering = ('material__name',)


class Party(models.Model):
    arrived_at = models.DateTimeField()
    warehouse = models.ForeignKey('wharehouse.WareHouse', on_delete=models.SET_NULL, related_name='party', null=True)

    def __str__(self):
        return str(self.arrived_at)

    class Meta:
        ordering = ('-arrived_at',)


class WareHouse(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)
