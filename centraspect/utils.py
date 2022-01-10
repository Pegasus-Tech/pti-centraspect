from django.core.serializers import serialize
from django.utils.text import slugify
from django.core.files.uploadedfile import InMemoryUploadedFile
from io import BytesIO
import qrcode

def generate_qr_code_image(account, instance_uuid, serialized_data):
    qr = qrcode.QRCode(version=1,box_size=10,border=5)
        
    qr.add_data(serialized_data)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')

    buffer = BytesIO()
    img.save(buffer)
    
    filename = _build_bucket_path(account, instance_uuid)
    filebuffer = InMemoryUploadedFile(buffer, None, filename, 'image/png', buffer.getbuffer().nbytes, None)
    
    return filebuffer
 
def _build_bucket_path(account, instance_uuid):
    return f'{slugify(account.name)}-{account.uuid}/codes/item-{instance_uuid}.png'
