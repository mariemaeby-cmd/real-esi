import json
import urllib.request
import urllib.parse

OVERPASS_URL = "https://overpass-api.de"

# TYPO REMOVED: Clean query targeting hospital and clinic tags across India map nodes
OVERPASS_QUERY = """
[out:json][timeout:90];
area["ISO3166-1"="IN"]->.searchArea;
(
  node["amenity"="hospital"]["name"~"ESI",i](area.searchArea);
  way["amenity"="hospital"]["name"~"ESI",i](area.searchArea);
  node["amenity"="clinic"]["name"~"ESI",i](area.searchArea);
);
out tags center;
"""

def get_real_map_data():
    print("Connecting directly to OpenStreetMap directory registries...")
    try:
        data = urllib.parse.urlencode({'data': OVERPASS_QUERY}).encode('utf-8')
        req = urllib.request.Request(OVERPASS_URL, data=data)
        
        with urllib.request.urlopen(req, timeout=60) as response:
            if response.status == 200:
                raw_json = json.loads(response.read().decode('utf-8'))
                elements = raw_json.get('elements', [])
                data_list = []
                
                print(f"Found {len(elements)} real map nodes. Processing fields...")
                
                for item in elements:
                    tags = item.get('tags', {})
                    state = tags.get('addr:state', 'India Region')
                    city = tags.get('addr:city', tags.get('addr:district', 'Local Zone'))
                    name = tags.get('name', 'ESI Facility')
                    phone = tags.get('phone', tags.get('contact:phone', 'Verify via Portal'))
                    
                    lat_coord = item.get('lat') or (item.get('center', {}).get('lat') if 'center' in item else None)
                    lon_coord = item.get('lon') or (item.get('center', {}).get('lon') if 'center' in item else None)
                    
                    data_list.append({
                        'state': state,
                        'location': f"{name}, {city}",
                        'type': tags.get('amenity', 'Hospital').title(),
                        'contact': phone,
                        'lat': lat_coord,
                        'lon': lon_coord
                    })
                
                with open('esi_live_data.json', 'w', encoding='utf-8') as f:
                    json.dump(data_list, f, indent=4)
                print("Database file 'esi_live_data.json' created successfully!")
            else:
                print("Map server returned an error code:", response.status)
    except Exception as e:
        print("System encountered a network error:", e)

if __name__ == "__main__":
    get_real_map_data()
