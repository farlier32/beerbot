import json

# Функция для обновления файла JSON с результатами голосования
def update_vote_results(user_id, beer_id, vote):
    with open('data/votes.json', 'r+', encoding='utf8') as f:
        vote_data = json.load(f)
        # Если пользователь уже голосовал за это пиво, обновите его голос
        if str(user_id) in vote_data and str(beer_id) in vote_data[str(user_id)]:
            vote_data[str(user_id)][str(beer_id)] = vote
        else:
            # Если пользователь еще не голосовал за это пиво, добавьте его голос
            if str(user_id) not in vote_data:
                vote_data[str(user_id)] = {}
            vote_data[str(user_id)][str(beer_id)] = vote

        # Перезаписываем файл с обновленными данными
        f.seek(0)
        json.dump(vote_data, f, ensure_ascii=False, indent=2)
        f.truncate()
