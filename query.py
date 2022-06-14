import requests

routes = requests.get("http://ray:8000/-/routes").json()

response = requests.get("http://ray:8000/my_path")
print(response)
