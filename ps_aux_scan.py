from subprocess import PIPE, Popen
from datetime import datetime

# выполняем команду и получаем результат
result = Popen(['ps', 'aux'], stdout=PIPE)
res = []
count_line = 0

# проходим построчно по результату и формируем список словарей
while True:
    line = result.stdout.readline().decode('utf-8')
    if not line:
        break
    if count_line > 0:
        line_lst = line.split()
        count = 0
        command_lst = []
        for command in line_lst:
            if count < 11:
                command_lst.append(command)
                count += 1
            else:
                command_lst[count-1] += ' ' + command
        res.append({"USER": command_lst[0], "PID": command_lst[1], "%CPU": command_lst[2], "%MEM": command_lst[3],
                    "VSZ": command_lst[4], "RSS": command_lst[5], "TTY": command_lst[6], "STAT": command_lst[7],
                    "START": command_lst[8], "TIME": command_lst[9], "COMMAND": command_lst[10]})
    count_line += 1

# получаем список уникальных пользователей
users = list(set([x['USER'] for x in res]))

# вычисляем количество процессов в системе (-1: т.к. первая строка является заголовком)
run_process = count_line - 1

# считаем количество процессов для каждого юзера
users_process = {}
for user in users:
    count_process = len([x for x in res if x['USER'] == user])
    users_process.update({user: count_process})

# вычисляем общее значение занимаемой памяти
all_mem = '{:.2f}'.format(sum([float(x['%MEM']) for x in res]))

# вычисляем общее значение занимаемого процессора
all_cpu = '{:.2f}'.format(sum([float(x['%CPU']) for x in res]))

# вычисляем процесс занимающий максимальный объем памяти
max_mem = [i['COMMAND'] for i in res if float(i['%MEM']) == max([float(x['%MEM']) for x in res])][0][:20]

# вычисляем процесс занимающий больше всех процессорного времени
max_proc = [i['COMMAND'] for i in res if float(i['%CPU']) == max([float(x['%CPU']) for x in res])][0][:20]

# производим вывод результатов
print(f'Пользователи системы: {users}')
print(f'Процессов запущено: {run_process}')
print(f'Пользовательских процессов: {users_process}')
print(f'Всего памяти используется: {all_mem}')
print(f'Всего CPU используется: {all_cpu}')
print(f'Больше всего памяти использует: {max_mem}')
print(f'Больше всего CPU использует: {max_proc}')


# сохраняем результаты в файл
now = datetime.now().__format__('%d_%m_%Y_%H_%M_%S')
f = open(f'{now}_scan.txt', 'w')
f.write(f'Пользователи системы: {users} \n')
f.write(f'Процессов запущено: {run_process} \n')
f.write(f'Пользовательских процессов: {users_process} \n')
f.write(f'Всего памяти используется: {all_mem} \n')
f.write(f'Всего CPU используется: {all_cpu} \n')
f.write(f'Больше всего памяти использует: {max_mem} \n')
f.write(f'Больше всего CPU использует: {max_proc} \n')
f.close()
