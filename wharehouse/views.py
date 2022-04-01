from rest_framework.views import APIView

from .serializers import OrderSerializer
from rest_framework.response import Response
from django.db.models import Count, Sum, FloatField, Q, OuterRef, Subquery
from django.db.models.functions import Coalesce
from .models import *


class OrderStatsView(APIView):
    serializer_class = OrderSerializer

    def post(self, request, *args, **kwargs):
        serializer = OrderSerializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)

        results = []
        party_material_given_data = {}
        for block in serializer.validated_data:
            product: Product = block['product']
            quantity = block['quantity']

            material_infos = product.product_material.values('material_id', 'material__name', 'value')

            for material_info in material_infos:
                material_id = material_info['material_id']
                material_name = material_info['material__name']
                value = material_info['value']
                total_value = value * quantity
                print('---')
                print(material_name)
                print(material_info['material_id'])
                print('---')

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
                    print(party)
                    print(total_value)
                    print(party['values'])
                    if given_value + party['values'] >= total_value:
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
                        given_value += party['values']
                        given_value_data.append(
                            {'party': party['id'], 'qty': party['values']}
                        )

                        try:
                            party_material_given_data[party['id']][material_id] += party['values']
                        except KeyError:
                            party_material_given_data[party['id']] = {}
                            party_material_given_data[party['id']][material_id] = party['values']

                if given_value < total_value:
                    given_value_data.append(
                        {'party': None, 'qty': total_value - given_value}
                    )

                for each in given_value_data:
                    results.append(
                        {
                            "party": each['party'],
                            "material": material_name,
                            "qty": each['qty'],
                        }
                    )
        print(party_material_given_data)

        return Response(data=results)
