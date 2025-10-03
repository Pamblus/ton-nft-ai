import requests

class TransactionMonitor:
    def __init__(self, wallet_address):
        self.wallet_address = wallet_address
        self.last_lt = 0
    
    def get_transactions(self, limit=10):
        """Получает последние транзакции кошелька"""
        url = "https://toncenter.com/api/v2/getTransactions"
        params = {
            'address': self.wallet_address,
            'limit': limit,
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
        """Парсит транзакцию и извлекает данные"""
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
                'lt': lt,
                'transaction_id': tx['transaction_id']
            }
        except Exception as e:
            print(f"❌ Ошибка парсинга транзакции: {e}")
            return None
    
    def get_new_transactions(self):
        """Возвращает только новые транзакции"""
        transactions = self.get_transactions(5)
        new_transactions = []
        
        for tx in transactions:
            tx_lt = int(tx['transaction_id']['lt'])
            if tx_lt > self.last_lt:
                new_transactions.append(tx)
        
        # Обновляем last_lt
        if transactions:
            self.last_lt = max(int(tx['transaction_id']['lt']) for tx in transactions)
        
        return [self.parse_transaction(tx) for tx in new_transactions if self.parse_transaction(tx)]
    
    def initialize_last_lt(self):
        """Инициализирует last_lt текущей последней транзакцией"""
        transactions = self.get_transactions(1)
        if transactions:
            self.last_lt = int(transactions[0]['transaction_id']['lt'])
            return self.last_lt
        return 0

# Глобальный экземпляр для удобства
# wallet_address = "EQCP3m3nG7T6atRKXx53pDPhsbks--KvVNlrHqayKhMjKeCY"
wallet_address = "UQAZi3-4juezPUWeYklag_ocgaceBPAcREaRqKc2uyGz6YbV"
transaction_monitor = TransactionMonitor(wallet_address)
