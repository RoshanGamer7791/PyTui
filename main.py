import os
import sys
import time
import threading

try:
    import readchar
    from readchar import key
except ModuleNotFoundError:
    os.system(f"{sys.executable} -m pip install readchar --break-system-packages")
    import readchar
    from readchar import key

def clear_terminal() -> None:
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")

sys.stdout.write("\x1b[?25l")
sys.stdout.flush()

class Screen:
    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.screen_buffer = [[' ' for _ in range(width)] for _ in range(height)]
        self.prev_buffer = []
        self.key = None
        threading.Thread(target=self.track_key, daemon=True).start()

    def render(self) -> None:
        if self.screen_buffer != self.prev_buffer:
            clear_terminal()
            for row in self.screen_buffer:
                print("".join(row))
            self.prev_buffer = [row.copy() for row in self.screen_buffer]

    def track_key(self):
        while True:
            self.key = readchar.readkey()

    def get_key_pressed(self) -> str | None:
        _key = self.key
        self.key = None
        return _key

    def draw_border(self):
        for x in range(self.width):
            self.screen_buffer[0][x] = "-"
            self.screen_buffer[self.height - 1][x] = "-"

        for y in range(self.height):
            self.screen_buffer[y][0] = "|"
            self.screen_buffer[y][self.width - 1] = "|"

    def get_width(self) -> int:
        return len(self.screen_buffer[0])

    def get_height(self) -> int:
        return len(self.screen_buffer)

    def clear_screen(self) -> None:
        self.screen_buffer = [[' ' for _ in range(self.width)] for _ in range(self.height)]

class Rect:
    def __init__(self, parent: Screen, x: int, y: int, width: int, height: int) -> None:
        self.parent = parent
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def draw_outline(self) -> None:
        for x in range(self.x, self.x + self.width):
            if x > self.parent.get_width():
                break
            if self.y > self.parent.get_height():
                break
            if self.y + self.height > self.parent.get_height():
                break
            self.parent.screen_buffer[self.y][x] = "-"
            self.parent.screen_buffer[self.y + self.height - 1][x] = "-"

        for y in range(self.y, self.y + self.height):
            if y > self.parent.get_height():
                break
            if self.y + self.height > self.parent.get_height():
                break
            if self.y > self.parent.get_height():
                break
            self.parent.screen_buffer[y][self.x] = "|"
            self.parent.screen_buffer[y][self.x + self.width] = "|"

class Text:
    def __init__(self, parent: Screen, text: str, x: int, y: int) -> None:
        self.parent = parent
        self.text = text
        self.x = x
        self.y = y

    def draw(self) -> None:
        text_index: int = 0
        for x in range(self.x, self.x + len(self.text)):
            if x > self.parent.get_width():
                break
            if self.y > self.parent.get_height():
                break
            self.parent.screen_buffer[self.y][x] = self.text[text_index]
            text_index += 1


canvas = Screen(120, 29)

test = Rect(canvas, 50, 10, 10, 5)
test.draw_outline()

text_test = Text(canvas, "", 50, 20)

i = 0
start_time = time.perf_counter()
fps = 0.0
while True:
    text_test.draw()
    canvas.render()
    i += 1
    if i % 1_000:
        average_time = time.perf_counter() - start_time
        fps = i / average_time
    print(f"\rRuns at: {fps:.0f}fps | Iteration number: {i:,}", end="")