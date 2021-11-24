#
# Скрипт поиска подстроки во всех главах проекта перевода с сайта Notabenoid.org
# 
# Написан в рамках боевой операции по экстренному изучению ужасного языка программирования Python
#

import sys
import re
import requests

print('Searching a substring in the Notabenoid.org translation project')
print('Version 1.21')
print('http://vayurik.ru', end = '\n\n')

# Проверяем переданные параметры
if (len(sys.argv) != 6) \
  or (re.search(r'http\:\/\/(?:www\.)?notabenoid\.org\/book\/\d+', sys.argv[1], flags=re.IGNORECASE) is None) \
  or (sys.argv[3].lower() not in 'ot01') or (len(sys.argv[3]) > 1):
  print(f'  usage: {sys.argv[0]} <url> <substring> <type> <login> <password>')
  print('    <url>       - url of the Notabenoid translation project (http://notabenoid.org/book/xxxxx)')
  print('    <search>    - substring for search; if contain spaces, must be enclosed in quotes')
  print('    <type>      - type of search: "0" or "o" - search in originals, "1" or "t" - search in translations')
  print('    <login>     - login on Notabenoid.org')
  print('    <password>  - password on Notabenoid.org')
  print()
  exit()

#
# Параметры вроде верные, так что погнали!
#

url = sys.argv[1].lower()
search_string = sys.argv[2]
if sys.argv[3].lower() == 'o':
  search_type = 0
elif sys.argv[3].lower() == 't':
  search_type = 1
else:
  search_type = int(sys.argv[3])
login = sys.argv[4]
password = sys.argv[5]

# Функция выдачи сообщения об ошибке
def show_error(error_str):
  print('Error: ' + error_str, ' '*120)
  exit()

# Функция получения страницы
def get_page(chapter_link, cookies):
  try:
    response = requests.get(chapter_link, cookies=cookies)
  except:
    show_error(f'Incorrect url [{chapter_link}]')
  if response.status_code == 403:
    show_error(f'Access is denied [{response.status_code}]')
  elif response.status_code == 404:
    show_error(f'Page not found [{response.status_code}]')
  elif auth_response.status_code != 200:
    show_error(f'Incorrect connection [{auth_response.status_code}]')
  return response

# Авторизуемся на сайте
domain = re.search(r'(http\:\/\/(?:www\.)?notabenoid\.org)', url).group(1)
try:
  post_data = {'login[login]': login, 'login[pass]': password}
  auth_response = requests.post(domain, data = post_data)
except:
  show_error(f'Incorrect url [{domain}]')
if auth_response.status_code != 200:
  show_error(f'Incorrect connection [{auth_response.status_code}]')
if "{id: 0, login: 'anonymous'}" in auth_response.text:
  show_error('Incorrect login or password [401]')

# Получаем список глав
response = get_page(url, auth_response.cookies)
chapters = re.findall(r'<td class=\'t\'><a href=\'\/book\/\d+\/(\d+)\'>(.+?)<\/a><\/td>', response.text)
if not chapters:
  show_error(f'Can\'t get a list of chapters')

# Получаем название проекта
project_name = re.search(r'<h1>(.*?)<\/h1>', response.text).group(1)

chapter_num = 1
chapter_count = len(chapters)

print(f'Project URL:  {url}')
print(f'Substring:    "{search_string}"')
print(f'Search scope: ', end='')
print('translations') if search_type else print('originals') # если 1, то по переводам, если 0, то по переводам оригиналам
print(f'Username:     {login}')
print(f'Project name: {project_name}')
print(f'Chapters:     {chapter_count}')
print()

results = []

for chapter in chapters:
  percent = int(chapter_num / chapter_count * 100)
  print(f'Progress: {percent}% ({chapter_num}/{chapter_count})', end='\r')

  search_link = url + '/' + chapter[0] + '?show=' + str(search_type + 5);
  search_link += '&tt=' if search_type else '&to=' # если 1, то по переводам, если 0, то по переводам оригиналам
  search_link += search_string
  response = get_page(search_link, auth_response.cookies)
  if ('В этой части перевода отсутствует текст оригинала' not in response.text) \
    and ('Ничего не найдено' not in response.text):
      results.append([search_link, chapter[1]])
  chapter_num += 1


print('Search completed!', ' '*120, '\n')
print(f'Substring found in {len(results)} chapters')
for result in results:
  print(f'{result[1]}\t{result[0]}')
