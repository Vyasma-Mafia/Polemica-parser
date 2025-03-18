import os
import sys

import pandas as pd
from datetime import datetime
import requests

from generate_tournament_seats import competition_id

baseurl = "https://app.polemicagame.com/v1"


def fetch_tournament_data(competition_id: int):
    try:
        url = baseurl + f"/competitions/{competition_id}/metrics?scoringType=1"
        response = requests.get(url)
        response.raise_for_status()
        players_data = []
        for player in response.json():
            player_id = player["id"]
            player_name = player["username"]
            total_scores = round(sum([
                player["metrics"]["don"]["totalScores"],
                player["metrics"]["maf"]["totalScores"],
                player["metrics"]["com"]["totalScores"],
                player["metrics"]["civ"]["totalScores"],
            ]), 2)

            players_data.append({
                "participant_name": player_name,
                "points": total_scores
            })
        return players_data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        exit(1)


def calculate_daily_points(current_results, previous_results):
    today = datetime.now().strftime('%Y-%m-%d')
    # Convert data to DataFrame for easy manipulation
    current_df = pd.DataFrame(current_results)
    previous_df = pd.DataFrame(previous_results)
    previous_df['points_previous'] = previous_df['points_current']
    previous_df.drop(columns=['points_current'], inplace=True)
    current_df.columns = ['participant_name', 'points_current']

    # Merge on participant name assuming uniqueness
    merged_df = pd.merge(current_df, previous_df, on='participant_name', how="left")
    merged_df.fillna(0, inplace=True)
    # Calculate the difference in points
    merged_df[today] = merged_df['points_current'] - merged_df['points_previous']
    merged_df.drop(columns=['points_previous'], inplace=True)
    # Select necessary columns
    # result_df = merged_df[['participant_name', 'points_increase']]

    return merged_df


def update_csv_file(daily_points, csv_filename='tournament_results.csv'):
    today = datetime.now().strftime('%Y-%m-%d')

    if not os.path.exists(csv_filename):
        # Initialize a new CSV with the header
        daily_points.to_csv(csv_filename, index=False, columns=['participant_name', today])
    else:
        # Append new data
        daily_points.fillna(0, inplace=True)  # Fill NaN values with 0 if new participants appear
        daily_points.to_csv(csv_filename, index=False)


if __name__ == '__main__':
    results_csv = sys.argv[1]
    competition_id = int(sys.argv[2])
    current_results = fetch_tournament_data(competition_id)
    # initialize_csv_file(initial_data, results_csv)
    previous_results = pd.read_csv(results_csv)
    daily_points = calculate_daily_points(current_results, previous_results)
    update_csv_file(daily_points, results_csv)
