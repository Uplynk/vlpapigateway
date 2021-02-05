import base64
import zlib
import hmac
import hashlib
import time
import json
import urllib.parse
import random


class APICredentials:
    """
    Stores information needed to make an Uplynk API call.
    """
    @property
    def user_id(self):
        """
        Set your user ID. Find this value within the Account Settings page
        within the Uplynk CMS.
        """
        return ''

    @property
    def secret(self):
        """
        Set your API key. Find this value within the Playback Tokens page
        within the Uplynk CMS.
        """
        return ''


class APIParams(object):
    """
    Helps make integration-test API calls. For details on the required message
    format, see:
        https://support.uplynk.com/doc_integration_apis.html
    """
    def __init__(self, credentials):
        self.credentials = credentials

    def get_params(self, data):
        """
        Encodes and signs <data> into the expected format and returns it.
        """
        data = self._get_params(**data)
        data.update(data)
        return data

    def _get_msg(self, msg=None):
        """
        Encodes and returns the 'msg' parameter.
        """
        msg = msg if msg else {}
        msg.update({
            '_owner': self.credentials.user_id,
            '_timestamp': int(time.time())
        })
        msg = json.dumps(msg)
        msg_compressed = zlib.compress(msg.encode(), 9)
        return base64.b64encode(msg_compressed).strip()
        print("msg: ", msg)

    def _get_params(self, **msg):
        """
        Returns the message and its signature.
        """
        msg = self._get_msg(msg)

        sig = hmac.new(
            self.credentials.secret.encode(), msg, hashlib.sha256
        ).hexdigest()
        return {
            'msg': msg,
            'sig': sig
        }


class Signer(object):
    def __init__(self, prefix, suffix, content_id):
        self.prefix = prefix
        self.suffix = suffix
        self.content_id = content_id

    def gen_playback_url(self, ad_config=None):
        aconfigstr = ad_config if ad_config else ''
        api_key = APICredentials().secret
        # combine all of the parameters except the signature
        queryStr = urllib.parse.urlencode(dict(
            tc='1',  # token check algorithm version
            exp=int(time.time()) + 600,  # expire 60 seconds from now
            rn=str(random.randint(0, 2 ** 32)),  # random number
            ct='p',
            cid=self.content_id,
            oid=APICredentials().user_id,
            test='1',
            ad=aconfigstr
        ))

        # compute the signature and add it to the *end*
        sig = hmac.new(api_key.encode('utf-8'), queryStr.encode('utf-8'), hashlib.sha256).hexdigest()
        queryStr = queryStr + '&sig=' + sig
        # Add the query string to the playback URL.
        url = self.prefix + '/' + self.content_id + '.' + self.suffix + '?' + queryStr
        print("Playback URL is: ")
        print(url)
