"""
Тести для каталогу фільмів.
Запуск: pytest tests/ -v   (з папки movie_catalog/)

Покриття (~30 тестів):
  ✅ Позитивні сценарії  — ~12
  ✅ Граничні умови      — ~8
  ✅ Валідація даних     — ~5
  ✅ Mock (поведінка)    — ~3
  ✅ Stub (заглушка)     — ~2
"""
import sys, os, pytest
from unittest.mock import MagicMock, call

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from models.movie import Movie
from services.movie_repository import MovieRepository
from services.catalog_service import CatalogService


# ══════════════════════════════════════════════════════════════
#  Допоміжні фікстури
# ══════════════════════════════════════════════════════════════

def make_movie(
    title="Inception",
    year=2010,
    genre="Sci-Fi",
    rating=8.8,
    director="Christopher Nolan",
    description="",
) -> Movie:
    return Movie(title=title, year=year, genre=genre,
                 rating=rating, director=director, description=description)


@pytest.fixture
def repo(tmp_path):
    """Реальний репозиторій з тимчасовим JSON-файлом."""
    return MovieRepository(str(tmp_path / "movies.json"))


@pytest.fixture
def service(repo):
    return CatalogService(repo)


@pytest.fixture
def populated_service(service):
    """Сервіс із трьома заздалегідь доданими фільмами."""
    service.add_movie(make_movie("Inception",  2010, "Sci-Fi",   8.8, "Nolan"))
    service.add_movie(make_movie("Parasite",   2019, "Thriller", 8.5, "Bong Joon-ho"))
    service.add_movie(make_movie("The Matrix", 1999, "Sci-Fi",   8.7, "The Wachowskis"))
    return service


# ══════════════════════════════════════════════════════════════
#  1. ПОЗИТИВНІ СЦЕНАРІЇ  (~12 тестів)
# ══════════════════════════════════════════════════════════════

class TestPositive:

    def test_valid_movie_is_valid(self):
        assert make_movie().is_valid() is True

    def test_add_movie_returns_true(self, service):
        ok, errors = service.add_movie(make_movie())
        assert ok is True
        assert errors == []

    def test_added_movie_appears_in_search(self, service):
        service.add_movie(make_movie("Blade Runner", 1982, "Sci-Fi", 8.1, "Scott"))
        results = service.search("Blade")
        assert len(results) == 1
        assert results[0].title == "Blade Runner"

    def test_search_by_director(self, populated_service):
        results = populated_service.search("Nolan")
        assert any(m.director == "Nolan" for m in results)

    def test_search_by_genre(self, populated_service):
        results = populated_service.search("Thriller")
        assert len(results) == 1

    def test_filter_by_genre_returns_correct_subset(self, populated_service):
        scifi = populated_service.filter_by_genre("Sci-Fi")
        assert len(scifi) == 2
        assert all(m.genre == "Sci-Fi" for m in scifi)

    def test_filter_by_genre_all_returns_everything(self, populated_service):
        all_movies = populated_service.filter_by_genre("Усі")
        assert len(all_movies) == 3

    def test_get_sorted_by_year_ascending(self, populated_service):
        sorted_movies = populated_service.get_sorted(by="year")
        years = [m.year for m in sorted_movies]
        assert years == sorted(years)

    def test_get_sorted_by_rating_descending(self, populated_service):
        sorted_movies = populated_service.get_sorted(by="rating", reverse=True)
        ratings = [m.rating for m in sorted_movies]
        assert ratings == sorted(ratings, reverse=True)

    def test_delete_removes_movie(self, service):
        ok, _ = service.add_movie(make_movie())
        movie_id = service.search("Inception")[0].id
        assert service.delete_movie(movie_id) is True
        assert service.get_movie(movie_id) is None

    def test_stats_total_count(self, populated_service):
        stats = populated_service.get_stats()
        assert stats["total"] == 3

    def test_stats_best_movie_is_highest_rated(self, populated_service):
        stats = populated_service.get_stats()
        assert stats["best_movie"].title == "Inception"   # rating 8.8

    def test_to_dict_contains_all_keys(self):
        m = make_movie()
        d = m.to_dict()
        for key in ("id", "title", "year", "genre", "rating", "director", "description"):
            assert key in d


# ══════════════════════════════════════════════════════════════
#  2. ГРАНИЧНІ УМОВИ  (~8 тестів)
# ══════════════════════════════════════════════════════════════

class TestBoundary:

    def test_year_exactly_1888_is_valid(self):
        assert make_movie(year=1888).is_valid() is True

    def test_year_exactly_2100_is_valid(self):
        assert make_movie(year=2100).is_valid() is True

    def test_year_1887_is_invalid(self):
        errors = make_movie(year=1887).validate()
        assert any("Рік" in e for e in errors)

    def test_rating_zero_is_valid(self):
        assert make_movie(rating=0.0).is_valid() is True

    def test_rating_ten_is_valid(self):
        assert make_movie(rating=10.0).is_valid() is True

    def test_rating_negative_is_invalid(self):
        errors = make_movie(rating=-0.1).validate()
        assert any("Рейтинг" in e for e in errors)

    def test_search_empty_query_returns_all(self, populated_service):
        results = populated_service.search("")
        assert len(results) == 3

    def test_search_whitespace_query_returns_all(self, populated_service):
        results = populated_service.search("   ")
        assert len(results) == 3

    def test_delete_nonexistent_id_returns_false(self, service):
        assert service.delete_movie(9999) is False

    def test_stats_empty_catalog(self, service):
        stats = service.get_stats()
        assert stats["total"] == 0
        assert stats["avg_rating"] == 0.0
        assert stats["best_movie"] is None


# ══════════════════════════════════════════════════════════════
#  3. ВАЛІДАЦІЯ ДАНИХ  (~5 тестів)
# ══════════════════════════════════════════════════════════════

class TestValidation:

    def test_empty_title_fails_validation(self):
        errors = make_movie(title="").validate()
        assert len(errors) >= 1
        assert any("Назва" in e for e in errors)

    def test_whitespace_title_fails_validation(self):
        errors = make_movie(title="   ").validate()
        assert any("Назва" in e for e in errors)

    def test_multiple_errors_returned_at_once(self):
        bad = Movie(title="", year=1800, genre="", rating=-5.0, director="")
        errors = bad.validate()
        assert len(errors) == 5   # всі п'ять полів невалідні

    def test_to_dict_types_are_correct(self):
        m = make_movie()
        d = m.to_dict()
        assert isinstance(d["title"], str)
        assert isinstance(d["year"], int)
        assert isinstance(d["rating"], float)

    def test_add_invalid_movie_returns_errors_list(self, service):
        bad = make_movie(title="", year=1000)
        ok, errors = service.add_movie(bad)
        assert ok is False
        assert isinstance(errors, list)
        assert len(errors) > 0

    def test_get_sorted_invalid_field_raises_value_error(self, service):
        with pytest.raises(ValueError):
            service.get_sorted(by="nonexistent_field")


# ══════════════════════════════════════════════════════════════
#  4. MOCK — поведінка  (~3 тести)
# ══════════════════════════════════════════════════════════════

class TestMock:

    def test_add_movie_calls_repo_add_once(self):
        """add_movie повинен викликати repo.add рівно один раз."""
        mock_repo = MagicMock()
        mock_repo.add.return_value = make_movie()
        svc = CatalogService(mock_repo)

        svc.add_movie(make_movie())

        mock_repo.add.assert_called_once()

    def test_invalid_movie_does_not_call_repo_add(self):
        """При невалідних даних repo.add не повинен викликатися взагалі."""
        mock_repo = MagicMock()
        svc = CatalogService(mock_repo)

        svc.add_movie(make_movie(title="", year=1000))

        mock_repo.add.assert_not_called()

    def test_delete_movie_calls_repo_delete_with_correct_id(self):
        """delete_movie має передавати точний ID у repo.delete."""
        mock_repo = MagicMock()
        mock_repo.delete.return_value = True
        svc = CatalogService(mock_repo)

        svc.delete_movie(42)

        mock_repo.delete.assert_called_once_with(42)


# ══════════════════════════════════════════════════════════════
#  5. STUB — підміна залежностей  (~2 тести)
# ══════════════════════════════════════════════════════════════

class StubRepository:
    """Простий stub: репозиторій із фіксованим набором фільмів."""

    def __init__(self, movies: list[Movie]):
        self._movies = movies

    def get_all(self) -> list[Movie]:
        return list(self._movies)

    def add(self, movie: Movie) -> Movie:
        movie.id = len(self._movies) + 1
        self._movies.append(movie)
        return movie

    def delete(self, movie_id: int) -> bool:
        before = len(self._movies)
        self._movies = [m for m in self._movies if m.id != movie_id]
        return len(self._movies) < before

    def get_by_id(self, movie_id: int):
        return next((m for m in self._movies if m.id == movie_id), None)

    def update(self, movie: Movie) -> bool:
        for i, m in enumerate(self._movies):
            if m.id == movie.id:
                self._movies[i] = movie
                return True
        return False


class TestStub:

    def test_search_uses_stub_data(self):
        """CatalogService.search повертає тільки те, що надав stub."""
        m1 = make_movie("Dune", 2021, "Sci-Fi", 8.0, "Villeneuve")
        m1.id = 1
        m2 = make_movie("Joker", 2019, "Drama", 8.4, "Phillips")
        m2.id = 2

        stub = StubRepository([m1, m2])
        svc = CatalogService(stub)

        results = svc.search("Dune")
        assert len(results) == 1
        assert results[0].title == "Dune"

    def test_get_stats_with_stub_calculates_average(self):
        """get_stats правильно рахує середній рейтинг на stub-даних."""
        m1 = make_movie(rating=8.0); m1.id = 1
        m2 = make_movie(rating=6.0); m2.id = 2

        stub = StubRepository([m1, m2])
        svc = CatalogService(stub)

        stats = svc.get_stats()
        assert stats["avg_rating"] == 7.0