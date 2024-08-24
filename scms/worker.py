import os

from django.core.files.base import ContentFile
from django_rq import job
from mysql import connector

from main.models import ScmsComplaint


@job
def process_image(complaint_id):
    from scms import process_image_script

    complaint = ScmsComplaint.objects.get(id=complaint_id)
    file_path = complaint.c_in_image.name
    output = process_image_script.process_image(f"media/{file_path}")
    name = os.path.basename(file_path)
    name, ext = os.path.splitext(name)
    complaint.c_out_image = ContentFile(output, name=f'{name}_out{ext}')
    complaint.save()
