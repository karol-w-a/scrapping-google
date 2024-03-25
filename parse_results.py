import json
import os
import csv
import datetime

CACHE_PATH = 'cache'
ADDRESS_KEY = 'addressComponents'
FIELDNAMES = ['place_id', 'name', 'status',
              'city', 'street', 'number', 'postal_code',
              'lat', 'lng', 'powiat', 'wojewodztwo', 'country',
              'phone',
              'primary_type', 'types',
              'google_place_url', 'google_location_url', 'street_view_url']

today_date = datetime.date.today().strftime('%Y-%m-%d')
file_out = f'google_maps_{today_date}.csv'


def get_cache_file_names():
    cache_path = CACHE_PATH
    return [f for f in os.listdir(cache_path) if os.path.isfile(os.path.join(cache_path, f))]

def extract_google_places_info(google_places_response: dict):
    return_address = {
        'place_id': None,
        'name': None,
        'phone': None,
        'status': None,
        'city': None,
        'street': None,
        'number': None,
        'postal_code': None,
        'lat': None,
        'lng': None,
        'powiat': None,
        'wojewodztwo': None,
        'country': None,
        'primary_type': '',
        'types': [],
        'google_place_url': None,
        'google_location_url': None,
    }
    for component in google_places_response['addressComponents']:
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
            return_address['powiat'] = component['longText']
        elif 'administrative_area_level_1' in types:
            return_address['wojewodztwo'] = component['longText']
        elif 'country' in types:
            return_address['country'] = component['longText']

    return_address['lat'] = google_places_response['location']['latitude']
    return_address['lng'] = google_places_response['location']['longitude']

    return_address['place_id'] = google_places_response['id']
    return_address['phone'] = google_places_response.get('nationalPhoneNumber')
    return_address['name'] = google_places_response['displayName']['text']
    return_address['status'] = google_places_response['businessStatus']
    return_address['primary_type'] = google_places_response.get('primaryType')
    return_address['types'] = google_places_response['types']

    return return_address


def parse_scrapped_points():
    result_files_count = 0
    google_places_count = 0
    file_names = get_cache_file_names()

    google_places = set()

    with open(file_out, 'w') as f_out:
        writer = csv.DictWriter(f_out, fieldnames=FIELDNAMES)
        writer.writeheader()
        for file_name in file_names:
            result_files_count += 1
            print(f'Parsing file: {file_name}')
            with open(os.path.join(CACHE_PATH, file_name), 'r') as f:
                data = json.loads(f.read())
                if data.get('places'):
                    for place in data['places']:
                        address = extract_google_places_info(place)
                        if address['place_id'] not in google_places:
                            google_places.add(address['place_id'])
                            address['google_place_url'] = f'https://www.google.com/maps/place/?q=place_id:{address["place_id"]}'
                            address['google_location_url'] = f'https://www.google.com/maps/@{address["lat"]},{address["lng"]},21z'
                            address['street_view_url'] = f'https://www.google.com/maps/@?api=1&map_action=pano&viewpoint={address["lat"]},{address["lng"]}'
                            writer.writerow(address)
                            google_places_count += 1
    print(f'Parsed {result_files_count} files')
    print(f'Scraped  {google_places_count} google places')

if __name__ == '__main__':
    parse_scrapped_points()
    print('Done!')
