import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Читаем строку подключения из переменных окружения
DATABASE_URL = os.getenv(
    "CONNECTION_STRING",
    "postgresql://postgres:1234@localhost:5432/app"
)

# Для SQLAlchemy нужен формат postgresql://user:password@host:port/database
# Преобразуем из формата .NET, если нужно
if DATABASE_URL.startswith("Host="):
    # Парсим строку формата .NET
    params = dict(item.split("=") for item in DATABASE_URL.split(";"))
    DATABASE_URL = f"postgresql://{params['Username']}:{params['Password']}@{params['Host']}:{params['Port']}/{params['Database']}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()