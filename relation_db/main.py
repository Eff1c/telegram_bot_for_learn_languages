from decouple import config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


engine = create_engine(config('DB_LINK'), echo=True)
Session = sessionmaker(bind=engine)
session = Session()

SECRET_KEY = config('SECRET_KEY')
BOT_TOKEN = config('BOT_TOKEN')