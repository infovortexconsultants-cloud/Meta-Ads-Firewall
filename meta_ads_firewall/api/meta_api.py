import requests
import logging
logger = logging.getLogger('MetaAPI')

class MetaAPI:
    def __init__(self, access_token: str = None, ad_account_id: str = None):
        self.access_token = access_token
        self.ad_account_id = ad_account_id

    def test_connection(self) -> bool:
        if not self.access_token or not self.ad_account_id:
            logger.error('Missing Meta API credentials')
            return False
        url = f'https://graph.facebook.com/v17.0/{self.ad_account_id}'
        try:
            r = requests.get(url, params={'access_token': self.access_token}, timeout=10)
            return r.status_code == 200
        except Exception as e:
            logger.exception('Meta API test failed: %s', e)
            return False
