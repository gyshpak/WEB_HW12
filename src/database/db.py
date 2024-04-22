import contextlib

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


DB_URL = "postgresql+asyncpg://postgres:567234@localhost:5432/hw12"


class DatabaseSessionManager:
    def __init__(self, url: str):
        self._engine: AsyncEngine | None = create_async_engine(url)
        self._session_maker: async_sessionmaker = async_sessionmaker(
            autoflush=False, autocommit=False, bind=self._engine
        )

    @contextlib.asynccontextmanager
    async def session(self):
        if self._session_maker is None:
            raise Exception("Session is not initialized")
        session = self._session_maker()
        try:
            yield session
        except Exception as err:
            print(err)
            try:
                await session.rollback()
            except Exception:
                print("ERR1")
        finally:
            try:
                await session.close()
            except Exception:
                print("ERR2")


sessionmanager = DatabaseSessionManager(DB_URL)


async def get_db():
    async with sessionmanager.session() as session:
        try:
            yield session
        except Exception:
            print("ERR3")
