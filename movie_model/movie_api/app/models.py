from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy import Integer, String


class Base(DeclarativeBase):
    pass


class Movie(Base):
    __tablename__ = "movies"
    movie_index: Mapped[int] = mapped_column(primary_key=True, index=True)
    original_title: Mapped[str] = mapped_column(String(30))
    id: Mapped[int] = mapped_column(
        Integer
    )  # IMDB id used to retrieve artwork and other information
