import requests

# headers = {"X-INTEGRATION-Authorization": token_uau,
#     "Content-Type": "application/json"}
# data = {
#     'login': login_uau,
#     'senha': senha_uau
# }

request = requests.get("https://economia.awesomeapi.com.br/USD-BRL/31?start_date=20220101&end_date=20220131")
print(request.json())
