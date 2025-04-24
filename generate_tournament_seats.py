import json
import os
from datetime import datetime
from random import shuffle

import requests
import random

from crawler import get_bearer_token

POLEMICA_USERNAME = os.getenv("POLEMICA_USERNAME")
POLEMICA_PASSWORD = os.getenv("POLEMICA_PASSWORD")

random.seed(42)
token = get_bearer_token()
headers = {'Authorization': f'Bearer {token}'}
baseurl = "https://app.polemicagame.com/v1"
competition_id = "3350"
members_url = baseurl + "/competitions/" + competition_id + "/members"
teams_url = baseurl + "/competitions/" + competition_id + "/teams"
games_url = baseurl + "/competitions/" + competition_id + "/games"
admins_url = baseurl + "/competitions/" + competition_id + "/admins"
tour_games_dir = "tour_games"
seats = {1: {1: {1: 22, 2: 3, 3: 7, 4: 45, 5: 19, 6: 27, 7: 14, 8: 30, 9: 34, 10: 1},
             2: {1: 48, 2: 12, 3: 28, 4: 17, 5: 2, 6: 40, 7: 9, 8: 31, 9: 36, 10: 5},
             3: {1: 0, 2: 35, 3: 47, 4: 23, 5: 24, 6: 43, 7: 8, 8: 18, 9: 16, 10: 10},
             4: {1: 38, 2: 25, 3: 6, 4: 29, 5: 44, 6: 41, 7: 32, 8: 46, 9: 11, 10: 13},
             5: {1: 37, 2: 21, 3: 42, 4: 33, 5: 4, 6: 39, 7: 26, 8: 15, 9: 49, 10: 20}},
         2: {1: {1: 45, 2: 15, 3: 43, 4: 5, 5: 28, 6: 19, 7: 32, 8: 7, 9: 22, 10: 34},
             2: {1: 12, 2: 26, 3: 47, 4: 42, 5: 6, 6: 2, 7: 38, 8: 16, 9: 20, 10: 30},
             3: {1: 39, 2: 17, 3: 24, 4: 33, 5: 48, 6: 46, 7: 3, 8: 37, 9: 27, 10: 11},
             4: {1: 1, 2: 41, 3: 23, 4: 35, 5: 29, 6: 49, 7: 36, 8: 9, 9: 13, 10: 18},
             5: {1: 21, 2: 40, 3: 0, 4: 31, 5: 4, 6: 44, 7: 25, 8: 10, 9: 8, 10: 14}},
         3: {1: {1: 18, 2: 42, 3: 32, 4: 9, 5: 27, 6: 40, 7: 38, 8: 7, 9: 1, 10: 35},
             2: {1: 33, 2: 4, 3: 16, 4: 26, 5: 45, 6: 41, 7: 28, 8: 2, 9: 6, 10: 21},
             3: {1: 47, 2: 15, 3: 48, 4: 20, 5: 39, 6: 13, 7: 11, 8: 22, 9: 31, 10: 24},
             4: {1: 43, 2: 23, 3: 37, 4: 19, 5: 14, 6: 3, 7: 10, 8: 8, 9: 30, 10: 29},
             5: {1: 49, 2: 12, 3: 25, 4: 34, 5: 17, 6: 44, 7: 46, 8: 36, 9: 5, 10: 0}},
         4: {1: {1: 19, 2: 21, 3: 28, 4: 24, 5: 0, 6: 30, 7: 10, 8: 17, 9: 41, 10: 45},
             2: {1: 39, 2: 46, 3: 22, 4: 5, 5: 1, 6: 8, 7: 43, 8: 27, 9: 25, 10: 35},
             3: {1: 42, 2: 49, 3: 6, 4: 9, 5: 29, 6: 31, 7: 37, 8: 12, 9: 18, 10: 26},
             4: {1: 11, 2: 33, 3: 14, 4: 47, 5: 15, 6: 36, 7: 2, 8: 4, 9: 44, 10: 7},
             5: {1: 16, 2: 40, 3: 32, 4: 34, 5: 38, 6: 13, 7: 48, 8: 20, 9: 23, 10: 3}},
         5: {1: {1: 26, 2: 30, 3: 15, 4: 13, 5: 35, 6: 3, 7: 37, 8: 19, 9: 44, 10: 28},
             2: {1: 22, 2: 25, 3: 34, 4: 36, 5: 47, 6: 42, 7: 29, 8: 2, 9: 40, 10: 10},
             3: {1: 12, 2: 49, 3: 8, 4: 45, 5: 33, 6: 20, 7: 0, 8: 24, 9: 32, 10: 27},
             4: {1: 41, 2: 18, 3: 46, 4: 7, 5: 31, 6: 1, 7: 5, 8: 11, 9: 21, 10: 16},
             5: {1: 48, 2: 9, 3: 17, 4: 39, 5: 43, 6: 38, 7: 4, 8: 23, 9: 14, 10: 6}},
         6: {1: {1: 24, 2: 19, 3: 38, 4: 49, 5: 46, 6: 33, 7: 2, 8: 9, 9: 7, 10: 4},
             2: {1: 34, 2: 5, 3: 27, 4: 41, 5: 10, 6: 15, 7: 12, 8: 0, 9: 32, 10: 23},
             3: {1: 6, 2: 37, 3: 45, 4: 35, 5: 44, 6: 20, 7: 31, 8: 29, 9: 22, 10: 14},
             4: {1: 30, 2: 43, 3: 17, 4: 8, 5: 39, 6: 47, 7: 21, 8: 26, 9: 48, 10: 1},
             5: {1: 13, 2: 42, 3: 40, 4: 28, 5: 36, 6: 25, 7: 16, 8: 3, 9: 11, 10: 18}},
         7: {1: {1: 29, 2: 44, 3: 49, 4: 38, 5: 45, 6: 39, 7: 17, 8: 23, 9: 3, 10: 32},
             2: {1: 46, 2: 18, 3: 48, 4: 27, 5: 10, 6: 15, 7: 24, 8: 6, 9: 14, 10: 4},
             3: {1: 43, 2: 47, 3: 40, 4: 37, 5: 20, 6: 34, 7: 13, 8: 22, 9: 0, 10: 9},
             4: {1: 36, 2: 16, 3: 2, 4: 19, 5: 8, 6: 33, 7: 12, 8: 25, 9: 5, 10: 31},
             5: {1: 41, 2: 28, 3: 11, 4: 1, 5: 21, 6: 35, 7: 30, 8: 26, 9: 7, 10: 42}},
         8: {1: {1: 21, 2: 45, 3: 8, 4: 2, 5: 33, 6: 43, 7: 3, 8: 31, 9: 49, 10: 13},
             2: {1: 7, 2: 36, 3: 10, 4: 44, 5: 47, 6: 32, 7: 18, 8: 28, 9: 17, 10: 39},
             3: {1: 9, 2: 23, 3: 37, 4: 16, 5: 35, 6: 5, 7: 6, 8: 14, 9: 25, 10: 48},
             4: {1: 42, 2: 29, 3: 19, 4: 41, 5: 34, 6: 1, 7: 11, 8: 12, 9: 4, 10: 24},
             5: {1: 40, 2: 27, 3: 30, 4: 20, 5: 46, 6: 26, 7: 22, 8: 0, 9: 15, 10: 38}},
         9: {1: {1: 13, 2: 38, 3: 4, 4: 0, 5: 22, 6: 27, 7: 44, 8: 6, 9: 18, 10: 47},
             2: {1: 31, 2: 43, 3: 26, 4: 46, 5: 3, 6: 10, 7: 35, 8: 19, 9: 15, 10: 2},
             3: {1: 14, 2: 7, 3: 42, 4: 32, 5: 37, 6: 49, 7: 40, 8: 28, 9: 45, 10: 25},
             4: {1: 16, 2: 34, 3: 36, 4: 39, 5: 24, 6: 9, 7: 21, 8: 29, 9: 1, 10: 12},
             5: {1: 17, 2: 8, 3: 20, 4: 48, 5: 41, 6: 11, 7: 23, 8: 33, 9: 30, 10: 5}},
         10: {1: {1: 33, 2: 28, 3: 39, 4: 22, 5: 38, 6: 0, 7: 9, 8: 3, 9: 26, 10: 16},
              2: {1: 31, 2: 41, 3: 45, 4: 25, 5: 49, 6: 23, 7: 7, 8: 13, 9: 4, 10: 19},
              3: {1: 47, 2: 24, 3: 27, 4: 37, 5: 12, 6: 11, 7: 35, 8: 43, 9: 40, 10: 17},
              4: {1: 8, 2: 34, 3: 14, 4: 46, 5: 32, 6: 42, 7: 18, 8: 15, 9: 2, 10: 29},
              5: {1: 44, 2: 10, 3: 5, 4: 30, 5: 36, 6: 48, 7: 6, 8: 1, 9: 21, 10: 20}},
         11: {1: {1: 26, 2: 44, 3: 20, 4: 21, 5: 32, 6: 9, 7: 16, 8: 46, 9: 12, 10: 7},
              2: {1: 0, 2: 35, 3: 3, 4: 40, 5: 15, 6: 8, 7: 29, 8: 49, 9: 24, 10: 47},
              3: {1: 27, 2: 48, 3: 33, 4: 38, 5: 42, 6: 10, 7: 14, 8: 41, 9: 31, 10: 19},
              4: {1: 18, 2: 39, 3: 1, 4: 25, 5: 11, 6: 30, 7: 45, 8: 5, 9: 23, 10: 36},
              5: {1: 34, 2: 22, 3: 13, 4: 43, 5: 17, 6: 4, 7: 28, 8: 37, 9: 6, 10: 2}},
         12: {1: {1: 8, 2: 36, 3: 44, 4: 32, 5: 27, 6: 24, 7: 22, 8: 16, 9: 3, 10: 9},
              2: {1: 2, 2: 38, 3: 49, 4: 47, 5: 5, 6: 14, 7: 30, 8: 11, 9: 43, 10: 21},
              3: {1: 46, 2: 48, 3: 39, 4: 42, 5: 19, 6: 35, 7: 4, 8: 1, 9: 12, 10: 28},
              4: {1: 25, 2: 6, 3: 33, 4: 10, 5: 40, 6: 37, 7: 20, 8: 45, 9: 13, 10: 15},
              5: {1: 29, 2: 17, 3: 34, 4: 23, 5: 18, 6: 7, 7: 0, 8: 41, 9: 26, 10: 31}},
         13: {1: {1: 44, 2: 33, 3: 22, 4: 30, 5: 49, 6: 37, 7: 5, 8: 10, 9: 16, 10: 40},
              2: {1: 15, 2: 6, 3: 0, 4: 18, 5: 28, 6: 12, 7: 26, 8: 48, 9: 34, 10: 3},
              3: {1: 38, 2: 46, 3: 9, 4: 8, 5: 31, 6: 24, 7: 19, 8: 21, 9: 41, 10: 17},
              4: {1: 4, 2: 47, 3: 1, 4: 14, 5: 43, 6: 32, 7: 23, 8: 27, 9: 20, 10: 25},
              5: {1: 35, 2: 39, 3: 36, 4: 2, 5: 42, 6: 45, 7: 7, 8: 13, 9: 29, 10: 11}},
         14: {1: {1: 28, 2: 32, 3: 25, 4: 18, 5: 12, 6: 4, 7: 8, 8: 39, 9: 9, 10: 22},
              2: {1: 19, 2: 45, 3: 35, 4: 49, 5: 30, 6: 16, 7: 36, 8: 21, 9: 0, 10: 6},
              3: {1: 23, 2: 31, 3: 44, 4: 11, 5: 40, 6: 14, 7: 27, 8: 34, 9: 47, 10: 26},
              4: {1: 7, 2: 29, 3: 43, 4: 13, 5: 1, 6: 38, 7: 20, 8: 5, 9: 24, 10: 15},
              5: {1: 3, 2: 10, 3: 41, 4: 48, 5: 37, 6: 46, 7: 33, 8: 17, 9: 2, 10: 42}},
         15: {1: {1: 17, 2: 13, 3: 7, 4: 21, 5: 3, 6: 25, 7: 31, 8: 20, 9: 27, 10: 0},
              2: {1: 49, 2: 37, 3: 11, 4: 16, 5: 34, 6: 28, 7: 1, 8: 14, 9: 46, 10: 23},
              3: {1: 32, 2: 5, 3: 19, 4: 44, 5: 9, 6: 6, 7: 15, 8: 47, 9: 39, 10: 33},
              4: {1: 45, 2: 8, 3: 26, 4: 40, 5: 48, 6: 36, 7: 42, 8: 4, 9: 29, 10: 22},
              5: {1: 35, 2: 30, 3: 38, 4: 43, 5: 41, 6: 2, 7: 24, 8: 18, 9: 10, 10: 12}}}


def authorize():
    global token, headers
    token = requests.post(baseurl + "/auth/login",
                          data={"username": POLEMICA_USERNAME, "password": POLEMICA_PASSWORD}).json()["access_token"]
    headers = {'Authorization': f'Bearer {token}'}


def crawl_games():
    games = requests.get(games_url, headers=headers).json()
    for game_id in games:
        game = requests.get(games_url + "/" + str(game_id["id"]) + "?version=4", headers=headers).json()
        game_num = game["num"]
        table_num = game["table"]
        with open(f"{tour_games_dir}/{game_num}_{table_num}.json", 'w', encoding='utf-8') as f:
            json.dump(game, f, ensure_ascii=False, indent=4)


def print_members():
    players = get_members()
    # print(list(map(lambda it: it['player']['id'], members)))
    for i, (id, username) in zip(range(len(players)), players):
        print(i, id, username)


def get_members():
    players = []
    members = requests.get(members_url, headers=headers).json()
    teams = requests.get(teams_url, headers=headers).json()
    for team in teams:
        for member in team["members"]:
            players.append((member['id'], member['username']))
    for member in members:
        if (member['player']['id'], member['player']['username']) not in players:
            players.append((member['player']['id'], member['player']['username']))
    return players


def create_games():
    members = get_members()

    # val admins: Map<Long, PolemicaUser> =
    #             polemicaClient.getCompetitionAdmins(3359).associateBy { it.player.id }.mapValues { it.value.player }
    admins = requests.get(admins_url, headers=headers).json()
    admins = {admin['player']['id']: admin['player'] for admin in admins}
    admin_by_table_num = {
        1: 13421,
        2: 18211,
        3: 8368,
        4: 60517,
        5: 50230
    }
    for game_num in range(1, 16):
        for table_num in range(1, 6):
            players = list(map(lambda it: {
                "position": it,
                "username": members[seats[game_num][table_num][it]][1],
                "role": 2,
                "techs": [],
                "fouls": [],
                "guess": None,
                "player": {
                    "id": members[seats[game_num][table_num][it]][0],
                    "username": members[seats[game_num][table_num][it]][1]
                },
                "disqual": None,
                "award": None
            }, range(1, 11)))

            game = {
                "id": None,
                "master": admin_by_table_num[table_num],
                "referee": {
                    "id": admin_by_table_num[table_num],
                    "username": admins[admin_by_table_num[table_num]]["username"]
                },
                "scoringVersion": "3.0",
                "scoringType": 1,
                "version": 4,
                "zeroVoting": "respeech",
                "tags": None,
                "players": players,
                "checks": [],
                "shots": [],
                "stage": None,
                "votes": [],
                "comKiller": None,
                "bonuses": [],
                "started": datetime.now().isoformat(),
                "stop": None,
                "isLive": True,
                "result": None,
                "num": game_num,
                "table": table_num,
                "phase": 0,
                "factor": 1.0
            }
            res = requests.post(games_url, json=game, headers=headers)
            print(res.status_code, res.text)


def delete_games():
    games = requests.get(games_url, headers=headers).json()
    for game in games:
        if game.get("result", None) is not None:
            continue
        print("Delete", requests.delete(games_url + "/" + str(game["id"]), headers=headers))


def save_modified_games():
    members = requests.get(members_url, headers=headers).json()
    # random.shuffle(masters)
    for filename in os.listdir(tour_games_dir):
        if not filename.endswith('.json'):
            continue

        filepath = os.path.join(tour_games_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            game = json.load(f)
            if game.get("result", None) is not None:
                continue
            game_num = game["num"]
            table = game["table"]
            game["id"] = None
            game["isLive"] = True
            # master = masters[game_num - 1]
            # gameMembers = list(filter(lambda it: it["player"]["id"] != master, members))
            # random.shuffle(gameMembers)
            # for player in game["players"]:
            #     member = members[seats[game_num][table][player["position"]] - 1]
            #     player["player"] = {}
            #     player["player"]["id"] = member["player"]["id"]
            #     player["username"] = member["player"]["username"]
            # game["master"] = master
            # game["referee"]["id"] = master
            res = requests.post(games_url, json=game, headers=headers)
            print(res.status_code, res.text)


def save_modified_games_in_overlay_service():
    # Base URLs for your API
    # host = 'http://51.250.18.236:8090'  # Replace with your actual host
    host = 'http://localhost:8080'  # Replace with your actual host
    overlay_game_players_url = f'{host}/gamePlayers'
    overlay_games_url = f'{host}/games'
    headers = {
        'Content-Type': 'application/json'
    }
    for filename in os.listdir(tour_games_dir):
        if not filename.endswith('.json'):
            continue

        filepath = os.path.join(tour_games_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            game = json.load(f)
            game_num = game["num"]
            table = game["table"]
            game_id = game.get("id", None)
            # if game.get("result", None) is not None:
            #     continue

            players_urls = []  # List to collect player URLs
            for player in game["players"]:
                player_data = {
                    "nickname": player["username"],
                    "checks": [],  # Adjust this if you have actual check data
                    "guess": [],  # Adjust this if you have actual check data
                    "stat": {},  # Adjust this if you have actual stat data
                    "role": player.get("role", "red"),  # Default role to "red" if not provided
                    "place": player["position"],
                    "photoUrl": f'https://storage.yandexcloud.net/mafia-photos/{player["player"]["id"]}.jpg'
                }

                # Create the gamePlayer
                response = requests.post(overlay_game_players_url, headers=headers, json=player_data)
                if response.status_code == 201:  # HTTP 201 Created
                    player_response = response.json()
                    player_url = player_response['_links']['self']['href']
                    players_urls.append(player_url)
                else:
                    print(f"Failed to create gamePlayer for {player['username']}: {response.text}")
                    # Handle the error as needed, possibly exit or skip this player/game

            # After all players are created, create the game
            game_data = {
                "type": "POLEMICA",
                "tournamentId": competition_id,  # Replace with your actual tournament ID
                "tableNum": table,
                "gameNum": game_num,
                "players": players_urls
            }

            # Create the game
            response = requests.post(overlay_games_url, headers=headers, json=game_data)
            if response.status_code == 201:  # HTTP 201 Created
                game_response = response.json()
                print(f"Successfully created game {game_num} at table {table}")
            else:
                print(f"Failed to create game {game_num} at table {table}: {response.text}")
                # Handle the error as needed


def update_overlay_game_texts():
    games = requests.get("http://51.250.18.236:8090/games?size=500").json()["_embedded"]["games"]
    for game in games:
        if game["tournamentId"] != 3359:
            continue
        print(game)
        text = f"Aurora Cup | Стол {game['tableNum']} | Игра {game['gameNum']}"
        requests.patch(game["_links"]["self"]["href"], json={"text": text})


if __name__ == "__main__":
    authorize()
    print_members()
    # crawl_games()
    delete_games()
    create_games()
    # save_modified_games()
    # save_modified_games_in_overlay_service()
    # update_overlay_game_texts()
    # print(players)
