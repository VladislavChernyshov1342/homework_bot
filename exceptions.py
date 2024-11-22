class ErrorStatusCode(Exception):
    """Ошибка кода страницы"""
    pass


class NotKeyHomeworks(Exception):
    """Отсутствие нужного ключа homeworks"""
    pass


class NotKeyHomeworkName(Exception):
    """Отсутствие ключа в ответе API homework_name"""
    pass


class NotKeyStatus(Exception):
    """Отсутствие в API ключа status"""
    pass


class NotStatusInHomeworkVerdict(Exception):
    """Нет статута подходящего по документации"""
    pass
