import requests
import json
import hashlib
import os
import csv
import time
import random

# Google Places API Key from file
with open('google_places_api_key.txt', 'r') as f:
    API_KEY = f.read().strip()


def read_points(file_path: str) -> list:
    with open(file_path, 'r') as f:
        reader = csv.reader(f)
        next(reader)
        return list(reader)


class GooglePlacesScrapper:
    def __init__(self, api_key, scrap_points=[]):
        self.api_key = api_key
        self.api_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        self.min_delay = 7.5
        self.max_delay = 61.5
        self.scrap_points = scrap_points
        self.cache_path = 'cache'
        
    def cache_result_to_file(self, lat, lng, radius, result):
        file_name = hashlib.md5(f"{lat},{lng},{radius}".encode()).hexdigest()
        cache_path = self.cache_path
        file_path = os.path.join(cache_path, file_name)
        try:
            with open(file_path, 'w') as f:
                if isinstance(result, str):
                    print(f"Writing string to file: {file_name}")
                    f.write(result)
                elif isinstance(result, dict):
                    print(f"Writing dict to file: {file_name}")
                    f.write(json.dumps(result))
                else:
                    raise Exception("Unknown type")
                return True
        except:
            return False

    def load_result_from_cache(self, lat, lng, radius):
        cache_path = self.cache_path
        file_name = hashlib.md5(f"{lat},{lng},{radius}".encode()).hexdigest()
        try:
            file_path = os.path.join(cache_path, file_name)
            with open(file_path, 'r') as f:
                print(f"Loading from cache: {file_name}")
                return json.loads(f.read())
        except:
            return None

    def google_search_nearby(self, lat, lng, radius_meters, languageCode='pl', maxResultCount=20, rankPreference='DISTANCE'):
        url = 'https://places.googleapis.com/v1/places:searchNearby'
        types = ["supermarket", "grocery_store", "convenience_store", "discount_store", "liquor_store"]
        field_mask = ["places.id", "places.displayName", "places.addressComponents", "places.businessStatus",
                      "places.location", "places.types", "places.primaryType", "places.nationalPhoneNumber"]

        d = {
            "includedTypes": types,
            "maxResultCount": maxResultCount,
            "locationRestriction": {
                "circle": {
                    "center": {
                        "latitude": lat,
                        "longitude": lng
                    },
                "radius": radius_meters
                }
            },
            'languageCode': languageCode,
            "rankPreference": rankPreference
        }

        h = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": API_KEY,
            "X-Goog-FieldMask": ",".join(field_mask)
        }

        result = requests.post(url, data=json.dumps(d), headers=h)
        if result.status_code != 200:
            print(result.text)
            return None
        return result.json()

    def scrap(self):
        for point in self.scrap_points:
            lat, lng, radius = point
            print(f"Scraping: {lat}, {lng}, radius: {radius}")
            result = self.load_result_from_cache(lat, lng, radius)
            if result is None:
                result = self.google_search_nearby(lat, lng, radius)
                if result is not None:
                    self.cache_result_to_file(lat, lng, radius, result)
                else:
                    print(f"Failed on request: {result.text}")
                    exit(-1)
                time.sleep(random.uniform(self.min_delay, self.max_delay))
            print(result)


if __name__ == "__main__":
    points_path = 'creating-grid/scrap_points_radius_limit_per_cell_35.csv'
    points = read_points(points_path)
    # random points order:
    points = random.sample(points, 5000)
    scrapper = GooglePlacesScrapper(API_KEY, points)
    scrapper.scrap()
