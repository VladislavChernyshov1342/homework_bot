import logging
import requests
import time
from dotenv import load_dotenv
from telebot import TeleBot
from logger_homework import logger
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
)


def check_tokens():
    """Проверяет доступность токенов в окружении."""
    if PRACTICUM_TOKEN is not None and \
       TELEGRAM_TOKEN is not None and \
       TELEGRAM_CHAT_ID is not None:
        return True
    else:
        logger.critical('Отсутствие переменных окружения')
        return False


def send_message(bot, message):
    """Отправляет сообщение через бота в Телеграмм."""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logger.debug('Сообщение отправлено в Telegram: %s', message)
    except Exception as error:
        logger.error('ошибка при отправке сообщения в Telegram: %s', error)


def get_api_answer(timestamp):
    """Делает GET запрос к API Практикума домашки."""
    try:
        homework_status = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params=timestamp
        )
    except requests.RequestException as e:
        logger.error('Ошибка при запросу к эндпоинту')
        print("Ошибка запроса:", e)
    if homework_status.status_code == 200:
        return homework_status.json()
    elif homework_status.status_code != 200:
        logger.error('Ошибка доступа к странице')
        raise ErrorStatusCode('Ошибка кода страницы!')


def check_response(response):
    """Проверяет ответ от API на соответствие документации."""
    if isinstance(response, dict) is not True:
        raise TypeError('Ответ от API не в виде словаря')
    if 'homeworks' not in response:
        raise NotKeyHomeworks('Нет нужного ключа homeworks')
    if isinstance(response['homeworks'], list) is not True:
        raise TypeError('Ответ от API под ключём homeworks не в виде списка')


def parse_status(homework):
    """Извлекает из домашней работы, её статус."""
    if 'homework_name' in homework:
        homework_name = homework['homework_name']
    else:
        logger.error('Отсутствие ключа homework_name в API')
        raise NotKeyHomeworkName(
            'В ответе от API отсутствует ключ homework_name'
        )
    if 'status' in homework:
        verdict = homework['status']
        if verdict in HOMEWORK_VERDICTS:
            verdict = HOMEWORK_VERDICTS[verdict]
            return (
                f'Изменился статус проверки работы "{homework_name}".{verdict}'
            )
        else:
            logger.error(
                'Нет статуса домашней работы, который подходит по документации'
            )
            raise NotStatusInHomeworkVerdict(
                'Нет статуса подходящего для документации'
            )
    else:
        logger.error('В ответе API отсутствует ключ status')
        raise NotKeyStatus('В ответе от API отсутсвует ключ status')


def main():
    """Основная логика работы бота."""
    # Создаём объект бота.
    bot = TeleBot(token=TELEGRAM_TOKEN)
    timestamp = 0
    time_marker = {'from_date': timestamp}
    # Проверяем доступность переменных окружения.
    old_tokens = check_tokens()
    if old_tokens is True:
        pass
    # Запускаем бесконечный цикл.
    while True:
        old_tokens = check_tokens()
        if old_tokens is True:
            pass
        else:
            break
        # Делаем запрос на API и проверяем ответ.
        homework_status = get_api_answer(time_marker)
        check_response(homework_status)
        # Проверяем в API наличие домашних работ.
        # Если их нет, делаем передышку и через какое-то время запускаем цикл
        # заного, где снова проверяем наличие домашней работы.
        # Как только появится новая домашная работа, цикл пойдёт дальше вниз
        # по коду с текущим ответом от API.
        if len(homework_status['homeworks']) == 0:
            logger.debug('Получен пустой список домашних работ')
            time.sleep(RETRY_PERIOD)
            homework_status = get_api_answer(time_marker)
            continue
        status_work = parse_status(homework_status['homeworks'][0])
        send_message(bot, status_work)
        try:
            status_tokens = check_tokens()
            if status_tokens is True:
                pass
            else:
                break
            # Тут мы узнаём, появился ли у домашней работы новый статус за
            # счёт того что делаем новый запрос. Если в ответе от API пришёл
            # тот же статус, цикл начнётся заного и через 10 минут повторится
            # новый запрос к API где мы снова сравним новый статус со статусом
            # от запроса, который был сделан 10 минут спустя.
            time.sleep(RETRY_PERIOD)
            new_request = get_api_answer(time_marker)
            if homework_status['homeworks'][0]['status'] == \
                    new_request['homeworks'][0]['status']:
                logger.debug('В домашней работе отсутствует новый статус')
            elif homework_status['homeworks'][0]['status'] != \
                    new_request['homeworks'][0]['status']:
                new_status_work = parse_status(new_request)
                send_message(bot, new_status_work)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(message)
            send_message(bot, message)


if __name__ == '__main__':
    main()
