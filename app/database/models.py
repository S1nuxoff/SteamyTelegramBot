from sqlalchemy import BigInteger, JSON, ForeignKey, Boolean, DateTime, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from config import DATABASE_URL

engine = create_async_engine(
    url=DATABASE_URL
)
async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True, nullable=False)
    steam_id: Mapped[str] = mapped_column(String, nullable=False)
    username: Mapped[str] = mapped_column(String, nullable=False)
    favorite: Mapped[list] = mapped_column(JSON, default=[])
    language: Mapped[int] = mapped_column(ForeignKey("languages.id"), nullable=False)
    currency: Mapped[int] = mapped_column(ForeignKey("currencies.id"), nullable=False)
    premium: Mapped[bool] = mapped_column(Boolean, default=False)
    state: Mapped[list] = mapped_column(JSON, default={})
    activity: Mapped[DateTime] = mapped_column(DateTime, nullable=True)  # Новое поле

class Game(Base):
    __tablename__ = "games"

    id: Mapped[int] = mapped_column(primary_key=True)
    steam_id: Mapped[int] = mapped_column()
    dmarket_id: Mapped[str] = mapped_column()
    name: Mapped[str] = mapped_column()


class Currency(Base):
    __tablename__ = "currencies"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    ratio: Mapped[float] = mapped_column()
    time: Mapped[str] = mapped_column()


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True)
    nameid: Mapped[int] = mapped_column()
    hash_name: Mapped[str] = mapped_column()
    game: Mapped[int] = mapped_column()


class Language(Base):
    __tablename__ = "languages"

    id: Mapped[int] = mapped_column(primary_key=True)
    language_code: Mapped[str] = mapped_column()
    name: Mapped[str] = mapped_column()


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
