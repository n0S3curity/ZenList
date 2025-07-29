import requests


def getURL(url):
    try:
        print(f"Fetching data from {url}")
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        with open('response.json', 'w') as file:
            file.write(response.text)
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None


url = 'https://osher.pairzon.com/v1.0/documents/fe4f9bcf-050e-48f5-af2b-bb5a7b81f001?p=1247'

res = getURL(url)
if res:
    print(f"Data fetched successfully.\n {res}")
