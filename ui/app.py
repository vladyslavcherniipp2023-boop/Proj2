"""
Головне вікно Tkinter — тільки UI, жодної бізнес-логіки.
"""
import tkinter as tk
from tkinter import ttk, messagebox

from models.movie import Movie
from services.catalog_service import CatalogService
from services.movie_repository import MovieRepository


# ──────────────────────────────────────────────
#  Діалог додавання / редагування фільму
# ──────────────────────────────────────────────
class MovieDialog(tk.Toplevel):
    def __init__(self, parent, service: CatalogService, movie: Movie | None = None):
        super().__init__(parent)
        self.service = service
        self.movie = movie
        self.result: Movie | None = None

        self.title("Редагувати фільм" if movie else "Додати фільм")
        self.resizable(False, False)
        self.grab_set()

        self._build()
        if movie:
            self._fill(movie)

    def _build(self):
        pad = {"padx": 8, "pady": 4}
        labels = ["Назва", "Рік", "Жанр", "Рейтинг (0–10)", "Режисер", "Опис"]
        self.entries: dict[str, tk.Widget] = {}

        for i, lbl in enumerate(labels):
            tk.Label(self, text=lbl + ":").grid(row=i, column=0, sticky="e", **pad)
            if lbl == "Опис":
                w = tk.Text(self, width=36, height=4)
                w.grid(row=i, column=1, sticky="ew", **pad)
            else:
                w = tk.Entry(self, width=36)
                w.grid(row=i, column=1, sticky="ew", **pad)
            self.entries[lbl] = w

        btn_frame = tk.Frame(self)
        btn_frame.grid(row=len(labels), column=0, columnspan=2, pady=8)
        tk.Button(btn_frame, text="Зберегти", width=12, command=self._save).pack(side="left", padx=4)
        tk.Button(btn_frame, text="Скасувати", width=12, command=self.destroy).pack(side="left", padx=4)

    def _fill(self, m: Movie):
        self.entries["Назва"].insert(0, m.title)
        self.entries["Рік"].insert(0, str(m.year))
        self.entries["Жанр"].insert(0, m.genre)
        self.entries["Рейтинг (0–10)"].insert(0, str(m.rating))
        self.entries["Режисер"].insert(0, m.director)
        self.entries["Опис"].insert("1.0", m.description)

    def _val(self, key: str) -> str:
        w = self.entries[key]
        if isinstance(w, tk.Text):
            return w.get("1.0", "end-1c").strip()
        return w.get().strip()

    def _save(self):
        try:
            year = int(self._val("Рік"))
            rating = float(self._val("Рейтинг (0–10)"))
        except ValueError:
            messagebox.showerror("Помилка", "Рік — ціле число, рейтинг — десяткове.", parent=self)
            return

        movie = Movie(
            title=self._val("Назва"),
            year=year,
            genre=self._val("Жанр"),
            rating=rating,
            director=self._val("Режисер"),
            description=self._val("Опис"),
        )

        if self.movie:          # режим редагування
            movie.id = self.movie.id
            ok, errors = self.service.update_movie(movie)
        else:                   # режим додавання
            ok, errors = self.service.add_movie(movie)

        if ok:
            self.result = movie
            self.destroy()
        else:
            messagebox.showerror("Помилка валідації", "\n".join(errors), parent=self)


# ──────────────────────────────────────────────
#  Головне вікно
# ──────────────────────────────────────────────
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🎬 Каталог фільмів")
        self.geometry("900x540")
        self.minsize(700, 400)

        repo = MovieRepository("movies.json")
        self.service = CatalogService(repo)

        self._build_toolbar()
        self._build_table()
        self._build_statusbar()
        self.refresh()

    # ---------- побудова UI ----------

    def _build_toolbar(self):
        bar = tk.Frame(self, pady=6)
        bar.pack(fill="x", padx=8)

        # пошук
        tk.Label(bar, text="🔍").pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.refresh())
        tk.Entry(bar, textvariable=self.search_var, width=24).pack(side="left", padx=(2, 12))

        # фільтр жанру
        tk.Label(bar, text="Жанр:").pack(side="left")
        self.genre_var = tk.StringVar(value="Усі")
        self.genre_combo = ttk.Combobox(
            bar, textvariable=self.genre_var, width=14, state="readonly"
        )
        self.genre_combo.pack(side="left", padx=(2, 12))
        self.genre_combo.bind("<<ComboboxSelected>>", lambda _: self.refresh())

        # сортування
        tk.Label(bar, text="Сортувати:").pack(side="left")
        self.sort_var = tk.StringVar(value="title")
        sort_combo = ttk.Combobox(
            bar,
            textvariable=self.sort_var,
            values=list(CatalogService.SORT_FIELDS),
            width=10,
            state="readonly",
        )
        sort_combo.pack(side="left", padx=(2, 4))
        sort_combo.bind("<<ComboboxSelected>>", lambda _: self.refresh())

        self.sort_rev = tk.BooleanVar(value=False)
        tk.Checkbutton(bar, text="↓", variable=self.sort_rev, command=self.refresh).pack(side="left", padx=(0, 12))

        # кнопки
        tk.Button(bar, text="➕ Додати", command=self._on_add).pack(side="left", padx=2)
        tk.Button(bar, text="✏️ Редагувати", command=self._on_edit).pack(side="left", padx=2)
        tk.Button(bar, text="🗑 Видалити", command=self._on_delete).pack(side="left", padx=2)
        tk.Button(bar, text="📊 Статистика", command=self._on_stats).pack(side="left", padx=2)

    def _build_table(self):
        cols = ("id", "title", "year", "genre", "rating", "director")
        headers = ("ID", "Назва", "Рік", "Жанр", "Рейтинг", "Режисер")

        frame = tk.Frame(self)
        frame.pack(fill="both", expand=True, padx=8, pady=(0, 4))

        self.tree = ttk.Treeview(frame, columns=cols, show="headings", selectmode="browse")
        widths = (40, 240, 60, 110, 70, 160)
        for col, hdr, w in zip(cols, headers, widths):
            self.tree.heading(col, text=hdr, command=lambda c=col: self._sort_by_col(c))
            self.tree.column(col, width=w, anchor="center" if col != "title" else "w")

        vsb = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self.tree.bind("<Double-1>", lambda _: self._on_edit())

    def _build_statusbar(self):
        self.status_var = tk.StringVar(value="Готово")
        tk.Label(self, textvariable=self.status_var, anchor="w", relief="sunken").pack(
            fill="x", padx=8, pady=(0, 4)
        )

    # ---------- оновлення таблиці ----------

    def refresh(self):
        query = self.search_var.get()
        genre = self.genre_var.get()

        movies = self.service.search(query)
        movies = self.service.filter_by_genre(genre) if genre != "Усі" else movies
        # якщо і пошук і жанр — перетин
        if query and genre != "Усі":
            movies = [m for m in self.service.search(query) if m.genre == genre]

        movies = self.service.get_sorted(movies, by=self.sort_var.get(), reverse=self.sort_rev.get())

        self.tree.delete(*self.tree.get_children())
        for m in movies:
            self.tree.insert("", "end", iid=str(m.id), values=(
                m.id, m.title, m.year, m.genre, f"★ {m.rating}", m.director
            ))

        # оновити список жанрів
        genres = ["Усі"] + self.service.get_all_genres()
        self.genre_combo["values"] = genres

        stats = self.service.get_stats()
        self.status_var.set(
            f"Фільмів у каталозі: {stats['total']}   |   "
            f"Показано: {len(movies)}   |   "
            f"Середній рейтинг: ★ {stats['avg_rating']}"
        )

    def _sort_by_col(self, col: str):
        if col == "id":
            return
        self.sort_var.set(col)
        self.refresh()

    # ---------- обробники кнопок ----------

    def _selected_id(self) -> int | None:
        sel = self.tree.selection()
        return int(sel[0]) if sel else None

    def _on_add(self):
        dlg = MovieDialog(self, self.service)
        self.wait_window(dlg)
        if dlg.result:
            self.refresh()

    def _on_edit(self):
        mid = self._selected_id()
        if mid is None:
            messagebox.showinfo("Увага", "Спочатку виберіть фільм у таблиці.")
            return
        movie = self.service.get_movie(mid)
        dlg = MovieDialog(self, self.service, movie)
        self.wait_window(dlg)
        if dlg.result:
            self.refresh()

    def _on_delete(self):
        mid = self._selected_id()
        if mid is None:
            messagebox.showinfo("Увага", "Спочатку виберіть фільм у таблиці.")
            return
        movie = self.service.get_movie(mid)
        if messagebox.askyesno("Підтвердження", f"Видалити «{movie.title}»?"):
            self.service.delete_movie(mid)
            self.refresh()

    def _on_stats(self):
        stats = self.service.get_stats()
        if stats["total"] == 0:
            messagebox.showinfo("Статистика", "Каталог порожній.")
            return
        best = stats["best_movie"]
        genres_text = "\n".join(f"  {g}: {n}" for g, n in sorted(stats["genres"].items()))
        msg = (
            f"Усього фільмів: {stats['total']}\n"
            f"Середній рейтинг: ★ {stats['avg_rating']}\n"
            f"Найкращий: {best.title} (★ {best.rating})\n\n"
            f"Жанри:\n{genres_text}"
        )
        messagebox.showinfo("Статистика каталогу", msg)


# ──────────────────────────────────────────────
if __name__ == "__main__":
    App().mainloop()