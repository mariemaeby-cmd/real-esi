import json
import requests

OVERPASS_URL = "https://overpass-api.de"

# TYPO FIXED: Clean query targeting hospital and clinic tags across India map nodes
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
    print("Connecting to OpenStreetMap directory registries...")
    try:
        response = requests.post(
            OVERPASS_URL, data={"data": OVERPASS_QUERY}, timeout=60
        )
        if response.status_code == 200:
            elements = response.json().get("elements", [])
            data_list = []

            print(f"Found {len(elements)} real map nodes. Processing fields...")

            for item in elements:
                tags = item.get("tags", {})
                state = tags.get("addr:state", "India Region")
                city = tags.get(
                    "addr:city", tags.get("addr:district", "Local Zone")
                )
                name = tags.get("name", "ESI Facility")
                phone = tags.get(
                    "phone", tags.get("contact:phone", "Verify via Portal")
                )

                # Collect structural coordinates if available from map pins
                lat_coord = item.get("lat") or (
                    item.get("center", {}).get("lat") if "center" in item else None
                )
                lon_coord = item.get("lon") or (
                    item.get("center", {}).get("lon") if "center" in item else None
                )

                data_list.append(
                    {
                        "state": state,
                        "location": f"{name}, {city}",
                        "type": tags.get("amenity", "Hospital").title(),
                        "contact": phone,
                        "lat": lat_coord,
                        "lon": lon_coord,
                    }
                )

            # Saves the data into its own separate data file
            with open("esi_live_data.json", "w", encoding="utf-8") as f:
                json.dump(data_list, f, indent=4)
            print("Data file 'esi_live_data.json' generated successfully!")
        else:
            print("Map server returned an error:", response.status_code)
    except Exception as e:
        print("Error connecting to server:", e)


if __name__ == "__main__":
    get_real_map_data()
  
