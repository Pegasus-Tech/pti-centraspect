from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import InspectionFormSerializer
from authentication.models import User
from centraspect.utils import S3UploadType, S3UploadUtils
from inspection_forms.models import InspectionForm
from inspection_items import service as inspection_item_service
from inspection_items.models import InspectionItem
from inspections.mixins import LogInspectionMixin
from inspections.models import InspectionImage


@csrf_exempt
def get_form_from_item(request, uuid):
    print(f'got request for uuid: {uuid}')
    if request.method == 'GET':
        item = InspectionForm.objects.get(uuid=uuid)
        serialized = InspectionFormSerializer(item, many=False)
        return JsonResponse(serialized.data, safe=False)


@csrf_exempt
def attach_photos_to_inspection(request, uuid):
    inspection = inspection_item_service.get_inspection_by_uuid(uuid)
    counter = 0
    if inspection is not None:
        has_images = request.FILES.get('images') is not None
        if has_images:
            images = request.FILES.pop('images')
            for img in images:
                try:
                    image = S3UploadUtils.upload_image(inspection.account,
                                                       inspection.uuid,
                                                       S3UploadType.INSPECTION_IMAGE,
                                                       img)

                    inspection_image = InspectionImage()
                    inspection_image.inspection = inspection
                    inspection_image.image = image
                    inspection_image.save()
                    counter += 1
                except Exception as e:
                    return JsonResponse(status=400, data={"Error": str(e)})

            return JsonResponse(status=200, data={"Success": f"{counter} image(s) uploaded"})
        return JsonResponse(status=422,
                            data={"Message": "No Images Uploaded. Make sure the request files are set to key 'images'"})
    else:
        return JsonResponse(status=400, data={"Error", f"Inspection {uuid} not found."})


class FormItemAPIView(LogInspectionMixin, APIView):

    def get(self, request, uuid):
        print(f'looking for form :: {uuid}')
        item = InspectionItem.objects.get(uuid=uuid)
        serialized = {
            "inspection_item_title": item.title,
            "inspection_item_uuid": item.uuid,
            "inspection_item_owner": item.assigned_to.get_full_name if item.assigned_to is not None else None,
            "inspection_item_owner_uuid": item.assigned_to.uuid if item.assigned_to is not None else None,
            "inspection_form_title": item.form.title if item.form is not None else None,
            "inspection_form_uuid": item.form.uuid if item.form is not None else None,
            "inspection_form": item.form.form_json if item.form is not None else None
        }
        return Response(serialized)

    def post(self, request, uuid):
        print(f"Getting reqeust :: {self.request.data['inspection_form_filled']} for form uuid {uuid}")
        data = self.request.data
        item = InspectionItem.objects.get(uuid=uuid)
        disposition = None

        # TODO - update User to be the authed user from the mobile app
        user = User.objects.filter(account__user__is_superuser=True).first()
        try:
            disposition = data['disposition']
        except KeyError:
            print(f'No disposition attached to request')
            return JsonResponse(data={"Error": "No disposition attached to request"}, status=400)
        finally:
            inspection = self.log_inspection(inspection_item=item,
                                             logged_by=user,
                                             completed_form=data['inspection_form_filled'],
                                             inspection_disposition=disposition or 'pass')
            if inspection.get('success'):
                inspection_log = inspection.get('inspection')
                item = self.update_inspection_item_due_dates(inspection=inspection.get('inspection'))
                resp = {'url': f'/dashboard/inspection-items/{item.uuid}', "inspection_log": inspection_log.to_json()}
                return JsonResponse(resp, status=201)
            else:
                print(f"FAILURE :: {inspection.get('inspection')}")
                resp = {'url': f'/dashboard/inspections/new/{item.uuid}'}
                return JsonResponse(resp, status=500)
