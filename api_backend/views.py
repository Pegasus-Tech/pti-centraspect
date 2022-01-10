from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from inspection_items.models import InspectionItem
from inspection_forms.models import InspectionForm
from .serializers import InspectionFormSerializer

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# Create your views here.
@csrf_exempt
def get_form_from_item(request, uuid):
    print(f'got request for uuid: {uuid}')
    if request.method == 'GET':
        
        item = InspectionForm.objects.get(uuid=uuid)
        serialized = InspectionFormSerializer(item, many=False)
        return JsonResponse(serialized.data, safe=False)

class FormItemAPIView(APIView):

    def get(self, request, uuid):
        print(f'looking for form :: {uuid}')
        item = InspectionItem.objects.get(uuid=uuid)
        serialized = {
            "inspection_item_title":item.title,
            "inspection_item_uuid":item.uuid,
            "inspection_item_owner":item.assigned_to.get_full_name() if item.assigned_to is not None else None,
            "inspection_item_owner_uuid":item.assigned_to.uuid if item.assigned_to is not None else None,
            "inspection_form_title":item.form.title,
            "inspection_form_uuid":item.form.uuid,
            "inspection_form":item.form.form_json
            }
        return Response(serialized)

    def post(self, request, uuid):
        pass