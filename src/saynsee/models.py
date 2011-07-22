from django.db import models
from django.contrib.auth.models import User

#TODO: need auto expiration
class ChatRequest(models.Model):
    fromUser = models.ForeignKey(User)
    toUser = models.CharField(max_length=50)
    token = models.CharField(max_length=50,primary_key=True)
    auth_token = models.CharField(max_length=100,primary_key=True)
    session_id = models.CharField(max_length=100,primary_key=True)
    date = models.DateTimeField(auto_now=True, auto_now_add=True)
