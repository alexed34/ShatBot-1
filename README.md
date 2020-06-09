## Чат-бот Telegram 

### Описание

Чат-бот оповещает в Telegram о проверенном задании на учебном ресурсе [dewman.](https://dvmn.org/)

После запуска скрипт работает в постоянном режиме, отправляя запрос на сайт Devman каждые 90 сек. При получении ответа о проверенных задачах отправляет сообщение в Telegram c результатом проверки.

### Установка

* Скачайт cкрипт с [Git](https://github.com/alexed34/ShatBot-1)
* Создайте виртуальное окружение
* Скопирйте скрипт в папку с виртуальным окружением
* Установите зависимости командой в консоле `pip install -r requirements.txt`

Дла работы вам понадобятся следующие токены-ключи:
* Токен от Devman, находится [здесь](https://dvmn.org/api/docs/), зайдите на сайт под своим логином. Выглядит `5d75305cc9d51234564faed3d17ac4b984f90438`
* Токен Telegram -бота. [Как зарегестрировать?](https://habr.com/ru/post/262247/). Выглядит `1112345652:AAG2poqo-2M-5yertqAG5ZADkILY3VjVTJ4`
* Ваш chat-id в Telegram. [Как узнать?](https://telegram-rus.ru/id). Выглядит `236542263`

### Запуск скрипта
Перейдите в папку с установленным скриптом.

Скрипт запускается командой `main.py` в консоли.

Токены необходимо указать в команде на запуск. 

Пример команды `main.py -d 5d75305cc9d51234564faed3d17ac4b984f90438
 -t 1112345652:AAG2poqo-2M-5yertqAG5ZADkILY3VjVTJ4 -c 236542263`
 
Расшифровка команды запуска:
* команда `main.py` - указывает какой файл надо запустить
* команда `-d` или `--devman` -указывает что надо передать токен devman, пришется команда затем через пробел ваш токен, пример: `-d 5d75305cc9d51234564faed3d17ac4b984f90438 `
* команда `-t` или `--telegram` -указывает что надо передать токен Telegram, пришется команда затем через пробел ваш токен, пример: `-t 1112345652:AAG2poqo-2M-5yertqAG5ZADkILY3VjVTJ4`
* команда `-с` или `--chat` -указывает что надо передать токен chat_id telegram, пришется команда затем через пробел ваш токен, пример: `-c 236542263`

После запуска вы увидите в консоле сообщение 

`Дата запуска - __main__ -  58 - INFO - ________Отправляем запрос сайту_________`

Каждые 90 секунд будут появлятся сообщения подтверждающие правильную работу скрипта

```
2020-06-06 12:30:36,755 - __main__ -  30 - INFO - Ответ сервера: 200
2020-06-06 12:30:36,760 - __main__ -  60 - INFO - Проверяем json 
2020-06-06 12:30:36,760 - __main__ -  62 - INFO - получен ответ: "status = timeout" проверенных работ нет 
2020-06-06 12:30:36,760 - __main__ -  58 - INFO - ________Отправляем запрос сайту_________
```

### Сохраняем токены 
Для того что бы не вводить постоянно токены в командной строке их можно сохранить в скрипте.

Создайте рядом с файлом `main.py` файл `.env`

Запишите в файл `.env` ваши токены в таком формате

```
DEVMAN_TOKEN=5d75305cc9d51234564faed3d17ac4b984f90438
TELEGRAM_TOKEN=1112345652:AAG2poqo-2M-5yertqAG5ZADkILY3VjVTJ4
TG_CHAT_ID=236542263
```
Теперь скрипт запускается командой `main.py` без передачи токенов
