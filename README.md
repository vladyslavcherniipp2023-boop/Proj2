# 🎬 Movie Catalog

![CI/CD Pipeline](https://github.com/vladyslavcherniipp2023-boop/Proj2/actions/workflows/ci-cd.yml/badge.svg)

Застосунок для управління особистим каталогом фільмів з графічним інтерфейсом (Tkinter).

## Структура проєкту
PROJ4LAB2/
├── models/movie.py
├── services/catalog_service.py
├── services/movie_repository.py
├── tests/test_unit.py
├── tests/test_e2e.py
├── ui/app.py
├── main.py
└── movies.json

## Запуск

```bash
python main.py
```

## Тести

```bash
# Unit-тести
pytest tests/test_unit.py -v

# E2e-тест (тільки локально, потребує дисплей)
pytest tests/test_e2e.py -v
```

## CI/CD

Проєкт використовує GitHub Actions для автоматичної перевірки коду при кожному push та pull request:
- ✅ Лінтер (flake8)
- ✅ Unit-тести (pytest)

Автоматичний деплой на Vercel при merge у гілку `main`.