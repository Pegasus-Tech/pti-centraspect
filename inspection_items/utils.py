import json


def serialize_inspection_item(instance):
    return json.dumps(
        {
            "uuid": str(instance.uuid),
            "form_uuid": str(instance.form.uuid) if instance.form is not None else None
        }
    )


def serialize_inspection_sub_item(instance):
    return json.dumps(
        {
            "uuid": str(instance.uuid),
            "kit_uuid": str(instance.kit.uuid)
        }
    )
