import requests
import csv
import time
import os
from tqdm import tqdm

# API endpoint
url = "https://gomafia.pro/api/stats/get"

# Headers for the request
headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
}

# CSV file setup
csv_filename = "gomafia_win_streaks.csv"
checkpoint_filename = "checkpoint.txt"
csv_header = ["id", "login", "mafia_max_win_streak", "red_max_win_streak", "don_max_win_streak",
              "sheriff_max_win_streak"]

# Total number of users to process
total_users = 10000
successful_count = 0

# Check if we have a checkpoint to resume from
start_id = 1
if os.path.exists(checkpoint_filename):
    with open(checkpoint_filename, 'r') as f:
        start_id = int(f.read().strip())
    print(f"Resuming from ID {start_id}")

# Open CSV in append mode if it exists, otherwise create it
file_mode = 'a' if os.path.exists(csv_filename) and start_id > 1 else 'w'
with open(csv_filename, file_mode, newline='', encoding='utf-8') as csvfile:
    csvwriter = csv.writer(csvfile)

    # Write header only if we're creating a new file
    if file_mode == 'w':
        csvwriter.writerow(csv_header)

    # Use tqdm to create a progress bar
    with tqdm(range(start_id, total_users + 1), desc="Processing users") as progress_bar:
        # Loop through user IDs
        for user_id in progress_bar:
            # Data for the POST request
            data = {
                'id': user_id,
                'period': 'all',
                'gameType': 'all',
                'tournamentType': 'all'
            }

            try:
                # Make the request
                response = requests.post(url, headers=headers, data=data)
                response_json = response.json()

                # Check if the response was successful
                if response_json.get("result") == "success":
                    user_data = response_json.get("data", {})
                    user = user_data.get("user", {})
                    stats = user_data.get("stats", {})
                    win_strike = stats.get("win_strike", {})

                    user_id_from_api = user.get("id")
                    login = user.get("login")

                    mafia_max = win_strike.get("mafia", {}).get("max", 0)
                    red_max = win_strike.get("red", {}).get("max", 0)
                    don_max = win_strike.get("don", {}).get("max", 0)
                    sheriff_max = win_strike.get("sheriff", {}).get("max", 0)

                    # Write the data to the CSV
                    csvwriter.writerow([user_id_from_api, login, mafia_max, red_max, don_max, sheriff_max])

                    successful_count += 1
                    progress_bar.set_postfix(success_rate=f"{successful_count / (user_id - start_id + 1) * 100:.1f}%",
                                             user=login)

                # Add a small delay to not overwhelm the server
                time.sleep(0.1)

            except Exception as e:
                progress_bar.write(f"Error processing user ID {user_id}: {e}")
                # Add a larger delay in case of an error
                time.sleep(1)

            # Update checkpoint every 100 users
            if user_id % 100 == 0:
                with open(checkpoint_filename, 'w') as f:
                    f.write(str(user_id + 1))
                # Flush the CSV to disk periodically
                csvfile.flush()

# Update the final checkpoint
with open(checkpoint_filename, 'w') as f:
    f.write(str(total_users + 1))

print(
    f"Data collection complete. {successful_count} users successfully processed out of {total_users - start_id + 1} attempted.")
print(f"Data has been written to {csv_filename}")
