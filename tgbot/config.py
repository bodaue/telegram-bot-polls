from dataclasses import dataclass
from typing import Any

from environs import Env
from google.oauth2.service_account import Credentials


@dataclass
class DbConfig:
    host: str
    password: str
    user: str
    database: str
    port: int = 27017


@dataclass
class TgBot:
    token: str
    admin_ids: list[int]
    use_mongo_storage: bool


@dataclass
class Miscellaneous:
    scoped_credentials: Any = None


@dataclass
class Config:
    tg_bot: TgBot
    misc: Miscellaneous
    db: DbConfig = None


def get_scoped_credentials(credentials, scopes):
    def prepare_credentials():
        return credentials.with_scopes(scopes)

    return prepare_credentials


def load_config(path: str = None) -> Config:
    env = Env()
    env.read_env(path)

    scopes = [
        "https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
        "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"
    ]
    google_credentials = Credentials.from_service_account_file('tgbot/config-google.json')
    scoped_credentials = get_scoped_credentials(google_credentials, scopes)

    return Config(
        tg_bot=TgBot(
            token=env.str("BOT_TOKEN"),
            admin_ids=env.list('ADMINS', subcast=int),
            use_mongo_storage=env.bool("USE_MONGO_STORAGE")
        ),

        # db=DbConfig(
        #     host=env.str('DB_HOST'),
        #     password=env.str('POSTGRES_PASSWORD'),
        #     user=env.str('POSTGRES_USER'),
        #     database=env.str('POSTGRES_DB'),
        # ),

        misc=Miscellaneous(
            scoped_credentials=scoped_credentials
        )
    )
