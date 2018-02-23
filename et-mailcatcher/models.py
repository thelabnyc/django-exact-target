from django.db import models


class TriggeredSend(models.model):
    email = models.EmailField(),
    date_received = models.DateTimeField(auto_now_add=True)
    data = models.TextField()

