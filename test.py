import requests

req = requests.get('https://edu.donstu.ru/api/Rasp?idGroup=44371&date=2022-09-07')
print(req)

rasp = req.json()['data']['rasp']
[i for i in rasp if '2022-09-01' in i['дата']]
