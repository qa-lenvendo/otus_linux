import argparse
import json
import os
import re
from collections import defaultdict
from datetime import datetime

# формируем параметры запуска скрипта
parser = argparse.ArgumentParser()
parser.add_argument('-f', dest='file', action='store', help='Путь до файла или директории', default='./logs/')
args = parser.parse_args()

# формируем базовый словарь для получения результатов
result_dict = defaultdict(
    lambda: {
        'top_ips': {},
        'top_longest': [],
        'total_stat': {
            'GET': 0,
            'HEAD': 0,
            'POST': 0,
            'PUT': 0,
            'DELETE': 0,
            'CONNECT': 0,
            'OPTIONS': 0,
            'TRACE': 0
        },
        'total_requests': 0
    }
)


def statistic(file_path, filename):
    with open(os.path.join(file_path, filename)) as file:
        for line in file:
            # ищем и считаем методы
            method = re.search(r"\] \"(GET|HEAD|POST|PUT|DELETE|CONNECT|OPTIONS|TRACE)", line)
            if method is not None:
                result_dict[filename]['total_stat'][method.group(1)] += 1
            # считаем общее количество запросов
            result_dict[filename]['total_requests'] += 1
            # считаем количество ip адресов
            ip_math = re.search(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", line)
            if ip_math is not None:
                ip = ip_math.group()
                if ip not in result_dict[filename]['top_ips']:
                    result_dict[filename]['top_ips'].update({ip: 0})
                result_dict[filename]['top_ips'][ip] += 1

            # извлекаем дату запроса
            date_math = re.search(r"\[.*\]", line)
            if date_math is not None:
                date = date_math.group()

            # извлекаем url запроса
            url_math = re.search(r"\d \"(.*?)\" ", line)
            if url_math is not None:
                url = url_math.group(1)

            # извлекаем длительность запроса
            duration_math = re.search(r"\" (\d*)$", line)
            if duration_math is not None:
                duration = duration_math.group(1)

            # формируем словарь для топа по длительности
            result_dict[filename]['top_longest'].append(
                {
                    'ip': ip,
                    'date': date,
                    'method': method.group(1),
                    'url': url,
                    'duration': duration
                })

        # сортируем значения для топа по длительности и оставляем 3 значения
        longest_sorted = sorted(result_dict[filename]['top_longest'], key=lambda k_v: k_v['duration'], reverse=True)[:3]
        # сортируем словарь с количеством ip и оставляем 3 значения
        ips_sorted = sorted(result_dict[filename]['top_ips'].items(), key=lambda k_v: k_v[1], reverse=True)[:3]
        # обновляем базовый словарь с результатами
        result_dict[filename]['top_longest'].clear()
        result_dict[filename]['top_longest'].extend(longest_sorted)
        result_dict[filename]['top_ips'].clear()
        result_dict[filename]['top_ips'].update(ips_sorted)
    return result_dict


# выполнение сбора статистики в зависимости от типа переданного аргумента
if os.path.isdir(args.file):
    path = os.path.dirname(args.file)
    result = {}
    for name in os.listdir(path):
        result = statistic(path, name)
else:
    result = statistic(os.path.dirname(args.file), os.path.basename(args.file))

# вывод результатов на экран
print(json.dumps(result, indent=4))
# запись результатов в файл
file = open(f'result_{datetime.now()}', 'w')
file.write(str(json.dumps(result, indent=4)))
file.close()
