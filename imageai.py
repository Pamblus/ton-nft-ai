import aiohttp
import asyncio
import json
import requests
import time
import subprocess
import sys
import os

# Конфигурация
API_KEY = "64713da3********f-95dc-551228d3e248"
# WALLET_ADDRESS = "UQCanRaXampOVHaytBEWJ0-tlvqNNaA8IMNbrP7H4KyTubCp"
WALLET_ADDRESS = "UQAZi3-4juezPUWeYklag_ocgaceBPAcREaRqKc2uyGz6YbV"
GETGEMS_API_HOST = "https://api.getgems.io"
# COLLECTION_ADDRESS = "EQCllppDPc4Vm5CpVb2UlbKvBagMKlf4QCvdymGGx_x2o9bd"
COLLECTION_ADDRESS = "EQB3cAoOHlU4g1xrSveoyhkhv-4UzniOZO92VjEMTwFJsOFS"
# AUTHORIZATION = "17588049********lHUbhBw9GgtJwPgz"
AUTHORIZATION = "1********978-mainnet-128*******K9"
class ImageAIGenerator:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://neuroimg.art/api/v1/free-generate"
        self.last_lt = 0
    
    async def generate_image(self, prompt):
        """Генерирует изображение через AI API"""
        print(f"🎨 Генерируем изображение для промпта: '{prompt}'")
        
        async with aiohttp.ClientSession() as session:
            payload = {
                "token": self.api_key,
                "model": "flux-schnell",
                "prompt": prompt,
                "width": 1024,
                "height": 1024,
                "steps": 25,
                "sampler": "Euler",
                "cfg_scale": 7,
                "stream": True,
                "response_type": "url"
            }

            try:
                async with session.post(self.base_url, json=payload) as response:
                    async for line in response.content:
                        if line:
                            try:
                                data = line.decode('utf-8').strip()
                                if data:
                                    status = json.loads(data)
                                    
                                    if status["status"] == "WAITING":
                                        print(f"🕒 В очереди: {status['queue_position']}/{status['queue_total']}")
                                    elif status["status"] == "RUNNING":
                                        print("🎨 Генерация изображения...")
                                    elif status["status"] == "SUCCESS":
                                        print("✅ Изображение готово!")
                                        return status['image_url']
                                
                            except json.JSONDecodeError as e:
                                print(f"❌ Ошибка парсинга JSON: {e}")
                                continue
                
                return None
                
            except Exception as e:
                print(f"❌ Ошибка генерации: {e}")
                return None

    def download_image(self, image_url):
        """Скачивает изображение по URL"""
        try:
            print(f"📥 Скачиваем изображение: {image_url}")
            response = requests.get(image_url, timeout=30)
            if response.status_code == 200:
                return response.content
            else:
                print(f"❌ Ошибка скачивания: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Ошибка скачивания: {e}")
            return None

    def upload_to_hosting(self, image_data):
        """Загружает изображение на хостинг"""
        try:
            # Сохраняем временный файл
            temp_filename = f"ai_image_{int(time.time())}.png"
            with open(temp_filename, 'wb') as f:
                f.write(image_data)
            
            # Используем upload.py
            result = subprocess.run([sys.executable, 'upload.py', temp_filename], 
                                  capture_output=True, text=True, timeout=30)
            
            # Удаляем временный файл
            os.remove(temp_filename)
            
            if "OK" in result.stdout:
                # Парсим URL
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if line.startswith("URL: "):
                        url = line.replace("URL: ", "").strip()
                        print(f"✅ Изображение загружено: {url}")
                        return url
            
            print(f"❌ Ошибка загрузки: {result.stdout}")
            return None
            
        except Exception as e:
            print(f"❌ Ошибка загрузки на хостинг: {e}")
            return None

    def mint_nft(self, image_url, owner_address, prompt):
        """Создает NFT с AI изображением"""
        url = f"{GETGEMS_API_HOST}/public-api/minting/{COLLECTION_ADDRESS}"
        headers = {
            'accept': 'application/json',
            'authorization': AUTHORIZATION,
            'Content-Type': 'application/json'
        }
        
        nft_data = {
            "requestId": f"ai_{int(time.time() * 1000)}",
            "ownerAddress": owner_address,
            "name": f"AI Art: {prompt[:30]}...",
            "description": f"AI generated art for prompt: {prompt}",
            "image": image_url,
            "attributes": [
                {
                    "trait_type": "Generator",
                    "value": "AI"
                },
                {
                    "trait_type": "Prompt",
                    "value": prompt
                },
                {
                    "trait_type": "Type",
                    "value": "AI Art"
                }
            ],
            "index": int(time.time() % 1000000)  # Уникальный индекс
        }
        
        try:
            print("📦 Минтим NFT...")
            response = requests.post(url, headers=headers, json=nft_data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print("✅ NFT успешно создан!")
                    print(f"🔗 Ссылка: {result['response']['url']}")
                    return True
                else:
                    print(f"❌ Ошибка API: {result}")
            else:
                print(f"❌ HTTP ошибка: {response.status_code}")
                print(f"📄 Ответ: {response.text}")
            
            return False
            
        except Exception as e:
            print(f"❌ Ошибка минта: {e}")
            return False

    def get_transactions(self):
        """Получает транзакции кошелька"""
        url = "https://toncenter.com/api/v2/getTransactions"
        params = {
            'address': WALLET_ADDRESS,
            'limit': 5,
            'archival': False
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    return data.get('result', [])
            return []
        except Exception as e:
            print(f"❌ Ошибка получения транзакций: {e}")
            return []

    def parse_transaction(self, tx):
        """Парсит транзакцию"""
        try:
            in_msg = tx.get('in_msg', {})
            if not in_msg:
                return None
                
            value = int(in_msg.get('value', 0)) / 10**9
            message = in_msg.get('message', '').strip()
            sender = in_msg.get('source', '')
            lt = int(tx['transaction_id']['lt'])
            
            return {
                'value': value,
                'message': message,
                'sender': sender,
                'lt': lt
            }
        except Exception as e:
            print(f"❌ Ошибка парсинга: {e}")
            return None

    async def process_transaction(self, tx_data):
        """Обрабатывает транзакцию: генерирует AI изображение и минт NFT"""
        if tx_data['value'] < 0.02:
            print("❌ Сумма меньше 0.02 TON, пропускаем")
            return False
        
        prompt = tx_data['message']
        if not prompt:
            prompt = "abstract digital art"
        
        print(f"🎯 Обрабатываем транзакцию: {tx_data['value']} TON, промпт: '{prompt}'")
        
        # Генерируем изображение
        image_url = await self.generate_image(prompt)
        if not image_url:
            return False
        
        # Скачиваем изображение
        image_data = self.download_image(image_url)
        if not image_data:
            return False
        
        # Загружаем на хостинг
        final_image_url = self.upload_to_hosting(image_data)
        if not final_image_url:
            return False
        
        # Минтим NFT
        success = self.mint_nft(final_image_url, tx_data['sender'], prompt)
        return success

    def get_initial_last_lt(self):
        """Получает начальный LT"""
        transactions = self.get_transactions()
        if transactions:
            return max(int(tx['transaction_id']['lt']) for tx in transactions)
        return 0

    async def start_monitoring(self):
        """Запускает мониторинг транзакций"""
        self.last_lt = self.get_initial_last_lt()
        
        print("🚀 AI NFT Generator запущен!")
        print(f"👛 Адрес кошелька: {WALLET_ADDRESS}")
        print("💡 Отправьте >0.02 TON с комментарием-промптом")
        print("🤖 AI сгенерирует изображение и создаст NFT")
        print("=" * 60)
        
        while True:
            try:
                transactions = self.get_transactions()
                new_transactions = []
                
                for tx in transactions:
                    tx_lt = int(tx['transaction_id']['lt'])
                    if tx_lt > self.last_lt:
                        new_transactions.append(tx)
                
                if new_transactions:
                    print(f"📥 Найдено новых транзакций: {len(new_transactions)}")
                
                for tx in new_transactions:
                    tx_data = self.parse_transaction(tx)
                    if tx_data:
                        await self.process_transaction(tx_data)
                    
                    # Обновляем last_lt
                    tx_lt = int(tx['transaction_id']['lt'])
                    if tx_lt > self.last_lt:
                        self.last_lt = tx_lt
                
                await asyncio.sleep(5)
                
            except KeyboardInterrupt:
                print("\n🛑 Генератор остановлен")
                break
            except Exception as e:
                print(f"❌ Ошибка: {e}")
                await asyncio.sleep(10)

# Создаем глобальный экземпляр
ai_generator = ImageAIGenerator(API_KEY)

async def main():
    """Основная функция"""
    await ai_generator.start_monitoring()

if __name__ == "__main__":
    # Проверяем что upload.py существует
    if not os.path.exists('upload.py'):
        print("❌ Файл upload.py не найден!")
        print("📁 Создайте файл upload.py для загрузки изображений")
        exit(1)
    
    # Запускаем мониторинг
    asyncio.run(main())
