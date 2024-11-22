import logging                                         # НЕ ЗАБЫТЬ УБРАТЬ ФАЙЛ С ТОКЕНАМИ ИЗ РЕПОЗИТОРИЯ
import requests
import time
from dotenv import load_dotenv
from telebot import TeleBot
from exceptions import (
    ErrorStatusCode,
    NotKeyHomeworks,
    NotKeyHomeworkName,
    NotKeyStatus,
    NotStatusInHomeworkVerdict,
)
from constants import (
    PRACTICUM_TOKEN,
    TELEGRAM_TOKEN,
    TELEGRAM_CHAT_ID,
    RETRY_PERIOD,
    ENDPOINT,
    HEADERS,
    HOMEWORK_VERDICTS,
)

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='homework.log',
    filemode='w'
)


def check_tokens():
    """Проверяет доступность токенов в окружении"""
    if PRACTICUM_TOKEN is not None and \
       TELEGRAM_TOKEN is not None and \
       TELEGRAM_CHAT_ID is not None:
        return True
    else:
        logging.critical('Отсутствие переменных окружения')
        return False


def send_message(bot, message):
    """Отправляет сообщение через бота в Телеграмм"""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logging.debug('Сообщение отправлено в Telegram: %s', message)
    except Exception as error:
        logging.error('ошибка при отправке сообщения в Telegram: %s', error)


def get_api_answer(timestamp):
    """Делает GET запрос к API Практикума домашки и"""
    """переводит его из типа json в тип python"""
    try:
        homework_status = requests.get(ENDPOINT, headers=HEADERS, params=timestamp)
    except requests.RequestException as e:
        print("Ошибка запроса:", e)
    if homework_status.status_code == 200:
        return homework_status.json()
    elif homework_status.status_code != 200:
        raise ErrorStatusCode('Ошибка кода страницы!')


def check_response(response):
    """Проверяет ответ от API на соответствие документации"""
    if isinstance(response, dict) is not True:
        raise TypeError('Ответ от API не в виде словаря')
    if 'homeworks' not in response:
        raise NotKeyHomeworks('Нет нужного ключа homeworks')
    if isinstance(response['homeworks'], list) is not True:
        raise TypeError('Ответ от API под ключём homeworks не в виде списка')


def parse_status(homework):
    """Извлекает из домашней работы, её статус"""
    if 'homework_name' in homework:
        homework_name = homework['homework_name']
    else:
        raise NotKeyHomeworkName('В ответе от API отсутствует ключ homework_name')
    if 'status' in homework:
        verdict = homework['status']
        if verdict in HOMEWORK_VERDICTS:
            verdict = HOMEWORK_VERDICTS[verdict]
            return f'Изменился статус проверки работы "{homework_name}". {verdict}'
        else:
            raise NotStatusInHomeworkVerdict('Нет статуса подходящего для документации')
    else:
        raise NotKeyStatus('В ответе от API отсутсвует ключ status')


#timestamp = int(time.time())
def main():
    """Основная логика работы бота."""
    bot = TeleBot(token=TELEGRAM_TOKEN)
    timestamp = 0
    time_marker = {'from_date': timestamp}
    old_tokens = check_tokens()
    if old_tokens is True:
        pass
    while True:
        old_tokens = check_tokens()
        if old_tokens is True:
            pass
        else:
            break
        homework_status = get_api_answer(time_marker)
        check_response(homework_status)
        print(homework_status)
        if len(homework_status['homeworks']) == 0:
            logging.debug('Получен пустой список домашних работ')
            time.sleep(RETRY_PERIOD)
            homework_status = get_api_answer(time_marker)
            continue
        # print(homework_status)
        #print(type(homework_status))
        #homework_status = homework_status
        #print(homework_status)
        # print(homework_status['homeworks'])
    # if len(homework_status['homeworks']) == 0:

        status_work = parse_status(homework_status['homeworks'][0])
        requests_from_the_api = requests.get(ENDPOINT, headers=HEADERS, params=time_marker)  # ДОДЕЛАТЬ ГЛАВНЫЙ СКРИПТ, УБРАТЬ ЛИШНЕЕ, СДЕЛАТЬ ЗАПРОСЫ ЧЕРЕЗ ФУНКЦИИ  !!!!!!
        response = requests_from_the_api.json()
        print(response)
        response = response['homeworks'][0]['status']
        # print(response)
        # print(type(response))
        #print(response.json())
        send_message(bot, status_work)

        try:
            status_tokens = check_tokens()
            if status_tokens is True:
                pass
            else:
                break
            new_request = requests.get(ENDPOINT, headers=HEADERS, params=time_marker) # ДОДЕЛАТЬ ГЛАВНЫЙ СКРИПТ, УБРАТЬ ЛИШНЕЕ, СДЕЛАТЬ ЗАПРОСЫ ЧЕРЕЗ ФУНКЦИИ  !!!!!
            new_response = new_request.json()
            new_response = new_response['homeworks'][0]['status']
            if response == new_response:
                time.sleep(RETRY_PERIOD)
            elif response != new_response:
                new_status_work = parse_status(new_response)
                send_message(bot, new_status_work)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            send_message(bot, message)


if __name__ == '__main__':
    main()
