from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
import random
import time

# 固定窗口大小（手机适配）
Window.size = (360, 640)


class HuarongTile(Button):
    def __init__(self, num, **kwargs):
        super().__init__(**kwargs)
        self.num = num
        self.font_size = 32
        self.bold = True
        self.color = (1, 1, 1, 1)
        if num == 0:
            self.text = ""
            self.background_color = get_color_from_hex("#FFFFFF")
        else:
            self.text = str(num)
            self.background_color = get_color_from_hex("#4285F4")


class NumberHuarongApp(App):
    def build(self):
        self.title = "数字华容道"
        self.size = 4
        self.tiles = []
        self.step = 0
        self.time_start = None
        self.running = False

        # 主布局
        self.main_layout = BoxLayout(orientation="vertical", padding=20, spacing=15)

        # 信息栏：步数 + 时间
        self.info_layout = BoxLayout(orientation="horizontal", size_hint=(1, 0.1))
        self.step_label = Label(text=f"步数：{self.step}", font_size=20, bold=True)
        self.time_label = Label(text="时间：0s", font_size=20, bold=True)
        self.info_layout.add_widget(self.step_label)
        self.info_layout.add_widget(self.time_label)
        self.main_layout.add_widget(self.info_layout)

        # 棋盘 4×4
        self.board = GridLayout(cols=4, spacing=8)
        self.main_layout.add_widget(self.board)

        # 按钮栏
        self.btn_layout = BoxLayout(orientation="horizontal", size_hint=(1, 0.1), spacing=10)
        self.restart_btn = Button(text="重新开始", font_size=18, bold=True,
                                  background_color=get_color_from_hex("#34A853"))
        self.restart_btn.bind(on_press=self.restart)
        self.btn_layout.add_widget(self.restart_btn)
        self.main_layout.add_widget(self.btn_layout)

        # 初始化游戏
        self.init_game()
        return self.main_layout

    def init_game(self):
        self.generate_solvable_puzzle()
        self.step = 0
        self.time_start = None
        self.running = False
        self.step_label.text = f"步数：{self.step}"
        self.time_label.text = "时间：0s"
        self.update_board()

    def update_board(self):
        self.board.clear_widgets()
        for n in self.tiles:
            tile = HuarongTile(n)
            tile.bind(on_press=self.tap_tile)
            self.board.add_widget(tile)

    def tap_tile(self, btn):
        idx = self.tiles.index(btn.num)
        empty_idx = self.tiles.index(0)
        row = idx // self.size
        col = idx % self.size
        er = empty_idx // self.size
        ec = empty_idx % self.size

        # 判断是否可移动
        if (abs(row - er) == 1 and col == ec) or (abs(col - ec) == 1 and row == er):
            self.tiles[empty_idx], self.tiles[idx] = self.tiles[idx], self.tiles[empty_idx]
            self.step += 1
            self.step_label.text = f"步数：{self.step}"

            if not self.running:
                self.time_start = time.time()
                self.running = True
                Clock.schedule_interval(self.update_time, 1)

            self.update_board()

            if self.check_win():
                self.running = False
                Clock.unschedule(self.update_time)
                from kivy.uix.popup import Popup
                p = Popup(title="恭喜通关！",
                          content=Label(text=f"步数：{self.step}\n用时：{int(time.time() - self.time_start)}秒"),
                          size_hint=(0.7, 0.4))
                p.open()
                self.restart(None)

    def update_time(self, dt):
        if self.running:
            t = int(time.time() - self.time_start)
            self.time_label.text = f"时间：{t}s"

    def check_win(self):
        target = list(range(1, self.size ** 2)) + [0]
        return self.tiles == target

    def generate_solvable_puzzle(self):
        while True:
            self.tiles = list(range(1, self.size ** 2)) + [0]
            random.shuffle(self.tiles)
            if self.is_solvable():
                break

    def is_solvable(self):
        board = self.tiles.copy()
        blank_row = board.index(0) // self.size + 1
        board = [x for x in board if x != 0]
        inv = 0
        for i in range(len(board)):
            for j in range(i + 1, len(board)):
                if board[i] > board[j]:
                    inv += 1
        if self.size % 2 == 0:
            return (inv + blank_row) % 2 == 0
        return inv % 2 == 0

    def restart(self, instance):
        Clock.unschedule(self.update_time)
        self.init_game()


if __name__ == "__main__":
    NumberHuarongApp().run()