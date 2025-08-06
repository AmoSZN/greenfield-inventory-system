import requests
import json

# Test update functionality
url = "https://greenfield-inventory-system.onrender.com/api/paradigm/update-quantity"
data = {"product_id": "RET4GAVLF", "quantity": 999}

response = requests.post(url, json=data)
print("Update Response:")
print(json.dumps(response.json(), indent=2))
