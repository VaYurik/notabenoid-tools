## Скрипты для работы с сайтом распределённых переводов Notabenoid.org

### Установка:
1. Качаем, ставим ~~и душим~~ [Питона](https://www.python.org/downloads/) для вашей ОС. Обращаю внимание, что под Windows 7 последняя версия - 3.8, а в Linux он, скорее всего, уже установлен.
2. На всякий случай запускаем командную строку/терминал и вводим: pip install requests

### Скрипты:
export_chapter.py - *скрипт для экспорта отдельно взятой главы перевода с сайта Notabenoid.org*

backup_project.py - *скрипт для экспорта проекта перевода с сайта Notabenoid.org*

search_string.py - *скрипт поиска подстроки во всех главах проекта перевода с сайта Notabenoid.org*

### Пример запуска:
`python export_chapter.py http://notabenoid.org/book/60225/283468 ваш_логин ваш_пароль`

`python backup_project.py http://notabenoid.org/book/78978 ваш_логин ваш_пароль`

`python search_string.py http://notabenoid.org/book/73676 "большие сиськи" t ваш_логин ваш_пароль`
