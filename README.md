# Homework Bot 🚀

💻 **Homework Bot** — это Telegram-бот для проверки статуса домашних работ на платформе Яндекс.Практикум.  

📁 Учебный проект, разработанный с использованием **Telegram API** и логирующий свою работу при помощи библиотеки `logging`.

---

## 🔍 Функционал

- Опрашивает **API Яндекс.Практикума** и проверяет статус домашней работы.  
- При изменении статуса анализирует ответ API и отправляет уведомление в **Telegram**.  
- Логирует свою работу с помощью `logging` и сообщает о критических ошибках в Telegram.  

---

## ⚙️ Установка и запуск

### 1. Установка и активация виртуального окружения  

- #### **Windows**  
Через bash:
```bash
python -m venv venv
source venv/Scripts/activate
```
- #### **MacOS/Linux**
```bash
python3 -m venv venv
source venv/bin/activate
```
- #### **Установка зависимостей из файла requirements.txt**
```bash
pip install -r requirements.txt
```
- #### **Запуск бота**
```bash
python homework.py
```
