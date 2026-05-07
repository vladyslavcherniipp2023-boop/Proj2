# test_e2e.py
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from ui.app import App
from models.movie import Movie


def test_e2e_critical_path(tmp_path):
    # ───────── Крок 1: запуск програми з порожнім файлом ─────────
    app = App()
    app.service._repo._filepath = str(tmp_path / "movies.json")
    app.service._repo._movies = []
    app.service._repo._next_id = 1
    app.refresh()

    assert len(app.tree.get_children()) == 0, "На старті таблиця має бути порожньою"

    # ───────── Крок 2: додати фільм ─────────
    movie = Movie(
        title="Inception",
        year=2010,
        genre="Sci-Fi",
        rating=8.8,
        director="Nolan"
    )

    ok, _ = app.service.add_movie(movie)
    assert ok is True

    app.refresh()

    items = app.tree.get_children()
    assert len(items) == 1
    

    values = app.tree.item(items[0])["values"]
    assert values[1] == "Inception"

    # ───────── Крок 3: пошук ─────────
    app.search_var.set("Inception")
    app.refresh()
    assert len(app.tree.get_children()) == 1

    # пошук якого немає
    app.search_var.set("Аватар")
    app.refresh()
    assert len(app.tree.get_children()) == 0

    app.search_var.set("")
    app.refresh()

    # ───────── Крок 4: фільтр по жанру ─────────
    app.genre_var.set("Sci-Fi")
    app.refresh()
    assert len(app.tree.get_children()) == 1

    app.genre_var.set("Усі")
    app.refresh()

    # ───────── Крок 5: сортування ─────────
    app.sort_var.set("year")
    app.sort_rev.set(True)
    app.refresh()
    assert len(app.tree.get_children()) == 1

    # ───────── Крок 6: видалення ─────────
    items = app.tree.get_children()
    movie_id = int(items[0])
    app.service.delete_movie(movie_id)
    app.refresh()

    assert len(app.tree.get_children()) == 0

    # ───────── Крок 7: статистика після видалення ─────────
    stats = app.service.get_stats()
    assert stats["total"] == 0

    app.destroy()