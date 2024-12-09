import csv
from datetime import datetime

import requests

from crawler import get_bearer_token

# Step 1: Fetch the JSON data from the API route
url = "https://app.polemicagame.com/v1/competitions/2299/metrics?scoringType=1"

try:
    headers = {'Authorization': f'Bearer {get_bearer_token()}'}
    response = requests.get(url, {})
    response.raise_for_status()  # Raise an error for bad status codes
    data = response.json()
except requests.exceptions.RequestException as e:
    print(f"Error fetching data: {e}")
    exit(1)

# Step 2: Process the JSON data to calculate the sum of totalScores for each player
players_data = []
for player in data:
    player_id = player["id"]
    player_name = player["username"]
    total_scores = round(sum([
        player["metrics"]["don"]["totalScores"],
        player["metrics"]["maf"]["totalScores"],
        player["metrics"]["com"]["totalScores"],
        player["metrics"]["civ"]["totalScores"],
    ]), 2)

    players_data.append({
        # "playerId": player_id,
        "playerName": player_name,
        "totalScores": str(total_scores).replace(".", ",")
    })

# Step 3: Write the processed data into a CSV file
current_date = datetime.now().strftime("%Y-%m-%d")
csv_filename = f"{current_date}.csv"

try:
    with open(csv_filename, mode='w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            # "playerId",
            "playerName",
            "totalScores"
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for player_data in players_data:
            writer.writerow(player_data)
    print(f"Data successfully written to {csv_filename}")
except IOError as e:
    print(f"Error writing to CSV file: {e}")
