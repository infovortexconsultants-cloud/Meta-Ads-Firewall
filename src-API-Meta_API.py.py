import requests
import logging
from typing import Dict, Optional

class MetaAPI:
    """Meta Graph API wrapper with error handling"""
    
    def __init__(self, access_token: str, ad_account_id: str):
        self.access_token = access_token
        self.ad_account_id = ad_account_id
        self.base_url = "https://graph.facebook.com/v17.0"
        self.logger = logging.getLogger('MetaAPI')
        
    def _make_request(self, endpoint: str, method: str = 'GET', params: Dict = None) -> Optional[Dict]:
        """Make API request with error handling"""
        url = f"{self.base_url}/{endpoint}"
        
        default_params = {
            'access_token': self.access_token
        }
        
        if params:
            default_params.update(params)
            
        try:
            if method.upper() == 'GET':
                response = requests.get(url, params=default_params, timeout=30)
            else:
                response = requests.post(url, data=default_params, timeout=30)
                
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API request failed: {e}")
            return None
    
    def test_connection(self) -> bool:
        """Test API connection"""
        result = self._make_request(f"{self.ad_account_id}/campaigns", params={'limit': 1})
        return result is not None and 'data' in result
    
    def get_account_info(self) -> Optional[Dict]:
        """Get ad account information"""
        return self._make_request(self.ad_account_id)