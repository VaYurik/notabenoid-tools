#
# Скрипт для экспорта проекта перевода с сайта Notabenoid.org
# 
# Написан в рамках боевой операции по экстренному изучению ужасного языка программирования Python
#

import sys
import re
import requests
import html
import zipfile

print('Creating a backup of the Notabenoid.org translation project')
print('Version 1.2')
print('http://vayurik.ru', end = '\n\n')

# Проверяем переданные параметры
if (len(sys.argv) != 4) \
  or (re.search(r'http\:\/\/(?:www\.)?notabenoid\.org\/book\/\d+', sys.argv[1], flags=re.IGNORECASE) is None):
  print(f'  usage: {sys.argv[0]} <url> <login> <password>')
  print('    <url>       - url of the Notabenoid translation project (http://notabenoid.org/book/xxxxx)')
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
  print('Error: ' + error_str)
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
match = re.search(r'<h1>(.*?)<\/h1>', response.text)
project_name =  match.group(1) if match else show_error(f'Can\'t get the project name')

# Получаем id проекта
match = re.search(r'.+\/(\d+)\/?', url)
project_id =  match.group(1) if match else show_error(f'Can\'t get the project ID')

# Создаём zip-архив
zip_file_name = project_id + '.zip'
try:
  zip_file = zipfile.ZipFile(zip_file_name, mode='w')
except:
  show_error(f'Can\'t create an archive {project_id}.zip')

chapter_num = 1
chapter_count = len(chapters)

print(f'Project URL:  {url}')
print(f'Username:     {login}')
print(f'Project name: {project_name}')
print(f'Chapters:     {chapter_count}')
print()

results = []

for chapter in chapters:
  chapter_text = ''
  percent = int(chapter_num / chapter_count * 100)
  print(f'Progress: {percent}% ({chapter_num}/{chapter_count})', end='\r')

# Получаем ссылку на главу
  chapter_link = url + '/' + chapter[0]

  response = get_page(chapter_link, auth_response.cookies)

# Получаем название главы
  match = re.search(r'<h1>.+?\: (.*?)<\/h1>', response.text)
  chapter_name = match.group(1) if match else show_error(f'This chapter is available only to translation moderators')

# Получаем количество страниц в главе
  match = re.search(r'>(\d{1,})<\/a><\/li><\/ul>', response.text)
  page_count = int(match.group(1)) if match else 1

  page_num = 1
  while (page_num <= page_count):
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
    zip_file.writestr(chapter_name + '.txt', chapter_text)
  except:
    show_error(f'Can\'t write to the archive {zip_file_name}')
  chapter_num += 1

try:
  zip_file.close()
except:
  show_error(f'Can\'t close archive {zip_file_name}')
print('Backup completed!\n')
print(f'File {zip_file_name} created')
