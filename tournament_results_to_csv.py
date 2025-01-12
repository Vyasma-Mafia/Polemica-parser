import json
import csv

import requests

def main():
    data = requests.get('https://app.polemicagame.com/v1/competitions/2695/metrics?scoringType=1').json()
    print(data)
    # Открываем CSV-файл для записи
    with open('output.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        # Записываем заголовки колонок
        writer.writerow(['id', 'username', 'totalScores'])

        # Обрабатываем каждого участника
        for participant in data:
            participant_id = participant['id']
            username = participant['username']
            total_scores = 0
            metrics = participant['metrics']

            # Суммируем totalScores по всем ролям
            for role in ['don', 'maf', 'com', 'civ']:
                role_metrics = metrics.get(role, {})
                total_scores += role_metrics.get('totalScores', 0)

            # Записываем данные в CSV-файл
            writer.writerow([participant_id, username, total_scores])

if __name__ == '__main__':
    main()