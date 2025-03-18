import requests
import csv
from datetime import datetime, timedelta
from collections import defaultdict

base_url = 'https://app.polemicagame.com/v1/clubs/72/metrics'
params = {
    'tags': 'ChampionshipLeague'
}

start_date = datetime(2024, 9, 1)
end_date = datetime(2025, 3, 10)

# Таблица, где ключ - username, значение - словарь {'дата': баллы}
user_scores = defaultdict(lambda: defaultdict(float))

# Список дат, чтобы использовать в качестве "заголовков" столбцов
all_dates = []

# Цикл по каждому дню
current_date = start_date
while current_date <= end_date:
    date_str = current_date.strftime('%Y-%m-%d')
    all_dates.append(date_str)  # Добавляем дату в список

    # Форматируем дату для запросов
    params['startDate'] = current_date.strftime('%Y-%m-%dT00:00:00.000')
    params['endDate'] = (current_date + timedelta(days=1) - timedelta(milliseconds=1)).strftime('%Y-%m-%dT23:59:59.999')

    # Запрос данных
    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()
        day_has_scores = False  # Флаг для того, чтобы отследить, есть ли баллы за этот день

        # Обработка каждого пользователя в ответе
        for user in data:
            total_scores = round(sum(user['metrics'][role]['totalScores'] for role in user['metrics']), 2)
            total_games = round(sum(user['metrics'][role]['games'] for role in user['metrics']), 2)

            if total_games != 0:
                user_scores[user['username']][date_str] = total_scores
                day_has_scores = True

        # Если ни один пользователь не набрал баллы, удаляем дату из списка
        if not day_has_scores:
            all_dates.pop()
    else:
        print(f"Failed to get data for {date_str}")

    current_date += timedelta(days=1)

# Сохранение данных в CSV
csv_file = 'user_metrics_table.csv'

with open(csv_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    # Записываем заголовки (дату)
    writer.writerow(['Username'] + all_dates)

    for username, scores in user_scores.items():
        row = [username] + [scores.get(date, '') for date in all_dates]  # Ставим '' вместо 0
        writer.writerow(row)
