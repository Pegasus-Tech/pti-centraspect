import json


def serialize_inspection_item(instance):
    return json.dumps(
        {
            "uuid": instance.uuid.__str__(),
            "form_uuid": instance.form.uuid.__str__() if instance.form is not None else None
        }
    )
