import requests

url = "http://127.0.0.1:5000/get_wine_advice"
data = {"query": "What wine pairs well with steak?"}
response = requests.post(url, json=data)

print("Response:", response.json())
