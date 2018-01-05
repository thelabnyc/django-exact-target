import logging
from django.conf import settings
from raven.contrib.django.raven_compat.models import client as raven_client
import requests
from . import token, exceptions

logger = logging.getLogger(__name__)



class TriggeredSend(object):
    url_base = 'https://www.exacttargetapis.com/messaging/v1/messageDefinitionSends'

    def __init__(self, external_key):
        self.external_key = external_key
        self.token = token.CachedTokenGenerator()


    def dispatch(self, email, attrs):
        url = '%s/key:%s/send' % (self.url_base, self.external_key)
        headers = self.token.headers()
        req_data = {
            "To": {
                "Address": email,
                "SubscriberKey": email,
                "ContactAttributes": {
                    "SubscriberAttributes": attrs
                },
            },
            "OPTIONS": {
                "RequestType": "SYNC"
            },
        }

        resp = requests.post(url, headers=headers, json=req_data)
        resp.raise_for_status()
        reply = resp.json()
        for response in reply['responses']:
            if response['hasErrors']:
                error_messages = response.get('messageErrors', [])
                # set of error codes in messages
                error_codes = {err.get('messageErrorCode') for err in error_messages}
                # coerce ET_IGNORED_ERROR_CODES into set
                codes_to_ignore = set(getattr(settings, 'ET_IGNORED_ERROR_CODES', {}))

                # if response has any ignorable codes... set intersection
                if codes_to_ignore & error_codes:
                    # log error, but don't send ignored error codes to raven
                    logger.warn("Suppressed exception for ET API exception. Error response: {}".format(reply))
                else:
                    raven_client.captureMessage('Error occurred while submitting subscriber to exact target', extra=reply)
                    reg_messages = response.get('messages')
                    # sometimes there are structured errors
                    if len(error_messages):
                        raise exceptions.TriggeredSendException(error_messages[0]['messageErrorStatus'])
                    # sometimes there are plain text errors
                    elif len(reg_messages):
                        raise exceptions.TriggeredSendException(reg_messages[0])
                    else:
                        raise exceptions.TriggeredSendException('Unknown TriggeredSend Error Occurred')
        return reply
