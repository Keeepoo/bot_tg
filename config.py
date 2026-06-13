import os

# Учётные данные для подключения к Telegram API
TELEGRAM_BOT_KEY = os.getenv("TELEGRAM_BOT_KEY", "ВАШ ТОКЕН")
SUPPORT_CHAT_ID =   # Идентификатор чата администрации зоопарка

# Альтернативные имена для импорта (для совместимости с переименованными файлами)
BOT_TOKEN = TELEGRAM_BOT_KEY
ADMIN_CHAT_ID = SUPPORT_CHAT_ID