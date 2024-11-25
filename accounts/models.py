from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.

class User(AbstractUser):
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.username


class BaseTimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        get_latest_by = 'created_at'
        ordering = ['-created_at']


class UserAICreds(BaseTimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_creds', blank=False, null=False)
    name_keys_object = models.CharField(max_length=120, blank=False, null=False)
    pinecone_api_key = models.CharField(max_length=255, blank=True, null=True)
    pinecone_index_name = models.CharField(max_length=255, blank=True, null=True)
    groq_api_key = models.CharField(max_length=255, blank=True, null=True)
    extra_data = models.JSONField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if self.is_active:
            UserAICreds.objects.filter(user=self.user).update(is_active=False)
        super(UserAICreds, self).save(*args, **kwargs)
