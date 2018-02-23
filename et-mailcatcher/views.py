from django.views import View
from django.http import HttpResponse
from .models import TriggeredSend
import json

class TriggeredSendView(View):

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            email = data["To"]["Address"]
            ts = TriggeredSend(email=email, data=data)
            ts.save()
            # TODO: return ET like response
            return HttpResponse("{}")
        except Exception as e:
            return HttpResponse("{"error":"{}"}".format(e),
                                status=500)

