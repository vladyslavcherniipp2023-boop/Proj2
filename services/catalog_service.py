"""
Сервіс каталогу — вся бізнес-логіка.
Між UI та репозиторієм. Не знає нічого про Tkinter.
"""
from models.movie import Movie
from services.movie_repository import MovieRepository


class CatalogService:
    """
    Координує операції над фільмами:
      - валідація перед збереженням
      - пошук і фільтрація
      - сортування
      - агрегована статистика
    """

    SORT_FIELDS = ("title", "year", "rating", "genre", "director")

    def __init__(self, repository: MovieRepository):
        self._repo = repository

    # ---------- CRUD ----------

    def add_movie(self, movie: Movie) -> tuple[bool, list[str]]:
        """
        Повертає (True, []) при успіху або (False, [помилки]) при невалідних даних.
        """
        errors = movie.validate()
        if errors:
            return False, errors
        self._repo.add(movie)
        return True, []

    def update_movie(self, movie: Movie) -> tuple[bool, list[str]]:
        errors = movie.validate()
        if errors:
            return False, errors
        updated = self._repo.update(movie)
        if not updated:
            return False, ["Фільм з таким ID не знайдено."]
        return True, []

    def delete_movie(self, movie_id: int) -> bool:
        return self._repo.delete(movie_id)

    def get_movie(self, movie_id: int) -> Movie | None:
        return self._repo.get_by_id(movie_id)

    # ---------- пошук / фільтрація ----------

    def search(self, query: str) -> list[Movie]:
        """Повнотекстовий пошук по назві, режисеру, жанру."""
        if not query.strip():
            return self._repo.get_all()
        return [m for m in self._repo.get_all() if m.matches_query(query)]

    def filter_by_genre(self, genre: str) -> list[Movie]:
        if genre == "Усі":
            return self._repo.get_all()
        return [m for m in self._repo.get_all() if m.genre == genre]

    def filter_by_min_rating(self, min_rating: float) -> list[Movie]:
        return [m for m in self._repo.get_all() if m.rating >= min_rating]

    # ---------- сортування ----------

    def get_sorted(
        self,
        movies: list[Movie] | None = None,
        by: str = "title",
        reverse: bool = False,
    ) -> list[Movie]:
        if by not in self.SORT_FIELDS:
            raise ValueError(f"Поле сортування має бути одним із: {self.SORT_FIELDS}")
        source = movies if movies is not None else self._repo.get_all()
        return sorted(source, key=lambda m: getattr(m, by), reverse=reverse)

    # ---------- статистика ----------

    def get_stats(self) -> dict:
        movies = self._repo.get_all()
        if not movies:
            return {
                "total": 0,
                "avg_rating": 0.0,
                "best_movie": None,
                "genres": {},
            }
        ratings = [m.rating for m in movies]
        genres: dict[str, int] = {}
        for m in movies:
            genres[m.genre] = genres.get(m.genre, 0) + 1
        best = max(movies, key=lambda m: m.rating)
        return {
            "total": len(movies),
            "avg_rating": round(sum(ratings) / len(ratings), 2),
            "best_movie": best,
            "genres": genres,
        }

    def get_all_genres(self) -> list[str]:
        genres = {m.genre for m in self._repo.get_all()}
        return sorted(genres)