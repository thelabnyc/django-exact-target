from django.core.cache import cache
from django.test import TestCase
import requests_mock
import simplejson
import mock

from exacttarget import token


class BaseTokenTestMixin(object):
    def mock_response(self, m):
        data = {"i": 0}

        def make_response(request, context):
            req = simplejson.loads(request.body)
            self.assertEqual(req["clientId"], "my-client-id")
            self.assertEqual(req["clientSecret"], "my-client-secret")
            resp = simplejson.dumps(
                {
                    "accessToken": "foobar-%s" % data["i"],
                    "expiresIn": 3600,
                }
            )
            data["i"] += 1
            return resp

        respond = mock.MagicMock()
        respond.side_effect = make_response

        m.register_uri(
            "POST", "https://auth.exacttargetapis.com/v1/requestToken", text=respond
        )
        self.assertEqual(respond.call_count, 0)
        return respond


@requests_mock.Mocker()
class TokenGeneratorTest(BaseTokenTestMixin, TestCase):
    def test_generate_token(self, m):
        respond = self.mock_response(m)

        t = token.TokenGenerator().generate()

        self.assertEqual(respond.call_count, 1)
        self.assertEqual(t, "foobar-0")

        t = token.TokenGenerator().generate()

        self.assertEqual(respond.call_count, 2)
        self.assertEqual(t, "foobar-1")

    def test_headers(self, m):
        respond = self.mock_response(m)

        headers = token.TokenGenerator().headers()

        self.assertEqual(respond.call_count, 1)
        self.assertEqual(headers["Authorization"], "Bearer foobar-0")

        headers = token.TokenGenerator().headers()

        self.assertEqual(respond.call_count, 2)
        self.assertEqual(headers["Authorization"], "Bearer foobar-1")


@requests_mock.Mocker()
class CachedTokenGeneratorTest(BaseTokenTestMixin, TestCase):
    def setUp(self):
        cache.clear()

    def test_generate_token(self, m):
        respond = self.mock_response(m)

        t = token.CachedTokenGenerator().generate()

        self.assertEqual(respond.call_count, 1)
        self.assertEqual(t, "foobar-0")

        t = token.CachedTokenGenerator().generate()

        self.assertEqual(respond.call_count, 1)
        self.assertEqual(t, "foobar-0")

    def test_headers(self, m):
        respond = self.mock_response(m)

        headers = token.CachedTokenGenerator().headers()

        self.assertEqual(respond.call_count, 1)
        self.assertEqual(headers["Authorization"], "Bearer foobar-0")

        headers = token.CachedTokenGenerator().headers()

        self.assertEqual(respond.call_count, 1)
        self.assertEqual(headers["Authorization"], "Bearer foobar-0")
