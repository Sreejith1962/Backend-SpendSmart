from app import app, db, CityCost
# from app.models import CityCost  # Update this import based on your structure
import requests
from datetime import datetime, timezone

RAPID_API_KEY = "48a15926f9msh4d5dee488a67d77p1d2717jsn2e3367a9a578"
RAPID_API_HOST = "cost-of-living-and-prices.p.rapidapi.com"

def fetch_and_add_city(city_name):
    url = f"https://{RAPID_API_HOST}/prices"
    params = {"city_name": city_name, "country_name": "India"}
    headers = {
        "x-rapidapi-key": RAPID_API_KEY,
        "x-rapidapi-host": RAPID_API_HOST,
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        resdata = response.json()

        rent_min = next((item["min"] for item in resdata["prices"] if item["item_name"] == "One bedroom apartment outside of city centre"), None)
        rent_max = next((item["max"] for item in resdata["prices"] if item["item_name"] == "Three bedroom apartment outside of city centre"), None)
        salary_min = next((item["min"] for item in resdata["prices"] if item["item_name"] == "Average Monthly Net Salary, After Tax"), None)
        salary_max = next((item["max"] for item in resdata["prices"] if item["item_name"] == "Average Monthly Net Salary, After Tax"), None)

        if None in (rent_min, rent_max, salary_min, salary_max):
            print(f"Missing data for {city_name}, skipping...")
            return

        existing = CityCost.query.filter_by(city_name=city_name).first()

        if existing:
            print(f"{city_name} already exists, skipping...")
            return

        city = CityCost(
            city_name=city_name,
            rent_min=rent_min,
            rent_max=rent_max,
            salary_min=salary_min,
            salary_max=salary_max,
            last_updated=datetime.now(timezone.utc)
        )
        db.session.add(city)
        db.session.commit()
        print(f"Added city cost for {city_name}")

    except Exception as e:
        print(f"Error fetching or saving {city_name}: {e}")

if __name__ == "__main__":
    with app.app_context():
        cities = ["Delhi", "Bengaluru", "Kochi"]
        for city in cities:
            fetch_and_add_city(city)
