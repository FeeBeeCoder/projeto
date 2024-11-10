import os
from dotenv import load_dotenv

# Carregar as variáveis do .env
load_dotenv(".gitignore/.env")

# Acessar a senha do banco de dados
database_password = os.getenv("DATABASE_PASSWORD")


DB_CONFIG = {
    'MYSQL_HOST': '127.0.0.1',
    'MYSQL_USER': 'root',
    'MYSQL_PASSWORD': 'ECU73!#V',
    'MYSQL_DB': 'projetopi'
}
