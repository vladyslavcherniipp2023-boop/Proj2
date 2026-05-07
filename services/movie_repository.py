"""
Репозиторій фільмів — зберігання й пошук.
Персистентність: JSON-файл на диску.
"""
import json
import os
from typing import Optional

from models.movie import Movie


class MovieRepository:
    """
    Відповідає за зберігання, завантаження та базові CRUD-операції.
    Не знає нічого про UI або бізнес-правила — тільки дані.
    """

    def __init__(self, filepath: str = "movies.json"):
        self._filepath = filepath
        self._movies: list[Movie] = []
        self._next_id: int = 1
        self._load()

    # ---------- public API ----------

    def add(self, movie: Movie) -> Movie:
        movie.id = self._next_id
        self._next_id += 1
        self._movies.append(movie)
        self._save()
        return movie

    def update(self, movie: Movie) -> bool:
        for i, m in enumerate(self._movies):
            if m.id == movie.id:
                self._movies[i] = movie
                self._save()
                return True
        return False

    def delete(self, movie_id: int) -> bool:
        before = len(self._movies)
        self._movies = [m for m in self._movies if m.id != movie_id]
        if len(self._movies) < before:
            self._save()
            return True
        return False

    def get_by_id(self, movie_id: int) -> Optional[Movie]:
        for m in self._movies:
            if m.id == movie_id:
                return m
        return None

    def get_all(self) -> list[Movie]:
        return list(self._movies)

    def count(self) -> int:
        return len(self._movies)

    # ---------- persistence ----------

    def _save(self) -> None:
        data = {
            "next_id": self._next_id,
            "movies": [m.to_dict() for m in self._movies],
        }
        with open(self._filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _load(self) -> None:
        if not os.path.exists(self._filepath):
            return
        try:
            with open(self._filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._next_id = data.get("next_id", 1)
            for d in data.get("movies", []):
                m = Movie(
                    title=d["title"],
                    year=d["year"],
                    genre=d["genre"],
                    rating=d["rating"],
                    director=d["director"],
                    description=d.get("description", ""),
                )
                m.id = d["id"]
                self._movies.append(m)
        except (json.JSONDecodeError, KeyError):
            # пошкоджений файл — стартуємо з порожнього каталогу
            self._movies = []
            self._next_id = 1