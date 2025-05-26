import tkinter as tk
import random
import pygame
import threading

CELL_SIZE = 10
GRID_WIDTH = 60
GRID_HEIGHT = 40

# Inicjalizacja dźwięku
pygame.init()
pygame.mixer.init()
frequencies = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88]  # C D E F G A H    4
#frequencies = [130.81, 146.83, 164.81, 174.61, 196, 220, 246.94]  # C D E F G A H          3


class GameOfLife:
    duration = 0
    def __init__(self, root, duration):
        self.duration = duration
        self.root = root
        self.root.title("Gra w Życie - Conway")

        self.running = False
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

        self.canvas = tk.Canvas(root, width=GRID_WIDTH * CELL_SIZE, height=GRID_HEIGHT * CELL_SIZE, bg='white')
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.toggle_cell)

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

        self.manual = True
        self.draw_grid()

    # ręczne ustawianie komórki
    def toggle_cell(self, event):
        if not self.running and self.manual:
            x = event.x // CELL_SIZE
            y = event.y // CELL_SIZE
            self.grid[y][x] = 1 - self.grid[y][x]
            self.draw_grid()

    # losowa generacja żywych komórek
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

    def draw_grid(self):
        self.canvas.delete("all")
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                color = "black" if self.grid[y][x] == 1 else "white"
                self.canvas.create_rectangle(
                    x * CELL_SIZE, y * CELL_SIZE,
                    (x + 1) * CELL_SIZE, (y + 1) * CELL_SIZE,
                    fill=color, outline="gray"
                )

    # tworzenie nowej generacji
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
        threading.Thread(target=self.play_sounds, daemon=True).start()
        self.root.after(self.duration, self.run_game)

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

    # Generowanie dzwięku
    def play_sounds(self):
        import numpy as np
        sample_rate = 44100
        duration = 200  # ms
        max_freq = 1000
        min_freq = 220

        # Podziel siatkę na kolumny i zlicz żywe komórki
        col_activity = [sum(self.grid[y][x] for y in range(GRID_HEIGHT)) for x in range(GRID_WIDTH)]

        for i, activity in enumerate(col_activity):
            if activity > 0:
                # Zmapuj liczbę komórek (np. 0–GRID_HEIGHT) na zakres częstotliwości
                freq = min_freq + (max_freq - min_freq) * (activity / GRID_HEIGHT)
                threading.Thread(target=self.beep, args=(freq, duration)).start()

    def beep(self, freq, duration=200):
        import numpy as np
        sample_rate = 44100
        t = np.linspace(0, duration / 1000, int(sample_rate * duration / 1000), False)

        # Fala sinusoidalna + prosty "fade" (envelope)
        wave = 0.5 * np.sin(2 * np.pi * freq * t)
        envelope = np.linspace(1, 0, wave.shape[0])  # Opadająca głośność
        wave *= envelope

        stereo_wave = np.stack((wave, wave), axis=-1)
        audio = (stereo_wave * 32767).astype(np.int16)

        sound = pygame.sndarray.make_sound(audio)
        sound.play()

    def sine_wave(self, freq, duration):
        import numpy as np
        sample_rate = 44100
        t = np.linspace(0, duration / 1000, int(sample_rate * duration / 1000), False)
        wave = np.sin(freq * t * 2 * np.pi)
        audio = (wave * 32767).astype(np.int16)
        return pygame.sndarray.make_sound(audio)

if __name__ == "__main__":
    root = tk.Tk()
    app = GameOfLife(root, 400)
    root.mainloop()
