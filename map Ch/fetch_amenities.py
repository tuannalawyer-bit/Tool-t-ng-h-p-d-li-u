import requests
import json
import sys
import io

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

overpass_url = "https://overpass-api.de/api/interpreter"
overpass_query = """
[out:json][timeout:300];
area["ISO3166-1"="VN"][admin_level=2]->.searchArea;
(
  node["amenity"~"^(school|kindergarten|university|college|hospital|clinic|doctors)$"](area.searchArea);
  way["amenity"~"^(school|kindergarten|university|college|hospital|clinic|doctors)$"](area.searchArea);
  relation["amenity"~"^(school|kindergarten|university|college|hospital|clinic|doctors)$"](area.searchArea);
);
out center;
"""

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

print("Sending query to Overpass API for all schools/hospitals in Vietnam...")
print("This may take a few seconds to a couple of minutes...")

try:
    headers = {
        'User-Agent': 'AntigravityStoreAnalyzer/1.0 (contact: non-commercial research python script)',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.post(overpass_url, data={'data': overpass_query}, headers=headers, verify=False)
    response.raise_for_status()
    data = response.json()
    
    elements = data.get('elements', [])
    print(f"Successfully fetched {len(elements)} elements!")
    
    # Save cache
    output_path = r"d:\Dự án AI\map Ch\vietnam_amenities.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Saved to {output_path}")
    
except Exception as e:
    print(f"Error during Overpass API query: {e}")
