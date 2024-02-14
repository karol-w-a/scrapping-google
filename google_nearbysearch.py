import requests
import requests_cache
import time
import random
import csv
import json
from datetime import timedelta
from tqdm import tqdm

API_KEY = ""


def extract_google_places_info(google_location_response: dict):
    return_address = {
        'place_id': None,
        'name': None,
        'status': None,
        'city': None,
        'street': None,
        'number': None,
        'postal_code': None,
        'lat': None,
        'lng': None,
        'powiat': None,
        'wojewodztwo': None,
        'types': []
    }
    for component in google_location_response['addressComponents']:
        types = component['types']
        if 'postal_code' in types:
            return_address['postal_code'] = component['longText']
        elif 'locality' in types:
            return_address['city'] = component['longText']
        elif 'route' in types:
            return_address['street'] = component['longText']
        elif 'street_number' in types:
            return_address['number'] = component['longText']
        elif 'administrative_area_level_2' in types:
            powiat = component['longText']
        elif 'administrative_area_level_1' in types:
            wojewodztwo = component['longText']    

    return_address['lat'] = google_location_response['location']['latitude']
    return_address['lng'] = google_location_response['location']['longitude']

    return_address['place_id'] = google_location_response['id']
    return_address['name'] = google_location_response['displayName']['text']
    return_address['status'] = google_location_response['businessStatus']
    return_address['types'] = google_location_response['types']

    return return_address


def google_search_nearby(lat, lng, radius_meters, types, languageCode='pl', maxResultCount=20, rankPreference='DISTANCE'):
    url = 'https://places.googleapis.com/v1/places:searchNearby'

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
        "X-Goog-FieldMask": "places.id,places.displayName,places.addressComponents,places.businessStatus,places.location,places.types,places.primaryType,places.nationalPhoneNumber"
    }

    result = requests.post(url, data=json.dumps(d), headers=h)
    if result.status_code != 200:
        print(result.text)
        return None
    return result.json()


if __name__ == '__main__':
    lat = 52.25252821596603
    lng = 21.07384298400376

    radius_km = 10
    radius_meters = radius_km * 1000
    types = ["supermarket",
            "grocery_store",
            "convenience_store",
            "discount_store",
            "liquor_store",
            ]

    requests_cache.install_cache('google_nearby_search_cache', expire_after=timedelta(days=180))
    result = google_search_nearby(lat, lng, radius_meters, types)
    for place in result['places']:
        print(extract_google_places_info(place))