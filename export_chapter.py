#
# Скрипт для экспорта главы проекта перевода с сайта Notabenoid.org
# 
# Написан в рамках боевой операции по экстренному изучению ужасного языка программирования Python
#

import sys
import re
import requests
import html

print('Exporting a chapter of the Notabenoid.org translation project')
print('Version 1.0')
print('http://vayurik.ru', end = '\n\n')

# Проверяем переданные параметры
if (len(sys.argv) != 4) \
  or (re.search(r'http\:\/\/(?:www\.)?notabenoid\.org\/book\/\d+\/\d+', sys.argv[1], flags=re.IGNORECASE) is None):
  print(f'  usage: {sys.argv[0]} <url> <login> <password>')
  print('    <url>       - url of the chapter of the Notabenoid translation project (http://notabenoid.org/book/xxxxxx/xxxxxx)')
  print('    <login>     - login on Notabenoid.org')
  print('    <password>  - password on Notabenoid.org')
  print()
  exit()

#
# Параметры вроде верные, так что погнали!
#

url = sys.argv[1].lower()
login = sys.argv[2]
password = sys.argv[3]

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

# Получаем название проекта и главы
response = get_page(url, auth_response.cookies)
match = re.search(r'<h1>.+?>(.+?)<\/a>\: (.*?)<\/h1>', response.text)
project_name =  match.group(1) if match else show_error(f'Can\'t get the project name')
chapter_name =  match.group(2) if match else show_error(f'This chapter is available only to translation moderators')

print(f'Project URL:  {url}')
print(f'Username:     {login}')
print(f'Project name: {project_name}')
print(f'Chapter:      {chapter_name}')
print()

results = []

chapter_text = ''

# Получаем ссылку на главу
chapter_link = url

response = get_page(chapter_link, auth_response.cookies)

# Получаем количество страниц в главе
match = re.search(r'>(\d{1,})<\/a><\/li><\/ul>', response.text)
page_count = int(match.group(1)) if match else 1

page_num = 1
while (page_num <= page_count):
  percent = int(page_num / page_count * 100)
  print(f'Progress: {percent}% ({page_num}/{page_count})', end='\r')

  if page_num > 1:
    response = get_page(chapter_link + '?Orig_page=' + str(page_num), auth_response.cookies)
  fragments = re.findall(r'<tr id=\'o([\d+]+)\'>([\S\s]*?)<\/tr>', response.text)
  for fragment in fragments:
    match = re.search(r'<td class=\'o\'><div><p class=\'text\'>([\S\s]*?)<\/p>', fragment[1])
    chapter_text += match.group(1) + '\n' if match else show_error(f'The text of original is available for registered users only')
    match = re.search(r'<div id=\'t.*?best.*?<p class=\'text\'>([\S\s]*?)<\/p>', fragment[1])
    if not match:
      match = re.search(r'<div id=\'t.*?<p class=\'text\'>([\S\s]*?)<\/p>', fragment[1])
    if match:
      chapter_text += match.group(1).replace('<br />', '') + '\n'
    chapter_text += '\n'
  page_num += 1

chapter_text = html.unescape(chapter_text).strip()
try:
  with open(chapter_name + '.txt', 'w') as f:
    f.write(chapter_text)
except:
  show_error(f'Can\'t write to the file {chapter_name}.txt')

print('Export completed!', ' '*120, '\n')
print(f'File {chapter_name}.txt created')
