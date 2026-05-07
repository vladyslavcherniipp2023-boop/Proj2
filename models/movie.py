"""
Модель фільму — чистий data-клас без залежностей.
"""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Movie:
    title: str
    year: int
    genre: str
    rating: float          # 0.0 – 10.0
    director: str
    description: str = ""
    id: Optional[int] = field(default=None, init=False)

    # ---------- валідація ----------

    def validate(self) -> list[str]:
        """Повертає список помилок або порожній список, якщо все ок."""
        errors = []
        if not self.title.strip():
            errors.append("Назва фільму не може бути порожньою.")
        if not (1888 <= self.year <= 2100):
            errors.append("Рік має бути між 1888 і 2100.")
        if not (0.0 <= self.rating <= 10.0):
            errors.append("Рейтинг має бути від 0.0 до 10.0.")
        if not self.genre.strip():
            errors.append("Жанр не може бути порожнім.")
        if not self.director.strip():
            errors.append("Режисер не може бути порожнім.")
        return errors

    def is_valid(self) -> bool:
        return len(self.validate()) == 0

    # ---------- зручності ----------

    def matches_query(self, query: str) -> bool:
        """Пошук по назві, режисеру та жанру (без урахування регістру)."""
        q = query.lower()
        return (
            q in self.title.lower()
            or q in self.director.lower()
            or q in self.genre.lower()
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "year": self.year,
            "genre": self.genre,
            "rating": self.rating,
            "director": self.director,
            "description": self.description,
        }

    def __str__(self) -> str:
        return f"{self.title} ({self.year}) — {self.genre}, ★{self.rating}"
