import json


def serialize_inspection_item(instance):
    return json.dumps(
        {
            "uuid": instance.uuid.__str__(), 
            "date_created": instance.date_created.__str__(),
            "serial_number": instance.serial_number, 
            "model_number": instance.model_number,
            "expiration_date": instance.expiration_date.__str__(),
            "form_uuid": instance.form.uuid.__str__() if instance.form is not None else None, 
            "assigned_to_id": instance.assigned_to.pk if instance.assigned_to is not None else None, 
            "account_uuid": instance.account.uuid.__str__()
        }
    )