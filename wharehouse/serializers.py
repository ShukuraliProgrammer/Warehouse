from rest_framework import serializers
from .models import Product
from django.utils.translation import gettext_lazy as _


def validate_positive(val):
    if val >0:
        return val
    else:
        raise serializers.ValidationError(_("Positive number is required"))


class OrderSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    quantity = serializers.IntegerField(validators=[validate_positive])
