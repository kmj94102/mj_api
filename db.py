from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session


user_name = "root"
user_pwd = "minjaedb"
db_host = "svc.sel3.cloudtype.app:31508"
db_name = "pokemonDB"

DATABASE = f"mysql+pymysql://{user_name}:{user_pwd}@{db_host}/{db_name}?charset=utf8"

ENGINE = create_engine(
    DATABASE,
    pool_pre_ping=True,
    pool_recycle=3600,
    encoding="utf-8",
    echo=True
)

session = scoped_session(
    sessionmaker(
        autocommit=False,
        autoflush=True,
        bind=ENGINE
    )
)

Base = declarative_base()
Base.query = session.query_property()