import requests
import json
import urllib.parse

def fetch_ge_mapping():
    url = "https://prices.runescape.wiki/api/v1/osrs/mapping"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch data: {response.status_code}")

def process_icon_link(icon_name):
    base_url = 'https://oldschool.runescape.wiki/images/'
    # Replace spaces with underscores
    icon_name = icon_name.replace(' ', '_')
    # URL encode the remaining special characters, except underscores
    encoded_name = urllib.parse.quote(icon_name, safe='_')
    return base_url + encoded_name

def main():
    try:
        data = fetch_ge_mapping()
        for item in data:
            if 'icon' in item:
                item['link'] = process_icon_link(item['icon'])

        with open('../flipping/items.json', 'w') as f:
            json.dump(data, f, indent=2)
        print("Data successfully saved to items.json")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()