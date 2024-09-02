import os


# Function to obtain a Bearer token (example implementation)
def get_bearer_token():
    # Replace with the actual logic to get your token
    return os.getenv("POLEMICA_BEARER")


import requests
import json
import time
from dataclasses import dataclass, field
from typing import List, Optional

# Define mappings for roles and results
ROLE_MAPPING = {
    0: 'don',
    1: 'mafia',
    2: 'peace',
    3: 'sheriff'
}

RESULT_MAPPING = {
    0: 'loss',
    1: 'win'
}


@dataclass
class Referee:
    id: int
    username: str
    region: Optional[str] = None
    city: Optional[str] = None
    avatar: Optional[str] = None


@dataclass
class Game:
    id: int
    started: str
    result: int
    scoringVersion: str
    scoringType: int
    updatedAt: str
    referee: Referee
    version: int
    tags: List[str]


@dataclass
class Player:
    position: int
    username: str
    avatar: Optional[str]
    role: int
    techs: int
    fouls: int
    player: int
    guess: Optional[dict] = None
    triple: Optional[int] = None


@dataclass
class Check:
    night: int
    role: int
    player: int


@dataclass
class Shot:
    night: int
    shooter: int
    victim: int


@dataclass
class Vote:
    day: int
    num: int
    voter: int
    candidate: int


@dataclass
class GameDetails:
    started: str
    id: int
    master: int
    referee: Referee
    scoringVersion: str
    scoringType: int
    tags: List[str]
    version: int
    players: List[Player]
    checks: List[Check]
    shots: List[Shot]
    votes: List[Vote]
    bonuses: List[dict]
    result: int


# Helper function to make a request with retries for 500 errors
def make_request_with_retries(url, headers, params=None, max_retries=3, delay=1):
    retries = 0
    response = {}
    while retries < max_retries:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code < 500:
            return response
        else:
            print(f"Error {response.status_code} encountered on {url}. Retrying {retries + 1}/{max_retries}...")
            retries += 1
            if retries >= max_retries:
                break
            time.sleep(delay)
            delay *= 2  # Exponential backoff

    # If max retries are reached, return the response
    return response


# Functions for making requests with Bearer token and retries
def fetch_games(club_id: int, offset=0, limit=50):
    token = get_bearer_token()
    url = f"https://app.polemicagame.com/v1/clubs/{club_id}/games"
    headers = {'Authorization': f'Bearer {token}'}
    params = {'offset': offset, 'limit': limit}
    response = make_request_with_retries(url, headers, params)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching games: {response.status_code}")
        return []


def fetch_game_details(club_id: int, game_id: int):
    token = get_bearer_token()
    url = f"https://app.polemicagame.com/v1/clubs/{club_id}/games/{game_id}"
    headers = {'Authorization': f'Bearer {token}'}
    response = make_request_with_retries(url, headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching game details: {response.status_code}")
        return {}


def save_games_and_details_to_json(club_id, games_filename='all_games.json', games_dir='games'):
    offset = 0
    limit = 50
    all_games = []

    if not os.path.exists(games_dir):
        os.makedirs(games_dir)

    while True:
        games = fetch_games(club_id, offset, limit)
        if not games:
            break

        all_games.extend(games)
        for game in games:
            game_id = game['id']
            game_details = fetch_game_details(club_id, game_id)

            if game_details != {}:
                # Save each game's details to a separate JSON file
                with open(f"{games_dir}/game_{game_id}.json", 'w', encoding='utf-8') as f:
                    json.dump(game_details, f, ensure_ascii=False, indent=4)

                # Print progress
                print(f"Fetched and saved details for game {game_id}")
                game["downloaded"] = True
            else:
                game["downloaded"] = False

            # Comply with rate limiting (1 request per second)
            time.sleep(1)

        offset += limit

        # Comply with rate limiting (1 request per second)
        time.sleep(1)

        # Print progress
        print(f"Fetched {offset} games so far...")

    # Save all fetched games to a JSON file (game summaries)
    with open(games_filename, 'w', encoding='utf-8') as f:
        json.dump(all_games, f, ensure_ascii=False, indent=4)

    print(f"All game summaries saved to {games_filename}. Individual game details saved to {games_dir} directory.")


# Example usage
if __name__ == "__main__":
    club_id = 72
    save_games_and_details_to_json(club_id)
