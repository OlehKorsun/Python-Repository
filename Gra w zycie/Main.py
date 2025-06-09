import tkinter as tk
import random
import pygame
import threading

CELL_SIZE = 30   # Rozmiar komurki
GRID_WIDTH = 30     # Ilość komórek w wierszu (szerokość)
GRID_HEIGHT = 20    #Ilość komórek w kolumnie (wysokość)

# Inicjalizacja dźwięku
pygame.init()
pygame.mixer.init()

class GameOfLife:
    NOTES_C_MAJOR = [
        130.81,  # C3
        146.83,  # D3
        164.81,  # E3
        174.61,  # F3
        196.00,  # G3
        220.00,  # A3
        246.94,  # B3

        261.63,  # C4
        293.66,  # D4
        329.63,  # E4
        349.23,  # F4
        392.00,  # G4
        440.00,  # A4
        493.88,  # B4

        523.25,  # C5
        587.33,  # D5
        659.25,  # E5
        698.46,  # F5
        783.99,  # G5
        880.00,  # A5
        987.77,  # B5

        1046.50,  # C6
    ]

    def __init__(self, root, duration):

        """
        Inicjalizuje główne komponenty aplikacji: siatkę, GUI i menu.

        :param root: Główne okno Tkinter.
        :type root: tk.Tk
        :param duration: Czas między generacjami w milisekundach.
        :type duration: int
        """

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

        """
        Zamienia stan pojedynczej komórki (żywa na martwa lub odwrotnie) po kliknięciu myszy.

        :param event: Obiekt zdarzenia kliknięcia myszy zawierający współrzędne.
        :type event: tk.Event
        """

        if not self.running and self.manual:
            x = event.x // CELL_SIZE
            y = event.y // CELL_SIZE
            self.grid[y][x] = 1 - self.grid[y][x]
            self.draw_grid()

    def random_mode(self):

        """
        Aktywuje tryb losowego generowania siatki z prawdopodobieństwem aktywnej komórki 20%.
        """

        self.manual = False
        # self.grid = [[random.choice([0, 1]) for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]  # szansa 50%
        self.grid = [[1 if random.random() < 0.2 else 0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]    # szansa 20%
        self.draw_grid()

    def manual_mode(self):

        """
        Włącza tryb ręczny i czyści siatkę do stanu początkowego (same martwe komórki).
        """

        self.manual = True
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.draw_grid()

    def start(self):

        """
        Uruchamia symulację, jeśli nie została wcześniej uruchomiona.
        """

        if not self.running:
            self.running = True
            self.play_initial_sound_then_start_game()

    def stop(self):

        """
        Zatrzymuje aktualnie działającą symulację.
        """

        self.running = False

    def clear_grid(self):

        """
        Zatrzymuje symulację i czyści siatkę ze wszystkich żywych komórek.
        """

        self.stop()
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.draw_grid()

    def play_initial_sound_then_start_game(self):

        """
        Odtwarza początkowy dźwięk przed uruchomieniem pierwszej generacji gry.
        Wykonywane w osobnym wątku, aby nie blokować GUI.
        """

        def run_initial_sound():
            self.play_sounds(initial_only=True)
            if self.running:
                self.root.after(self.duration, self.run_game)

        threading.Thread(target=run_initial_sound, daemon=True).start()




    def draw_grid(self, highlight_col=None):

        """
        Rysuje całą siatkę na płótnie. Może opcjonalnie wyróżnić jedną kolumnę.

        :param highlight_col: Indeks kolumny do wyróżnienia kolorem (np. na potrzeby synchronizacji z dźwiękiem).
        :type highlight_col: int | None
        """

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

        """
        Wykonuje jedną generację symulacji zgodnie z regułami gry w życie.
        Aktualizuje siatkę i GUI. Uruchamia także dźwięki w osobnym wątku.
        """

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

        """
        Zlicza liczbę żywych sąsiadów dla komórki o współrzędnych (x, y).

        Metoda przeszukuje wszystkie 8 sąsiadujących komórek wokół podanej pozycji
        i zlicza te, które są żywe (wartość 1). Komórki poza granicami siatki są ignorowane.

        :param x: Współrzędna pozioma (szerokość) komórki.
        :type x: int
        :param y: Współrzędna pionowa (wysokość) komórki.
        :type y: int

        :return: Liczba żywych sąsiadów komórki.
        :rtype: int
        """

        count = 0
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                    count += self.grid[ny][nx]
        return count

    # def play_sounds(self):
    #     import numpy as np
    #     import time
    #
    #     sample_rate = 44100
    #     duration = 100      # jak długo będzie generowany dźwięk
    #     max_freq = 1000
    #     min_freq = 220
    #     delay = 0.1        # Jak szybko będę przeskakiwał przez te kolumny
    #
    #     col_activity = [sum(self.grid[y][x] for y in range(GRID_HEIGHT)) for x in range(GRID_WIDTH)]
    #
    #     for i, activity in enumerate(col_activity):
    #         if not self.running:
    #             break  # przerwij, jeśli gra została zatrzymana
    #
    #         self.root.after(0, self.draw_grid, i)
    #
    #         if activity > 0:
    #             freq = min_freq + (max_freq - min_freq) * (activity / GRID_HEIGHT)
    #             self.beep(freq, duration)
    #
    #         time.sleep(delay)
    #
    #     # Po zakończeniu dźwięku kontynuuj grę, jeśli nadal trwa
    #     if self.running:
    #         self.root.after(self.duration, self.run_game)

    def play_sounds(self, initial_only=False):

        """
        Odtwarza dźwięki na podstawie aktywności w kolumnach siatki.

        Dla każdej kolumny obliczana jest liczba żywych komórek, a następnie, jeśli jest większa od zera,
        odtwarzany jest odpowiedni dźwięk odpowiadający wysokości dźwięku w skali C-dur.
        Metoda również podświetla aktualnie przetwarzaną kolumnę w interfejsie.
        Jeśli parametr `initial_only` jest ustawiony na True, metoda nie kontynuuje gry po zakończeniu
        odtwarzania dźwięków.

        :param initial_only: Jeśli True, metoda nie przechodzi do kolejnej generacji po zakończeniu odtwarzania.
        :type initial_only: bool
        """

        import time

        duration = 100  # jak długo będzie generowany dźwięk
        delay = 0.1     # Jak szybko będę przeskakiwał przez te kolumny

        col_activity = [sum(self.grid[y][x] for y in range(GRID_HEIGHT)) for x in range(GRID_WIDTH)]   # liczy żywe komórki w kolumnie

        for i, activity in enumerate(col_activity):
            if not self.running:
                break

            self.root.after(0, self.draw_grid, i)   # nieblokująca aktualizacja GUI

            if activity > 0:
                note_index = min(activity, len(self.NOTES_C_MAJOR))
                freq = self.NOTES_C_MAJOR[note_index]
                self.beep(freq, duration)

            time.sleep(delay)

        if self.running and not initial_only:
            self.root.after(self.duration, self.run_game)


    def beep(self, freq, duration=200):
        import numpy as np

        """ 
        Generuje dźwięk sinusoidalny o zadanej częstotliwości i czasie trwania.
        sample_rate - częstotliwość próbkowania (kluczowy parametr w cyfrowym przetwarzaniu dźwięku). W ciągu 1 sekundy generujemy 44100 próbek fali dźwiękowej.
        t - generuje num równomiernie rozmieszczonych punktów między start a stop.To są punkty w czasie, w których obliczamy wartości fali sinusoidalnej (np. sin(2πft)).
        to podstawowy krok w cyfrowym generowaniu dźwięku:
        1) tworzenie siatkę punktów czasowych,
        2) liczenie fali sinusoidalnej w tych punktach (sin(2πft)),
        3) odtwarzanie całości jako dźwięk.
        wave -  (obwiednia) — czyli wektor wartości liniowo malejących od 1 do 0 o tej samej długości co fala wave. Cel: Głośność dźwięku będzie stopniowo malała, co zapobiega nagłym cięciom (trzaskom) przy końcu dźwięku.
        wave *= envelope - tworzy łagodne wygaszanie dźwięku — tzw. "fade out".
        stereo_wave - Zamienia mono dźwięk (1 kanał) na stereo (2 kanały — lewy i prawy). Po prostu kopiuje ten sam sygnał do obu kanałów, np.:
        audio - fala dźwiękowa (której wartości są w zakresie -1.0 do 1.0) jest przeskalowana do formatu, który może być odtwarzany przez pygame.
        32767 to maksymalna wartość typu int16 (dla 16-bitowego dźwięku). 
        astype(np.int16) konwertuje dane na typ, którego pygame.sndarray.make_sound oczekuje.


        Args:
            freq (float): Częstotliwość dźwięku w Hz.
            duration (int, optional): Czas trwania w milisekundach. Domyślnie 200.
        """

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
        """
        Uruchamia dźwięk w osobnym wątku żeby nie blokować GUI i żeby program się nie zawieszał
        """
        threading.Thread(target=self.play_sounds, daemon=True).start()

    def save_grid(self):
        """
        Służy do zapisywania narysowanego bądź wygenerowanego obrazka do pliku tekstowego, gdzie 1 - to będzie "żywa" komórka, a 0 - "martwa".
        """
        from tkinter import filedialog
        filepath = filedialog.asksaveasfilename(defaultextension=".txt",
                                                filetypes=[("Pliki tekstowe", "*.txt")])
        if not filepath:
            return

        with open(filepath, "w") as f:
            for row in self.grid:
                f.write(" ".join(map(str, row)) + "\n")

    def load_grid(self):

        """
        Wczytuje siatkę komórek z pliku tekstowego.

        Użytkownik wybiera plik tekstowy zawierający dane siatki (ręcznie zapisanej lub wygenerowanej wcześniej).
        Metoda odczytuje dane, przekształca je do formatu siatki (lista list) i aktualizuje planszę gry.
        Jeśli wczytana siatka ma inne wymiary niż bieżąca, dane są przycinane do aktualnego rozmiaru.
        """

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

        """
        Zaznacza komórkę jako żywą podczas rysowania myszką w trybie ręcznym.

        Metoda jest wywoływana, gdy użytkownik przeciąga lewym przyciskiem myszy po planszy.
        Jeśli gra nie jest uruchomiona i jest w trybie ręcznym, zaznacza komórki jako żywe (ustawia wartość 1)
        na podstawie pozycji kursora.

        :param event: Obiekt zdarzenia `tkinter`, zawierający współrzędne pozycji myszy.
        :type event: tkinter.Event
        """

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