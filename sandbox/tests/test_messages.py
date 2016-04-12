from django.core.cache import cache
from django.test import TestCase
import requests_mock
import simplejson
import mock

from exacttarget import messages, exceptions
from .test_token import BaseTokenTestMixin


class BaseMessageTestMixin(BaseTokenTestMixin):
    def mock_response(self, m, has_errors=False):
        super().mock_response(m)

        def make_response(request, context):
            req = simplejson.loads(request.body)
            self.assertEqual(req['To']['Address'], 'foo@example.com')
            self.assertEqual(req['To']['SubscriberKey'], 'foo@example.com')
            self.assertEqual(req['To']['ContactAttributes']['SubscriberAttributes'], { 'CampaignID': 'my-campaign-id' })
            self.assertEqual(req['OPTIONS']['RequestType'], 'SYNC')
            resp = simplejson.dumps({
                'responses': [
                    {
                        'hasErrors': has_errors,
                        'messageErrors': None if not has_errors else [
                            {
                                'messageErrorStatus': 'Some error occurred'
                            }
                        ]
                    }
                ]
            })
            return resp
        respond = mock.MagicMock()
        respond.side_effect = make_response

        url = 'https://www.exacttargetapis.com/messaging/v1/messageDefinitionSends/key:my-external-key/send'
        m.register_uri('POST', url, text=respond)
        self.assertEqual(respond.call_count, 0)
        return respond


@requests_mock.Mocker()
class TriggeredSendTest(BaseMessageTestMixin, TestCase):
    def test_dispatch(self, m):
        respond = self.mock_response(m)
        sender = messages.TriggeredSend('my-external-key')
        self.assertEqual(respond.call_count, 0)
        sender.dispatch('foo@example.com', { 'CampaignID': 'my-campaign-id' })
        self.assertEqual(respond.call_count, 1)

    def test_dispatch_with_errors(self, m):
        respond = self.mock_response(m, has_errors=True)
        sender = messages.TriggeredSend('my-external-key')
        def dispatch():
            sender.dispatch('foo@example.com', { 'CampaignID': 'my-campaign-id' })
        self.assertRaises(exceptions.TriggeredSendException, dispatch)
        self.assertEqual(respond.call_count, 1)
