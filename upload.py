import requests
import sys
import os
from mimetypes import guess_type

def main():
    if len(sys.argv) != 2:
        print("Usage: python upload.py <image_path>")
        sys.exit(1)

    image_path = sys.argv[1]
    url = 'https://cтвой сайт/загрузить.пхп'

    if not os.path.exists(image_path):
        print(f"Error: File {image_path} not found")
        return

    mime_type, _ = guess_type(image_path)
    if not mime_type:
        mime_type = 'image/png'

    try:
        with open(image_path, 'rb') as f:
            files = {
                'image': (os.path.basename(image_path), f, mime_type)
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0'
            }
            
            r = requests.post(url, files=files, headers=headers, timeout=30)
            data = r.json()
            
            if data.get('status') == 'ok':
                print("OK")
                print(f"URL: {data['url']}")
                print(f"Filename: {data['filename']}")
            else:
                print(f"Error: {data.get('error', 'Unknown error')}")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
