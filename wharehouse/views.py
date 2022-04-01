from rest_framework.views import APIView
from .serializers import OrderSerializer
from rest_framework.response import Response
from django.db.models import Sum, FloatField, Q
from django.db.models.functions import Coalesce
from .models import *


class OrderStatsView(APIView):
    serializer_class = OrderSerializer

    def get(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)

        results = {}
        """
        results = {
            "Product name" : [
                {
                    "party": 1,
                    "material": "material name 1",
                    "qty": 20.0
                },
                {
                    "party": 2,
                    "material": "material name 2",
                    "qty": 5.0
                },
                {
                    "party": None,
                    "material": "material name 2",
                    "qty": 30.0
                },
            ]
        """

        party_material_given_data = {}
        """
            {
                |party_id|: {
                    |material_id|: |material_given_value|
                }, 
                2: {
                    4: 90.0
                }, 
                3: {
                    4: 20.0
                }
            }
        """

        for block in serializer.validated_data:
            product: Product = block['product']
            quantity = block['quantity']

            results[product.name] = []

            product_materials = product.product_material.values('material_id', 'material__name', 'value')

            for product_material in product_materials:
                material_id = product_material['material_id']
                material_name = product_material['material__name']
                value = product_material['value']
                total_value = value * quantity

                given_value = 0
                given_value_data = []

                parties = Party.objects.annotate(
                    values=Coalesce(
                        Sum(
                            'party_material__value',
                            filter=Q(
                                party_material__material_id=material_id
                            ),
                            output_field=FloatField()
                        ),
                        0.0
                    )
                ).filter(values__gt=0).order_by('-values').values('id', 'values')

                for party in parties:
                    try:
                        party_values = party['values'] - party_material_given_data[party['id']][material_id]
                    except KeyError:
                        party_values = party['values']

                    if party_values == 0:
                        break

                    if given_value + party_values >= total_value:
                        given_value_data.append(
                            {'party': party['id'], 'qty': total_value - given_value}
                        )

                        try:
                            party_material_given_data[party['id']][material_id] += total_value - given_value
                        except KeyError:
                            party_material_given_data[party['id']] = {}
                            party_material_given_data[party['id']][material_id] = total_value - given_value

                        given_value = total_value
                        break
                    else:
                        given_value += party_values
                        given_value_data.append(
                            {'party': party['id'], 'qty': party_values}
                        )

                        try:
                            party_material_given_data[party['id']][material_id] += party_values
                        except KeyError:
                            party_material_given_data[party['id']] = {}
                            party_material_given_data[party['id']][material_id] = party_values

                if given_value < total_value:
                    given_value_data.append(
                        {'party': None, 'qty': total_value - given_value}
                    )

                for each in given_value_data:
                    results[product.name].append(
                        {
                            "party": each['party'],
                            "material": material_name,
                            "qty": each['qty'],
                        }
                    )

        return Response(data=results)
