from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Базовый класс для всех ORM-моделей. Модели импортируют и наследуются от него,
    чтобы их таблицы регистрировались в Base.metadata для Alembic autogenerate."""
