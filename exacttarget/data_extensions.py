from raven.contrib.django.raven_compat.models import client as raven_client
import requests
from . import token, exceptions


class DataExtension(object):
    '''post a data extension'''
    url_base = 'https://www.exacttargetapis.com/hub/v1/dataevents'

    def __init__(self, external_key):
        self.external_key = external_key
        self.token = token.CachedTokenGenerator()

    def create(self, keys, attrs):
        url = '%s/key:%s/rowset' % (self.url_base, self.external_key)
        headers = self.token.headers()
        # api endpoint accepts multiple rows, but we only send one at a time for now
        req_data = [
            {"keys": keys, "values": attrs}
        ]
        print('\nsending this request to {}:\n\t{}\n'.format(url,json.dumps(req_data)))
        resp = requests.post(url, headers=headers, json=req_data)
        reply = resp.json()
        print('response from ET ok:', resp.ok, resp.json())
        if not resp.ok:
            raven_client.captureMessage('Error occurred while submitting data extension to exact target', extra=reply)
            message = reply.get('message', '')
            raise exceptions.TriggeredSendException(message or 'Unknown TriggeredSend Error Occurred')
