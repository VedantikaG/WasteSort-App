from django.db import models


# Create your models here.
class ScmsUser(models.Model):
    u_username = models.CharField(max_length=255, unique=True)
    u_password = models.TextField()

    is_admin = models.BooleanField(default=False)

    class Meta:
        db_table = "scms_user"


class ScmsComplaint(models.Model):
    u_id = models.ForeignKey(ScmsUser, on_delete=models.CASCADE)
    c_title = models.CharField(max_length=255)
    c_in_image = models.FileField(upload_to='images/')
    c_verified = models.CharField(max_length=1, default='n')
    c_resolved = models.CharField(max_length=1, default='n')
    c_lat = models.FloatField()
    c_long = models.FloatField()
    c_class = models.JSONField(default=list)
    c_out_image = models.FileField(upload_to='images/', null=True)
    c_datetime = models.DateTimeField(auto_now_add=True)

    verifier = models.ForeignKey(ScmsUser, on_delete=models.CASCADE, related_name='verified_complaints', null=True)
    resolver = models.ForeignKey(ScmsUser, on_delete=models.CASCADE, related_name='resolved_complaints', null=True)

    class Meta:
        db_table = "scms_complaint"
