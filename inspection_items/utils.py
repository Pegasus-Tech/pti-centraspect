import json


def serialize_inspection_item(instance):
    return json.dumps({
        "qr_code": 
            {
                "inpection_equipment_uuid": instance.uuid.__str__(), 
                "date_created": instance.date_created.__str__(), 
                "last_updated": instance.last_updated.__str__(), 
                "title": instance.title, 
                "description": instance.description, 
                "inspection_interval": instance.inspection_interval, 
                "inspection_type": instance.inspection_type, 
                "serial_number": instance.serial_number, 
                "model_number": instance.model_number, 
                "first_inspection_date": instance.first_inspection_date.__str__(), 
                "last_inspection_date": instance.last_inspection_date.__str__(), 
                "next_inspection_date": instance.next_inspection_date.__str__(), 
                "expiration_date": instance.expiration_date.__str__(), 
                "is_active": instance.is_active, 
                "form_uuid": instance.form.uuid.__str__() if instance.form is not None else None, 
                "assigned_to_id": instance.assigned_to.pk if instance.assigned_to is not None else None, 
                "account_uuid": instance.account.uuid.__str__()
            }
        }
    )