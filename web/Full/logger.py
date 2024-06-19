import logging

log = logging

log.basicConfig(
    level=logging.INFO,  # Уровень логгирования INFO
    format='%(asctime)s - %(levelname)s - %(message)s'  # Формат сообщений
)