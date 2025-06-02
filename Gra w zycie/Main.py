import tkinter as tk
import random
import pygame
import threading

CELL_SIZE = 30   # Rozmiar komurki
GRID_WIDTH = 30     # Ilość komórek szerokość
GRID_HEIGHT = 20    #Ilość komórek wysokość

# Inicjalizacja dźwięku
pygame.init()
pygame.mixer.init()


class GameOfLife:
    def __init__(self, root, duration):
        self.duration = duration  # czas między generacjami w ms
        self.root = root
        self.root.title("Gra w Życie - Conway")

        self.running = False
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

        self.canvas = tk.Canvas(root, width=GRID_WIDTH * CELL_SIZE, height=GRID_HEIGHT * CELL_SIZE, bg='white')
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.toggle_cell)
        self.canvas.bind("<B1-Motion>", self.paint_cell)

        self.menu_frame = tk.Frame(root)
        self.menu_frame.pack(pady=10)

        self.random_button = tk.Button(self.menu_frame, text="Losowe komórki", command=self.random_mode)
        self.random_button.pack(side=tk.LEFT, padx=5)

        self.manual_button = tk.Button(self.menu_frame, text="Tryb ręczny", command=self.manual_mode)
        self.manual_button.pack(side=tk.LEFT, padx=5)

        self.start_button = tk.Button(self.menu_frame, text="Start", command=self.start)
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = tk.Button(self.menu_frame, text="Stop", command=self.stop)
        self.stop_button.pack(side=tk.LEFT, padx=5)

        self.clear_button = tk.Button(self.menu_frame, text="Wyczyść", command=self.clear_grid)
        self.clear_button.pack(side=tk.LEFT, padx=5)

        self.save_button = tk.Button(self.menu_frame, text="Zapisz", command=self.save_grid)
        self.save_button.pack(side=tk.LEFT, padx=5)

        self.load_button = tk.Button(self.menu_frame, text="Wczytaj", command=self.load_grid)
        self.load_button.pack(side=tk.LEFT, padx=5)

        self.manual = True
        self.draw_grid()

    def toggle_cell(self, event):
        if not self.running and self.manual:
            x = event.x // CELL_SIZE
            y = event.y // CELL_SIZE
            self.grid[y][x] = 1 - self.grid[y][x]
            self.draw_grid()

    def random_mode(self):
        self.manual = False
        self.grid = [[random.choice([0, 1]) for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.draw_grid()

    def manual_mode(self):
        self.manual = True
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.draw_grid()

    def start(self):
        self.running = True
        self.run_game()

    def stop(self):
        self.running = False

    def clear_grid(self):
        self.stop()
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.draw_grid()

    def draw_grid(self, highlight_col=None):
        self.canvas.delete("all")
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if highlight_col is not None and x == highlight_col:
                    color = "blue" if self.grid[y][x] == 1 else "#ADD8E6"
                else:
                    color = "black" if self.grid[y][x] == 1 else "white"
                self.canvas.create_rectangle(
                    x * CELL_SIZE, y * CELL_SIZE,
                    (x + 1) * CELL_SIZE, (y + 1) * CELL_SIZE,
                    fill=color, outline="gray"
                )

    def run_game(self):
        if not self.running:
            return

        new_grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                live_neighbors = self.count_neighbors(x, y)
                if self.grid[y][x] == 1:
                    if live_neighbors in [2, 3]:
                        new_grid[y][x] = 1
                else:
                    if live_neighbors == 3:
                        new_grid[y][x] = 1

        self.grid = new_grid
        self.draw_grid()

        # Uruchamiamy dźwięk w osobnym wątku, a po zakończeniu kontynuujemy grę
        self.play_sounds_threaded()

    def count_neighbors(self, x, y):
        count = 0
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                    count += self.grid[ny][nx]
        return count

    def play_sounds(self):
        import numpy as np
        import time

        sample_rate = 44100
        duration = 100      # jak długo będzie generowany dźwięk
        max_freq = 1000
        min_freq = 220
        delay = 0.05        # Jak szybko będę przeskakiwał przez te kolumny

        col_activity = [sum(self.grid[y][x] for y in range(GRID_HEIGHT)) for x in range(GRID_WIDTH)]

        for i, activity in enumerate(col_activity):
            if not self.running:
                break  # przerwij, jeśli gra została zatrzymana

            self.root.after(0, self.draw_grid, i)

            if activity > 0:
                freq = min_freq + (max_freq - min_freq) * (activity / GRID_HEIGHT)
                self.beep(freq, duration)

            time.sleep(delay)

        # Po zakończeniu dźwięku kontynuuj grę, jeśli nadal trwa
        if self.running:
            self.root.after(self.duration, self.run_game)

    def beep(self, freq, duration=200):
        import numpy as np
        sample_rate = 44100
        t = np.linspace(0, duration / 1000, int(sample_rate * duration / 1000), False)

        wave = 0.5 * np.sin(2 * np.pi * freq * t)
        envelope = np.linspace(1, 0, wave.shape[0])
        wave *= envelope

        stereo_wave = np.stack((wave, wave), axis=-1)
        audio = (stereo_wave * 32767).astype(np.int16)

        sound = pygame.sndarray.make_sound(audio)
        sound.play()

    def play_sounds_threaded(self):
        threading.Thread(target=self.play_sounds, daemon=True).start()

    def save_grid(self):
        from tkinter import filedialog
        filepath = filedialog.asksaveasfilename(defaultextension=".txt",
                                                filetypes=[("Pliki tekstowe", "*.txt")])
        if not filepath:
            return

        with open(filepath, "w") as f:
            for row in self.grid:
                f.write(" ".join(map(str, row)) + "\n")

    def load_grid(self):
        from tkinter import filedialog
        filepath = filedialog.askopenfilename(filetypes=[("Pliki tekstowe", "*.txt")])
        if not filepath:
            return

        with open(filepath, "r") as f:
            lines = f.readlines()

        loaded_grid = []
        for line in lines:
            row = list(map(int, line.strip().split()))
            loaded_grid.append(row)

        # Dopasuj rozmiar jeśli plik ma inne wymiary
        for y in range(min(len(loaded_grid), GRID_HEIGHT)):
            for x in range(min(len(loaded_grid[y]), GRID_WIDTH)):
                self.grid[y][x] = loaded_grid[y][x]

        self.draw_grid()

    def paint_cell(self, event):
        if not self.running and self.manual:
            x = event.x // CELL_SIZE
            y = event.y // CELL_SIZE
            if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
                if self.grid[y][x] != 1:  # rysuj tylko jeśli zmieniamy coś
                    self.grid[y][x] = 1
                    self.draw_grid()


if __name__ == "__main__":
    root = tk.Tk()
    app = GameOfLife(root, 400)  # 400 ms między generacjami
    root.mainloop()