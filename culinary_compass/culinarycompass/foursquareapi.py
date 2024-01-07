import requests

url = "https://api.foursquare.com/v3/places/fsq_id"

headers = {
    "accept": "application/json",
    "Authorization": ""
}

response = requests.get(url, headers=headers)

print(response.text)