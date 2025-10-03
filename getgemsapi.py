import requests
import json
import time

class GetGemsAPI:
    def __init__(self, api_host, collection_address, authorization):
        self.api_host = api_host
        self.collection_address = collection_address
        self.authorization = authorization
    
    def mint_nft(self, image_url, owner_address, name, description, attributes=None, index=0):
        """Создает NFT в коллекции"""
        url = f"{self.api_host}/public-api/minting/{self.collection_address}"
        headers = {
            'accept': 'application/json',
            'authorization': self.authorization,
            'Content-Type': 'application/json'
        }
        
        request_id = f"mint_{int(time.time() * 1000)}_{index}"
        
        nft_data = {
            "requestId": request_id,
            "ownerAddress": owner_address,
            "name": name,
            "description": description,
            "image": image_url,
            "index": index
        }
        
        if attributes:
            nft_data["attributes"] = attributes
        
        try:
            response = requests.post(url, headers=headers, json=nft_data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    return {
                        'success': True,
                        'nft_address': result['response']['address'],
                        'nft_url': result['response']['url'],
                        'status': result['response']['status'],
                        'request_id': request_id
                    }
                else:
                    return {
                        'success': False,
                        'error': 'API returned success: false',
                        'response': result
                    }
            else:
                return {
                    'success': False,
                    'error': f'HTTP error {response.status_code}',
                    'response_text': response.text
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

# Глобальный экземпляр для удобства
# api_host = "https://api.testnet.getgems.io"
api_host = "https://api.getgems.io"
# collection_address = "EQCllppDPc4Vm5CpVb2UlbKvBagMKlf4QCvdymGGx_x2o9bd"
collection_address = "EQB3cAoOHlU4g1xrSveoyhkhv-4UzniOZO92VjEMTwFJsOFS"
# authorization = "175******7763-testnet-23**-a-eKoLhJtEzI1P*****IggzAqsA3yt0***UbhBw9GgtJwPgz"
authorization = "17578-mainnet-12n5Co2L******q2wK9"
getgems_api = GetGemsAPI(api_host, collection_address, authorization)
