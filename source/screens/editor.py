import os
from datetime import datetime
import pyxel
# from PIL import Image
# from js import window, Blob, URL, document
from js import Blob, URL, Uint8Array, document
from copy import deepcopy

import utils
# =========================================================
# Pyxel標準16色
# =========================================================

PYXEL_PALETTE = [
    0x000000,  # 0
    0x2B335F,  # 1
    0x7E2072,  # 2
    0x19959C,  # 3
    0x8B4852,  # 4
    0x395C98,  # 5
    0xA9C1FF,  # 6
    0xEEEEEE,  # 7
    0xD4186C,  # 8
    0xD38411,  # 9
    0xE9C35B,  # 10
    0x70C6A9,  # 11
    0x7696DE,  # 12
    0xA3A3A3,  # 13
    0xFF9798,  # 14
    0xEDCF80,  # 15
]


class EditorScreen:
    # =====================================================
    # 基本設定
    # =====================================================

    SCREEN_WIDTH = 256
    SCREEN_HEIGHT = 256

    BACK_BUTTON = [
        4,
        4,
        32,
        12
    ]

    # パターンそのもののサイズ
    PATTERN_SIZE_LIST = [8, 16, 32, 48]

    # 中央の入力枠の表示サイズ
    # パターンサイズとは別に変更できる
    FRAME_SIZE_LIST = [64, 96, 128, 160]

    # 中央入力枠の上端
    EDITOR_Y = 37

    # パレット
    PALETTE_CELL_SIZE = 14
    PALETTE_X = 16
    PALETTE_Y = 236

    # ツール
    TOOL_CELL_SIZE = 15
    TOOL_X = 4
    TOOL_Y = 20
    TOOL_PEN = 0
    TOOL_FILL = 1
    TOOL_LINE = 2
    TOOL_RECT_LINE = 3
    TOOL_RECT_FILL = 4
    TOOL_CIR_LINE = 5
    TOOL_CIR_FILL = 6
    TOOL_SPUIT = 7
    TOOL_MOVE = 8
    # TOOL_SELECT = 9
    TOOLS = [
        TOOL_PEN,
        TOOL_FILL,
        TOOL_LINE,
        TOOL_RECT_LINE,
        TOOL_RECT_FILL,
        TOOL_CIR_LINE,
        TOOL_CIR_FILL,
        TOOL_SPUIT,
        TOOL_MOVE,
        # TOOL_SELECT
    ]

    MENU_UNDO = 0
    MENU_REDO = 1
    MENU_SAVE = 2
    MENU_EXPORT = 3
    MENU_CELL_SIZE = 15
    MENU_X = 192
    MENU_Y = 20
    MENUS = [
        MENU_UNDO,
        MENU_REDO,
        MENU_SAVE,
        MENU_EXPORT
    ]

    def __init__(self, app, list, id, canvas):
        self.app = app
        self.list = list
        self.id = id
        # pyxel.init(
        #     self.SCREEN_WIDTH,
        #     self.SCREEN_HEIGHT,
        #     title="Pattern Maker",
        #     fps=30,
        # )

        pyxel.mouse(True)
        pyxel.load("assets/asset.pyxres")
        # --------------------
        # CANVAS関連
        # --------------------
        # キャンバス
        self.canvas = []
        # 一時的に表示する仮想的なキャンバス
        self.preview_canvas = []
        # 戻る用のキャンバス
        self.undo_canvases = []
        # 進む用のキャンバス
        self.redo_canvases = []
        # 現在のパターンサイズ
        self.pattern_size = 16

        # 現在の入力枠サイズ
        self.frame_size = 128

        # 選択中の色
        self.selected_color = 7

        # プレビューモード
        self.preview_mode = False
        # ツール一覧の表示
        self.show_tools = True
        # パレット一覧の表示
        self.show_pallet = False

        # 前回描画した論理座標
        self.previous_point = None
        # 開始倫理座標
        self.starting_point = None

        # 選択中のツール
        self.selected_tool = self.TOOL_PEN

        # ステータス状態
        # self.status = None
        self.status_time = 0
        # 初期キャンバス
        # 0番色、つまり黒で埋める
        # self.create_canvas()
        self.canvas = canvas
        self.create_preview_canvas()

        # pyxel.run(self.update, self.draw)

    # =====================================================
    # キャンバス
    # =====================================================

    def create_canvas(self):
        """
        キャンバスを黒で初期化する。
        """

        self.canvas = [
            [0 for _ in range(self.pattern_size)]
            for _ in range(self.pattern_size)
        ]

    def create_preview_canvas(self):
        """
        キャンバスをNoneで初期化する。
        プレビューはNoneが有効
        """

        self.preview_canvas = [
            [None for _ in range(self.pattern_size)]
            for _ in range(self.pattern_size)
        ]

    def clear_canvas(self):
        """
        キャンバスをすべて黒に戻す。
        """

        for y in range(self.pattern_size):
            for x in range(self.pattern_size):
                self.canvas[y][x] = 0

    def clear_preview_canvas(self):
        """
        プレビュー用キャンバスをすべてNoneに戻す。
        """

        for y in range(self.pattern_size):
            for x in range(self.pattern_size):
                self.preview_canvas[y][x] = None

    def change_pattern_size(self, new_size):
        """
        パターンサイズを変更する。

        サイズ変更時は、誤った座標変換を防ぐため
        キャンバスを黒で初期化する。
        """

        if new_size not in self.PATTERN_SIZE_LIST:
            return

        if new_size == self.pattern_size:
            return

        self.pattern_size = new_size
        self.previous_point = None
        self.create_canvas()
        self.create_preview_canvas()

    def change_frame_size(self, new_size):
        """
        中央の入力枠の表示サイズだけを変更する。
        パターンの論理サイズは変更しない。
        FRAME_SIZE_LIST = [64, 96, 128, 160]
        """

        # if new_size not in self.FRAME_SIZE_LIST:
        #     return
        if not (52 <= new_size < 200):
            return

        self.frame_size = new_size
        self.previous_point = None

    def register_undo(self):
        """
        キャンバスをundoへ登録する
        """
        
        self.undo_canvases.append(deepcopy(self.canvas))

    def register_redo(self):
        """
        キャンバスをundoへ登録する
        """

        self.redo_canvases.append(deepcopy(self.canvas))

    def undo_canvas(self):
        """
        キャンバスをひとつ前の状態に戻す
        """
        if self.undo_canvases:
            self.register_redo()
            self.canvas = self.undo_canvases.pop()

    def redo_canvas(self):
        """
        キャンバスをひとつ先の状態に進める
        """
        if self.redo_canvases:
            self.register_undo()
            self.canvas = self.redo_canvases.pop()

    def reset_undo(self):
        self.undo_canvases = []
    def reset_redo(self):
        self.redo_canvases = []

    # =====================================================
    # 座標変換
    # =====================================================

    def editor_x(self):
        """
        中央入力枠の左端を返す。
        """

        return (
            self.SCREEN_WIDTH - self.frame_size
        ) // 2

    def editor_y(self):
        """
        中央入力枠の上端を返す。
        """

        return (
            self.SCREEN_HEIGHT - self.frame_size
        ) // 2

    def screen_to_canvas(self, screen_x, screen_y):
        """
        画面座標をキャンバスの論理座標へ変換する。
        """

        editor_x = self.editor_x()

        if not (
            editor_x <= screen_x < editor_x + self.frame_size
            and self.editor_y() <= screen_y < self.editor_y() + self.frame_size
        ):
            return None

        x = (
            (screen_x - editor_x)
            * self.pattern_size
            // self.frame_size
        )

        y = (
            (screen_y - self.editor_y())
            * self.pattern_size
            // self.frame_size
        )

        if 0 <= x < self.pattern_size and 0 <= y < self.pattern_size:
            return x, y

        return None

    # =====================================================
    # 更新処理
    # =====================================================

    def update(self):
        before_canvas = deepcopy(self.canvas)
        # ---------------------------------------------
        # 一覧画面へ戻る
        # ---------------------------------------------
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            x, y, w, h = self.BACK_BUTTON
            if (
                x < pyxel.mouse_x <= x + w
                and y < pyxel.mouse_y <= y + h
            ):
                self.app.change_screen(self.app.SCREEN_LIST)
        # ---------------------------------------------
        # メニュークリック
        # ---------------------------------------------
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            menu = self.get_select_menu(
                pyxel.mouse_x,
                pyxel.mouse_y,
            )

            if menu is not None:
                if menu == self.MENU_UNDO:
                    self.undo_canvas()
                elif menu == self.MENU_REDO:
                    self.redo_canvas()
                elif menu == self.MENU_SAVE:
                    self.save_canvas()
                elif menu == self.MENU_EXPORT:
                    self.export_png()
                # if self.show_tools:
                #     if self.selected_tool == tool:
                #         self.show_tools = False
                #     self.selected_tool = tool
                #     self.previous_point = None
                #     return
                # else:
                #     if self.selected_tool == tool:
                #         self.show_tools = True

        # ---------------------------------------------
        # プレビューモード
        # ---------------------------------------------

        if pyxel.btnp(pyxel.KEY_P):
            self.preview_mode = not self.preview_mode
            self.previous_point = None
            return

        # プレビューモード時は何も受け付けない。
        if self.preview_mode:
            return
        # ---------------------------------------------
        # Undo, Redo 関連の処理
        # ---------------------------------------------
        if (
            # pyxel.btnp(pyxel.KEY_B, hold=15, repeat=1)
            pyxel.btn(pyxel.KEY_CTRL)
            and not pyxel.btn(pyxel.KEY_SHIFT)
            and pyxel.btnp(pyxel.KEY_Z)
        ):
            self.undo_canvas()
            return

        if (
            # pyxel.btnp(pyxel.KEY_N, hold=15, repeat=1)
            # pyxel.btn(pyxel.KEY_GUI)
            pyxel.btn(pyxel.KEY_CTRL)
            and pyxel.btn(pyxel.KEY_SHIFT)
            and pyxel.btnp(pyxel.KEY_Z)
        ):
            self.redo_canvas()
            return

        # ---------------------------------------------
        # パターンサイズ変更
        # ---------------------------------------------

        # if pyxel.btnp(pyxel.KEY_1):
        #     self.change_pattern_size(8)

        # if pyxel.btnp(pyxel.KEY_2):
        #     self.change_pattern_size(16)

        # if pyxel.btnp(pyxel.KEY_3):
        #     self.change_pattern_size(32)

        # if pyxel.btnp(pyxel.KEY_4):
        #     self.change_pattern_size(48)

        # ---------------------------------------------
        # 入力枠サイズ変更
        # ---------------------------------------------

        if pyxel.btnp(pyxel.KEY_Q):
            self.change_frame_size(64)

        if pyxel.btnp(pyxel.KEY_W):
            self.change_frame_size(96)

        if pyxel.btnp(pyxel.KEY_E):
            self.change_frame_size(128)

        if pyxel.btnp(pyxel.KEY_R):
            self.change_frame_size(160)

        if pyxel.btn(pyxel.KEY_UP):
            self.change_frame_size(self.frame_size + 4)
        if pyxel.btn(pyxel.KEY_DOWN):
            self.change_frame_size(self.frame_size - 4)
        # ---------------------------------------------
        # 色変更
        # ---------------------------------------------

        if (
            not pyxel.btn(pyxel.KEY_ALT)
            and pyxel.btnp(pyxel.KEY_LEFT)
        ):
            self.selected_color = (
                self.selected_color - 1
            ) % 16

        if (
            not pyxel.btn(pyxel.KEY_ALT)
            and pyxel.btnp(pyxel.KEY_RIGHT)
        ):
            self.selected_color = (
                self.selected_color + 1
            ) % 16

        # ---------------------------------------------
        # ツール変更
        # ---------------------------------------------

        if (
            pyxel.btn(pyxel.KEY_ALT)
            and pyxel.btnp(pyxel.KEY_LEFT)
        ):
            self.selected_tool = (
                self.selected_tool - 1
            ) % len(self.TOOLS)

        if (
            pyxel.btn(pyxel.KEY_ALT)
            and pyxel.btnp(pyxel.KEY_RIGHT)
        ):
            self.selected_tool = (
                self.selected_tool + 1
            ) % len(self.TOOLS)

        # ---------------------------------------------
        # パレットクリック
        # ---------------------------------------------

        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            palette_color = self.get_palette_color(
                pyxel.mouse_x,
                pyxel.mouse_y,
            )

            if palette_color is not None:
                self.selected_color = palette_color
                self.previous_point = None
                return

        # ---------------------------------------------
        # ツールクリック
        # ---------------------------------------------

        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            tool = self.get_select_tool(
                pyxel.mouse_x,
                pyxel.mouse_y,
            )

            if tool is not None:
                if self.show_tools:
                    if self.selected_tool == tool:
                        self.show_tools = False
                    self.selected_tool = tool
                    self.previous_point = None
                    return
                else:
                    if self.selected_tool == tool:
                        self.show_tools = True

        # ---------------------------------------------
        # 左クリックで描画
        # ---------------------------------------------

        current_point = self.screen_to_canvas(
            pyxel.mouse_x,
            pyxel.mouse_y,
        )

        if current_point is not None:
            # ----------
            # ペンツール
            # ----------
            if self.selected_tool == self.TOOL_PEN:
                if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                    self.register_undo()
                    self.reset_redo()
                    self.starting_point = current_point
                if self.starting_point is not None:
                    if pyxel.btn(pyxel.MOUSE_BUTTON_LEFT):
                        if self.previous_point is None:
                            self.paint_point(
                                current_point[0],
                                current_point[1],
                                self.selected_color,
                            )
                        else:
                            self.paint_line(
                                self.previous_point,
                                current_point,
                                self.selected_color,
                            )

                        self.previous_point = current_point
                    else:
                        self.previous_point = None
                    if pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT):
                        self.starting_point = None
                
            # ----------
            # 塗りつぶしツール
            # ----------
            elif self.selected_tool == self.TOOL_FILL:
                if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                    self.register_undo()
                    self.reset_redo()
                if pyxel.btn(pyxel.MOUSE_BUTTON_LEFT):
                    start_x, start_y = current_point[0], current_point[1]

                    # クリックしたセルの元の色
                    target_color = self.canvas[start_y][start_x]

                    # すでに選択色なら何もしない
                    if target_color != self.selected_color:
                        fill_cells = [(start_x, start_y)]
                        visited = set()

                        directions = [
                            (0, -1),  # 上
                            (-1, 0),  # 左
                            (1, 0),   # 右
                            (0, 1),   # 下
                        ]

                        while fill_cells:
                            x, y = fill_cells.pop(0)

                            # 同じセルを二重処理しない
                            if (x, y) in visited:
                                continue

                            # 枠外ならスキップ
                            if not (
                                0 <= x < self.pattern_size
                                and 0 <= y < self.pattern_size
                            ):
                                continue

                            # 元の色ではないセルには到達しない
                            if self.canvas[y][x] != target_color:
                                continue

                            visited.add((x, y))

                            # セルを塗る
                            self.paint_point(
                                x,
                                y,
                                self.selected_color,
                            )

                            # 上下左右を追加
                            for dx, dy in directions:
                                next_x = x + dx
                                next_y = y + dy

                                if (next_x, next_y) not in visited:
                                    fill_cells.append((next_x, next_y))

            # ----------
            # 線ツール
            # ----------
            elif self.selected_tool == self.TOOL_LINE:
                if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                    self.register_undo()
                    self.reset_redo()
                    self.starting_point = current_point
                if self.starting_point is not None:
                    if pyxel.btn(pyxel.MOUSE_BUTTON_LEFT):
                        self.clear_preview_canvas()
                        self.paint_line(
                            self.starting_point,
                            current_point,
                            self.selected_color,
                            preview=True
                        )
                    if pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT):
                        self.paint_line(
                            self.starting_point,
                            current_point,
                            self.selected_color,
                        )
                        self.starting_point = None
                        self.clear_preview_canvas()
            # ----------
            # 四角（線）ツール
            # ----------
            elif self.selected_tool == self.TOOL_RECT_LINE:
                if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                    self.register_undo()
                    self.reset_redo()
                    self.starting_point = current_point
                if self.starting_point is not None:
                    if pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT):
                        self.paint_rect_line(
                            self.starting_point,
                            current_point,
                            self.selected_color,
                        )
                        self.starting_point = None
                        self.clear_preview_canvas()
                    if pyxel.btn(pyxel.MOUSE_BUTTON_LEFT):
                        self.clear_preview_canvas()
                        self.paint_rect_line(
                            self.starting_point,
                            current_point,
                            self.selected_color,
                            preview=True
                        )
            # ----------
            # 四角（塗りつぶし）ツール
            # ----------
            elif self.selected_tool == self.TOOL_RECT_FILL:
                if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                    self.register_undo()
                    self.reset_redo()
                    self.starting_point = current_point
                if self.starting_point is not None:
                    if pyxel.btn(pyxel.MOUSE_BUTTON_LEFT):
                        self.clear_preview_canvas()
                        self.paint_rect_fill(
                            self.starting_point,
                            current_point,
                            self.selected_color,
                            preview=True
                        )
                    if pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT):
                        self.paint_rect_fill(
                            self.starting_point,
                            current_point,
                            self.selected_color,
                        )
                        self.starting_point = None
                        self.clear_preview_canvas()
            # ----------
            # 円（線）ツール
            # ----------
            elif self.selected_tool == self.TOOL_CIR_LINE:
                if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                    self.register_undo()
                    self.reset_redo()
                    self.starting_point = current_point
                if self.starting_point is not None:
                    if pyxel.btn(pyxel.MOUSE_BUTTON_LEFT):
                        self.clear_preview_canvas()
                        self.paint_cir_line(
                            self.starting_point,
                            current_point,
                            self.selected_color,
                            preview=True
                        )
                    if pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT):
                        self.paint_cir_line(
                            self.starting_point,
                            current_point,
                            self.selected_color,
                        )
                        self.starting_point = None
                        self.clear_preview_canvas()
            # ----------
            # 円（塗りつぶし）ツール
            # ----------
            elif self.selected_tool == self.TOOL_CIR_FILL:
                if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                    self.register_undo()
                    self.reset_redo()
                    self.starting_point = current_point
                if self.starting_point is not None:
                    if pyxel.btn(pyxel.MOUSE_BUTTON_LEFT):
                        self.clear_preview_canvas()
                        self.paint_cir_fill(
                            self.starting_point,
                            current_point,
                            self.selected_color,
                            preview=True
                        )
                    if pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT):
                        self.paint_cir_fill(
                            self.starting_point,
                            current_point,
                            self.selected_color,
                        )
                        self.starting_point = None
                        self.clear_preview_canvas()
            # ----------
            # スポイトツール
            # ----------
            elif self.selected_tool == self.TOOL_SPUIT:
                if pyxel.btn(pyxel.MOUSE_BUTTON_LEFT):
                    x, y = current_point[0], current_point[1]
                    color = self.canvas[y][x]
                    self.selected_color = color
            # ----------
            # 移動ツール
            # ----------
            elif self.selected_tool == self.TOOL_MOVE:
                if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                    self.register_undo()
                    self.reset_redo()
                    self.starting_point = current_point
                if self.starting_point is not None:
                    if pyxel.btn(pyxel.MOUSE_BUTTON_LEFT):
                        start_x, start_y = self.starting_point
                        current_x, current_y = current_point

                        # 座標の差分
                        diff_x = current_x - start_x
                        diff_y = current_y - start_y

                        # 横方向の移動
                        if diff_x > 0:
                            for _ in range(diff_x):
                                self.move_to_right()

                        elif diff_x < 0:
                            for _ in range(-diff_x):
                                self.move_to_left()

                        # 縦方向の移動
                        if diff_y > 0:
                            for _ in range(diff_y):
                                self.move_to_down()

                        elif diff_y < 0:
                            for _ in range(-diff_y):
                                self.move_to_up()

                        self.starting_point = current_point
                    if pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT):
                        self.starting_point = None

        else:
            # 以下枠外にあるとき・・・（変更するかも）
            self.previous_point = None
            self.clear_preview_canvas()

        # ---------------------------------------------
        # 全消去
        # ---------------------------------------------

        if pyxel.btnp(pyxel.KEY_C):
            self.clear_canvas()
            self.clear_preview_canvas()

        # ---------------------------------------------
        # ファイル出力
        # ---------------------------------------------

        if pyxel.btnp(pyxel.KEY_S):
            self.export_png()
            # self.export_text()

    # =====================================================
    # 描画データ変更
    # =====================================================

    def paint_point(self, x, y, color, preview=False):
        """
        指定した1ドットだけを変更する。

        """

        if not (
            0 <= x < self.pattern_size
            and 0 <= y < self.pattern_size
        ):
            return

        if not preview:
            self.canvas[y][x] = color
        else:
            self.preview_canvas[y][x] = color

    def paint_line(self, start, end, color, preview=False):
        """
        直線を引く。
        前回位置と現在位置の間を補間して描画する。
        マウスを速く動かしたときに、途中のドットが
        抜けるのを防ぐのにも有効
        """
        x1, y1 = start
        x2, y2 = end

        dx = x2 - x1
        dy = y2 - y1

        distance = max(abs(dx), abs(dy))

        if distance == 0:
            self.paint_point(x1, y1, color, preview)
            return

        for i in range(distance + 1):
            x = round(
                x1 + dx * i / distance
            )
            y = round(
                y1 + dy * i / distance
            )
            self.paint_point(x, y, color, preview)

    def paint_rect_line(self, start, end, color, preview=False):
        """
        四角形の枠線を描く。
        start と end は、対角線上の2点。
        """
        x1, y1 = start
        x2, y2 = end

        # 四隅の座標
        top_left = (x1, y1)
        top_right = (x2, y1)
        bottom_left = (x1, y2)
        bottom_right = (x2, y2)

        # 上辺
        self.paint_line(
            top_left,
            top_right,
            color,
            preview
        )

        # 右辺
        self.paint_line(
            top_right,
            bottom_right,
            color,
            preview
        )

        # 下辺
        self.paint_line(
            bottom_right,
            bottom_left,
            color,
            preview
        )

        # 左辺
        self.paint_line(
            bottom_left,
            top_left,
            color,
            preview
        )

    def paint_rect_fill(self, start, end, color, preview=False):
        """
        四角形を塗りつぶす。
        start と end は、対角線上の2点。
        """
        x1, y1 = start
        x2, y2 = end

        # 左右・上下の順番を正規化
        left = min(x1, x2)
        right = max(x1, x2)
        top = min(y1, y2)
        bottom = max(y1, y2)

        # 各行を横方向に描画
        for y in range(top, bottom + 1):
            self.paint_line(
                (left, y),
                (right, y),
                color,
                preview
            )

    def paint_cir_line(self, start, end, color, preview=False):
        """
        左上のカーブを基準に、上下左右対称な楕円を描く。
        """
        x1, y1 = start
        x2, y2 = end

        left = min(x1, x2)
        right = max(x1, x2)
        top = min(y1, y2)
        bottom = max(y1, y2)

        center_x = (left + right) / 2
        center_y = (top + bottom) / 2

        radius_x = (right - left) / 2
        radius_y = (bottom - top) / 2

        if radius_x == 0 and radius_y == 0:
            self.paint_point(
                round(center_x),
                round(center_y),
                color,
                preview
            )
            return

        pixels = set()

        # 左上の1/4だけを作る
        steps = max(90, round(max(radius_x, radius_y) * 8))

        previous = None

        for i in range(steps + 1):
            # 180度から270度が左上側
            angle = 180 + i * 90 / steps

            x = round(
                center_x + radius_x * pyxel.cos(angle)
            )
            y = round(
                center_y + radius_y * pyxel.sin(angle)
            )

            current = (x, y)

            if previous is None:
                pixels.add(current)
            else:
                self.add_line_pixels(
                    pixels,
                    previous,
                    current
                )

            previous = current

        # 左上のカーブに対して、上下左右対称に配置
        mirrored_pixels = set()

        for x, y in pixels:
            mirrored_pixels.add((x, y))
            mirrored_pixels.add((
                round(2 * center_x - x),
                y
            ))
            mirrored_pixels.add((
                x,
                round(2 * center_y - y)
            ))
            mirrored_pixels.add((
                round(2 * center_x - x),
                round(2 * center_y - y)
            ))

        # L字を対称に除去
        mirrored_pixels = self.remove_l_shapes_symmetric(
            mirrored_pixels,
            center_x,
            center_y
        )

        for x, y in mirrored_pixels:
            self.paint_point(x, y, color, preview)


    def add_line_pixels(self, pixels, start, end):
        """
        2点間のドットを pixels に追加する。
        """
        x1, y1 = start
        x2, y2 = end

        dx = x2 - x1
        dy = y2 - y1

        distance = max(abs(dx), abs(dy))

        if distance == 0:
            pixels.add(start)
            return

        for i in range(distance + 1):
            x = round(x1 + dx * i / distance)
            y = round(y1 + dy * i / distance)
            pixels.add((x, y))

    def remove_l_shapes_symmetric(self, pixels, center_x, center_y):
        """
        2×2のL字を整理する。

        円の中心に近いドットから削除するが、
        削除によって円周が途切れる場合は削除しない。
        """
        pixels = set(pixels)

        def symmetric_pixels(x, y):
            return {
                (x, y),
                (round(2 * center_x - x), y),
                (x, round(2 * center_y - y)),
                (
                    round(2 * center_x - x),
                    round(2 * center_y - y)
                ),
            }

        def is_connected(target):
            """
            ドット群が8方向でつながっているか確認する。
            """
            if not target:
                return False

            start = next(iter(target))
            visited = {start}
            stack = [start]

            directions = (
                (-1, -1), (0, -1), (1, -1),
                (-1,  0),          (1,  0),
                (-1,  1), (0,  1), (1,  1),
            )

            while stack:
                x, y = stack.pop()

                for dx, dy in directions:
                    next_pixel = (x + dx, y + dy)

                    if (
                        next_pixel in target
                        and next_pixel not in visited
                    ):
                        visited.add(next_pixel)
                        stack.append(next_pixel)

            return len(visited) == len(target)

        while True:
            candidates = []

            for x, y in pixels:
                block = {
                    (x, y),
                    (x + 1, y),
                    (x, y + 1),
                    (x + 1, y + 1),
                }

                present = block & pixels

                if len(present) != 3:
                    continue

                # L字を構成しているドットを候補にする
                for px, py in present:
                    distance = (
                        (px - center_x) ** 2
                        + (py - center_y) ** 2
                    )

                    candidates.append((
                        distance,
                        px,
                        py
                    ))

            if not candidates:
                break

            # 中心に近いドットから調べる
            candidates.sort(
                key=lambda item: item[0]
            )

            removed = False

            for _, remove_x, remove_y in candidates:
                remove_pixels = symmetric_pixels(
                    remove_x,
                    remove_y
                )

                new_pixels = pixels - remove_pixels

                # 削除後も円周がつながる場合だけ削除する
                if is_connected(new_pixels):
                    pixels = new_pixels
                    removed = True
                    break

            # どの候補も削除できなければ終了
            if not removed:
                break

        return pixels

    def paint_cir_fill(self, start, end, color, preview=False):
        """
        左上のカーブを基準に、上下左右対称な楕円を塗りつぶす。
        """
        x1, y1 = start
        x2, y2 = end

        left = min(x1, x2)
        right = max(x1, x2)
        top = min(y1, y2)
        bottom = max(y1, y2)

        center_x = (left + right) / 2
        center_y = (top + bottom) / 2

        radius_x = (right - left) / 2
        radius_y = (bottom - top) / 2

        if radius_x == 0 and radius_y == 0:
            self.paint_point(
                round(center_x),
                round(center_y),
                color,
                preview
            )
            return

        pixels = set()

        # 左上の1/4だけを作る
        steps = max(
            90,
            round(max(radius_x, radius_y) * 8)
        )

        previous = None

        for i in range(steps + 1):
            # 180度から270度が左上側
            angle = 180 + i * 90 / steps

            x = round(
                center_x + radius_x * pyxel.cos(angle)
            )
            y = round(
                center_y + radius_y * pyxel.sin(angle)
            )

            current = (x, y)

            if previous is None:
                pixels.add(current)
            else:
                self.add_line_pixels(
                    pixels,
                    previous,
                    current
                )

            previous = current

        # 左上のカーブを上下左右に反転
        mirrored_pixels = set()

        for x, y in pixels:
            mirrored_pixels.add((x, y))

            mirrored_pixels.add((
                round(2 * center_x - x),
                y
            ))

            mirrored_pixels.add((
                x,
                round(2 * center_y - y)
            ))

            mirrored_pixels.add((
                round(2 * center_x - x),
                round(2 * center_y - y)
            ))

        # L字を対称に除去
        mirrored_pixels = self.remove_l_shapes_symmetric(
            mirrored_pixels,
            center_x,
            center_y
        )

        # 行ごとに左右端を調べて、横線で塗りつぶす
        rows = {}

        for x, y in mirrored_pixels:
            if y not in rows:
                rows[y] = []

            rows[y].append(x)

        for y, xs in rows.items():
            line_left = min(xs)
            line_right = max(xs)

            self.paint_line(
                (line_left, y),
                (line_right, y),
                color,
                preview
            )


    def move_to_up(self):
        if self.canvas:
            self.canvas = self.canvas[1:] + self.canvas[:1]

    def move_to_down(self):
        if self.canvas:
            self.canvas = self.canvas[-1:] + self.canvas[:-1]

    def move_to_right(self):
        for y in range(len(self.canvas)):
            if self.canvas[y]:
                self.canvas[y] = self.canvas[y][-1:] + self.canvas[y][:-1]

    def move_to_left(self):
        for y in range(len(self.canvas)):
            if self.canvas[y]:
                self.canvas[y] = self.canvas[y][1:] + self.canvas[y][:1]



    # =====================================================
    # 描画
    # =====================================================

    def draw(self):
        pyxel.cls(0)

        if self.preview_mode:
            self.draw_preview()
        else:
            self.draw_pattern()
            self.draw_preview_pattern()
            self.draw_palette()
            self.draw_tools()
            self.draw_menus()
            self.draw_header()
            self.draw_status()
            # self.draw_footer()
        # pyxel.text(0, 0, f"undo: {len(self.undo_canvases)}", 7)
        # pyxel.text(100, 0, f"redo: {len(self.redo_canvases)}", 7)

    def draw_text_shadow(self, x, y, text, color=7):
        """
        文字の右下に黒い影を付ける。
        """

        pyxel.text(
            x + 1,
            y + 1,
            text,
            0,
        )

        pyxel.text(
            x,
            y,
            text,
            color,
        )

    def draw_header(self):
        pyxel.rect(
            self.BACK_BUTTON[0],
            self.BACK_BUTTON[1],
            self.BACK_BUTTON[2],
            self.BACK_BUTTON[3],
            1
        )
        self.draw_text_shadow(
            8,
            7,
            "< BACK",
            7,
        )
    def draw_pattern(self):
        """
        中央の入力枠と、その周囲の繰り返しパターンを描画する。
        """

        editor_x = self.editor_x()
        editor_y = self.editor_y()

        # 周囲を5×5で描画
        for tile_y in range(-2, 3):
            for tile_x in range(-2, 3):
                left = editor_x + (
                    tile_x * self.frame_size
                )

                top = editor_y + (
                    tile_y * self.frame_size
                )

                self.draw_tile(left, top)

        # 中央のガイド線を表示
        # 縦
        pyxel.line(
            editor_x + (self.frame_size // 2) - 1,
            editor_y - 1,
            editor_x + (self.frame_size // 2) - 1,
            editor_y + self.frame_size - 1,
            1
        )
        # 横
        pyxel.line(
            editor_x - 1,
            editor_y + (self.frame_size // 2) - 1,
            editor_x + self.frame_size - 1,
            editor_y + (self.frame_size // 2) - 1,
            1
        )

        # 中央の入力枠を強調
        pyxel.rectb(
            editor_x - 1,
            editor_y - 1,
            self.frame_size + 2,
            self.frame_size + 2,
            7,
        )

    def draw_preview_pattern(self):
        """
        パターンの入力中のプレビュー部分を描画する。
        """

        editor_x = self.editor_x()
        editor_y = self.editor_y()

        self.draw_tile(editor_x, editor_y, preview=True)

    def draw_tile(self, tile_x, tile_y, preview=False):
        """
        1枚分のパターンを描画する。
        """

        if not preview:
            canvas = self.canvas
        else:
            canvas = self.preview_canvas
        for y in range(self.pattern_size):
            for x in range(self.pattern_size):
                if canvas[y][x] is None:
                    continue
                color = canvas[y][x]

                left = tile_x + (
                    x * self.frame_size
                    // self.pattern_size
                )

                top = tile_y + (
                    y * self.frame_size
                    // self.pattern_size
                )

                right = tile_x + (
                    (x + 1) * self.frame_size
                    // self.pattern_size
                ) - 1

                bottom = tile_y + (
                    (y + 1) * self.frame_size
                    // self.pattern_size
                ) - 1

                width = right - left + 1
                height = bottom - top + 1

                if width > 0 and height > 0:
                    pyxel.rect(
                        left,
                        top,
                        width,
                        height,
                        color,
                    )

        # タイルの枠
        pyxel.rectb(
            tile_x,
            tile_y,
            self.frame_size,
            self.frame_size,
            1,
        )

    def draw_palette(self):
        """
        16色パレットを表示する。
        """

        for color in range(16):
            x = (
                self.PALETTE_X
                + color * self.PALETTE_CELL_SIZE
            )

            pyxel.rect(
                x,
                self.PALETTE_Y,
                self.PALETTE_CELL_SIZE - 2,
                self.PALETTE_CELL_SIZE - 2,
                color,
            )

            # 選択中の色
            if color == self.selected_color:
                pyxel.rectb(
                    x - 1,
                    self.PALETTE_Y - 1,
                    self.PALETTE_CELL_SIZE,
                    self.PALETTE_CELL_SIZE,
                    7 if pyxel.frame_count // 20 % 2 == 0 else 10,
                )

        # パレットサイズ表示
        # self.draw_text_shadow(
        #     8,
        #     202,
        #     "PALETTE: 16 COLORS",
        #     7,
        # )

    def draw_tools(self):
        """
        ツールを表示する。
        """

        if self.show_tools:
            for tool in range(len(self.TOOLS)):
                x = (
                    self.TOOL_X
                    + tool * self.TOOL_CELL_SIZE
                )
                pyxel.pal(5, 0)
                pyxel.blt(
                    x+1,
                    self.TOOL_Y+1,
                    0,
                    tool * 16,
                    0,
                    self.TOOL_CELL_SIZE-2,
                    self.TOOL_CELL_SIZE-2,
                    10
                )
                pyxel.pal()
                if tool == self.selected_tool:
                    pyxel.pal(5, 7)
                pyxel.blt(
                    x,
                    self.TOOL_Y,
                    0,
                    tool * 16,
                    0,
                    self.TOOL_CELL_SIZE-2,
                    self.TOOL_CELL_SIZE-2,
                    10
                )
                pyxel.pal()

            # self.draw_text_shadow(
            #     self.TOOL_X,
            #     self.TOOL_Y-7,
            #     "TOOLS",
            #     7,
            # )
        else:
            tool = self.TOOLS[self.selected_tool]
            pyxel.pal(5, 7)
            pyxel.blt(
                self.TOOL_X,
                self.TOOL_Y,
                0,
                tool * 16,
                0,
                self.TOOL_CELL_SIZE-2,
                self.TOOL_CELL_SIZE-2,
                10
            )
            pyxel.pal()

    def draw_menus(self):
        for menu in range(len(self.MENUS)):
            x = (
                self.MENU_X
                + menu * self.MENU_CELL_SIZE
            )
            y = self.MENU_Y
            pyxel.pal(5, 0)
            pyxel.blt(
                x+1,
                y+1,
                0,
                menu * 16,
                16,
                self.MENU_CELL_SIZE-2,
                self.MENU_CELL_SIZE-2,
                10
            )
            pyxel.pal()
            if (
                pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT)
                and x <= pyxel.mouse_x < x+self.MENU_CELL_SIZE
                and y <= pyxel.mouse_y < y+self.MENU_CELL_SIZE
            ):
                pyxel.pal(5, 7)
            pyxel.blt(
                x,
                y,
                0,
                menu * 16,
                16,
                self.MENU_CELL_SIZE-2,
                self.MENU_CELL_SIZE-2,
                10
            )
            pyxel.pal()

    def draw_footer(self):
        self.draw_text_shadow(
            8,
            229,
            "1-4: PATTERN SIZE",
            7,
        )

        self.draw_text_shadow(
            8,
            239,
            "Q-R: FRAME SIZE",
            7,
        )

        self.draw_text_shadow(
            8,
            249,
            "P: PREVIEW  S: SAVE",
            7,
        )

    # =====================================================
    # プレビューモード
    # =====================================================

    def draw_preview(self):
        """
        パターンを等倍で画面全体に繰り返し表示する。
        キャンバスの1ドットを、画面上の1ピクセルとして描画する。
        """

        # 等倍表示
        scale = 1
        tile_size = self.pattern_size

        # 画面全体を覆うため、左右・上下に余分に描画する
        tile_count_x = (
            self.SCREEN_WIDTH // tile_size
        ) + 2

        tile_count_y = (
            self.SCREEN_HEIGHT // tile_size
        ) + 2

        for tile_y in range(-1, tile_count_y):
            for tile_x in range(-1, tile_count_x):
                tile_left = tile_x * tile_size
                tile_top = tile_y * tile_size

                for y in range(self.pattern_size):
                    for x in range(self.pattern_size):
                        color = self.canvas[y][x]

                        pyxel.pset(
                            tile_left + x,
                            tile_top + y,
                            color,
                        )

        # 操作説明を表示する場合
        # self.draw_text_shadow(
        #     8,
        #     8,
        #     f"PREVIEW: {self.pattern_size} x {self.pattern_size}",
        #     7,
        # )

        # self.draw_text_shadow(
        #     8,
        #     19,
        #     "P : BACK",
        #     7,
        # )
    
    def draw_status(self):
        """
        保存状態のステータスを返す
        """
        s = "SAVED"
        if (
            self.status_time > 0
            and pyxel.frame_count < self.status_time+60
            ):
            pyxel.text(
                pyxel.mouse_x-10,
                pyxel.mouse_y+10,
                s,
                pyxel.rndi(1, 15),
                self.app.font
            )

    # =====================================================
    # パレット
    # =====================================================

    def get_palette_color(self, mouse_x, mouse_y):
        """
        クリックされたパレット色を返す。
        パレット外ならNoneを返す。
        """

        palette_width = (
            self.PALETTE_CELL_SIZE * 16
        )

        if not (
            self.PALETTE_X <= mouse_x
            < self.PALETTE_X + palette_width
            and self.PALETTE_Y <= mouse_y
            < self.PALETTE_Y + self.PALETTE_CELL_SIZE
        ):
            return None

        color = (
            mouse_x - self.PALETTE_X
        ) // self.PALETTE_CELL_SIZE

        if 0 <= color < 16:
            return color

        return None

    # =====================================================
    # ツール
    # =====================================================

    def get_select_tool(self, mouse_x, mouse_y):
        """
        クリックされたツールを返す。
        ツール外ならNoneを返す。
        """

        if self.show_tools:
            tool_width = (
                self.TOOL_CELL_SIZE * len(self.TOOLS)
            )

            if not (
                self.TOOL_X <= mouse_x
                < self.TOOL_X + tool_width
                and self.TOOL_Y <= mouse_y
                < self.TOOL_Y + self.TOOL_CELL_SIZE
            ):
                return None

            tool = (
                mouse_x - self.TOOL_X
            ) // self.TOOL_CELL_SIZE

            if 0 <= tool < len(self.TOOLS):
                return tool

            return None
        else:
            tool_width = self.TOOL_CELL_SIZE

            if not (
                self.TOOL_X <= mouse_x
                < self.TOOL_X + tool_width
                and self.TOOL_Y <= mouse_y
                < self.TOOL_Y + self.TOOL_CELL_SIZE
            ):
                return None
            
            tool = self.selected_tool
            return tool

    # =====================================================
    # メニュー
    # =====================================================

    def get_select_menu(self, mouse_x, mouse_y):
        """
        クリックされたメニューを返す。
        ツール外ならNoneを返す。
        """

        menu_width = (
            self.MENU_CELL_SIZE * len(self.MENUS)
        )

        if not (
            self.MENU_X <= mouse_x
            < self.MENU_X + menu_width
            and self.MENU_Y <= mouse_y
            < self.MENU_Y + self.MENU_CELL_SIZE
        ):
            return None

        menu = (
            mouse_x - self.MENU_X
        ) // self.MENU_CELL_SIZE

        if 0 <= menu < len(self.MENUS):
            return menu

        return None
    # =====================================================
    # キャンバスの保存
    # =====================================================
    def save_canvas(self):
        self.list.save_canvas(
            self.id,
            self.canvas
        )
        self.status_time = pyxel.frame_count



    # =====================================================
    # PNG出力
    # =====================================================

    def export_png(self):
        """
        パターンをPNGで出力する。
        背景は透明ではなく、すべてRGB形式で出力する。
        """

        output_size = self.pattern_size

        p_image = pyxel.Image(output_size, output_size)

        for y in range(self.pattern_size):
            for x in range(self.pattern_size):
                color_index = self.canvas[y][x]
                # rgb = PYXEL_PALETTE[color_index]

                # red = (rgb >> 16) & 0xFF
                # green = (rgb >> 8) & 0xFF
                # blue = rgb & 0xFF

                p_image.set(x, y, [f"{color_index:X}"])

        # filename = (
        #     f"pattern_{self.pattern_size}x"
        #     f"{self.pattern_size}_3x3.png"
        # )

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"pattern_{timestamp}.png"
        self.download_image(p_image, filename)
        print(f"PNG saved: {filename}")
        print(f"canvas: {self.canvas}")

    # =====================================================
    # テキスト出力
    # =====================================================

    def export_text(self):
        """
        PyxelのImage.set()で利用できる形式で出力する。
        """

        filename = (
            f"pattern_{self.pattern_size}x"
            f"{self.pattern_size}.txt"
        )

        output = "pyxel.image(0).set(0, 0, [\n"

        for y in range(self.pattern_size):
            row = ""

            for x in range(self.pattern_size):
                color = self.canvas[y][x]
                row += format(color, "x")

            comma = "," if y < self.pattern_size - 1 else ""
            output += f'    "{row}"{comma}\n'

        output += "])\n"

        # ファイルに書き込む
        with open(filename, "w", encoding="utf-8") as file:
            file.write(output)

        # 書き込んだ内容を画面に表示
        print(output)

        # print(f"Text saved: {filename}")

    def download_image(self, image, filename):
        path = "/tmp/download.png"

        image.save(path, 1)

        with open(path, "rb") as file:
            data = file.read()

        blob = Blob.new(
            [Uint8Array.new(data)],
            {"type": "image/png"},
        )

        url = URL.createObjectURL(blob)

        link = document.createElement("a")
        link.href = url
        link.download = filename

        document.body.appendChild(link)
        link.click()
        link.remove()

        URL.revokeObjectURL(url)
        os.remove(path)


# if __name__ == "__main__":
#     PatternEditor()
