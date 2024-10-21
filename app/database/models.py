from sqlalchemy import BigInteger, JSON, ForeignKey, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

# engine = create_async_engine(url="sqlite+aiosqlite:///db.sqlite3")
engine = create_async_engine(
    url="postgresql+asyncpg://steamy:Afynjv228@185.93.6.180:5432/steamy_db"
)
async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger)
    steam_id: Mapped[str] = mapped_column()
    username: Mapped[str] = mapped_column()
    favorite: Mapped[list] = mapped_column(JSON)
    language: Mapped[int] = mapped_column(ForeignKey("languages.id"))
    currency: Mapped[int] = mapped_column(ForeignKey("currencies.id"))
    premium: Mapped[bool] = mapped_column(Boolean)
    state: Mapped[list] = mapped_column(JSON)


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
