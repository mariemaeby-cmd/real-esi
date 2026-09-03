import json
import os
import pandas as pd
import requests

# 1. Connect to the public Overpass API endpoint for OpenStreetMap data
OVERPASS_URL = "https://overpass-api.de"

# 2. This query scans the entire map of India for any hospital or clinic with "ESI" in its name
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


def scrape_open_maps_esi():
    print("Connecting to OpenStreetMap directory registries...")

    try:
        # Send the data request to the public map server
        response = requests.post(
            OVERPASS_URL, data={"data": OVERPASS_QUERY}, timeout=60
        )

        if response.status_code == 200:
            elements = response.json().get("elements", [])
            data_list = []

            print(f"Found {len(elements)} raw map nodes. Parsing real text...")

            # 3. Loop through every single real facility found on the map
            for item in elements:
                tags = item.get("tags", {})

                # Extract address data fields safely
                state = tags.get("addr:state", "Verified Region")
                city = tags.get(
                    "addr:city", tags.get("addr:district", "India Zone")
                )
                name = tags.get("name", "ESI Healthcare Facility")

                # Extract phone numbers if mapped by local users
                phone = tags.get(
                    "phone", tags.get("contact:phone", "Check Portal Registry")
                )

                # Clean and structure the dataset row
                data_list.append(
                    {
                        "state": state,
                        "location": f"{name}, {city}",
                        "type": tags.get("amenity", "Hospital").title(),
                        "contact": phone,
                    }
                )

            # 4. Save everything directly as a JSON file for your HTML website frontend
            with open("esi_live_data.json", "w", encoding="utf-8") as f:
                json.dump(data_list, f, indent=4)

            print(
                f"Successfully compiled {len(data_list)} real facilities into 'esi_live_data.json'!"
            )

        else:
            print(
                f"Map directory returned a connection error: {response.status_code}"
            )

    except Exception as e:
        print(f"Encountered a network tracking error: {e}")


if __name__ == "__main__":
    scrape_open_maps_esi()
