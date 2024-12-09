import json
from collections import defaultdict

import requests

from crawler import get_bearer_token


def main():
    url = "https://app.polemicagame.com/v1/competitions/2514"

    token = get_bearer_token()

    games = json.loads(requests.get(url + "/games", headers={'Authorization': f'Bearer {token}'}).text)

    games.sort(key=lambda x: x["num"])
    players = defaultdict(list)

    for game in games:
        full_game = json.loads(
            requests.get(url + "/games/" + str(game["id"]), headers={'Authorization': f'Bearer {token}'}).text)
        result = full_game["result"]
        if result is None:
            continue

        for player in full_game["players"]:
            score = 0
            if (player["role"] in [0, 1]) and result == 1:
                score = 1
            elif (player["role"] in [2, 3]) and result == 0:
                score = 1
            players[player["username"]].append(score + player.get("award", 0))

    for player, games in players.items():
        print(player, ",".join(map(str, games)), sep=",")

if __name__ == "__main__":
    main()