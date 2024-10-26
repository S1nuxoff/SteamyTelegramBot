from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from backend.config import DATABASE_URL

engine = create_async_engine(
    url=DATABASE_URL
)
async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


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


