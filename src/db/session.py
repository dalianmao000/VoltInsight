"""数据库会话管理"""
import os
from contextlib import contextmanager
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from .models import Base

# 数据库 URL 配置
# 开发/测试环境使用 SQLite，生产环境使用 PostgreSQL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{Path(__file__).parent.parent.parent / 'data' / 'research_assistant.db'}"
)

# 创建引擎
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False,
    )
else:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db() -> None:
    """初始化数据库，创建所有表"""
    Base.metadata.create_all(bind=engine)

def get_db_session() -> Generator[Session, None, None]:
    """获取数据库会话的上下文管理器"""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

@contextmanager
def db_transaction() -> Generator[Session, None, None]:
    """带事务的数据库会话"""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()