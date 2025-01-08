import numpy as np
import tkinter as tk
import threading
import random

# ボードのサイズ
BOARD_SIZE = 10

# 初期化
EMPTY = ' '
PLAYER = '❌'
AI = '⭕'

def create_board():
    return np.full((BOARD_SIZE, BOARD_SIZE), EMPTY)

def check_winner(board, symbol):
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE - 4):
            if all(board[i, j+k] == symbol for k in range(5)):  # 横
                return True
            if all(board[j+k, i] == symbol for k in range(5)):  # 縦
                return True

    for i in range(BOARD_SIZE - 4):
        for j in range(BOARD_SIZE - 4):
            if all(board[i+k, j+k] == symbol for k in range(5)):  # 斜め（\）
                return True
            if all(board[i+k, j+4-k] == symbol for k in range(5)):  # 斜め（/）
                return True

    return False

def is_full(board):
    return not np.any(board == EMPTY)

def evaluate_line(line, symbol):
    """指定されたライン（リスト）を評価し、スコアを計算する。"""
    score = 0
    count = 0
    for cell in line:
        if cell == symbol:
            count += 1
        elif cell == EMPTY:
            continue
        else:
            count = 0
        score = max(score, count)
    return score

def evaluate_board(board, symbol):
    """評価関数でスコアを計算する。"""
    score = 0

    # 横方向と縦方向のスコアを計算
    for i in range(BOARD_SIZE):
        score += evaluate_line(board[i, :], symbol)  # 横
        score += evaluate_line(board[:, i], symbol)  # 縦

    # 斜め方向のスコアを計算
    for i in range(BOARD_SIZE - 4):
        for j in range(BOARD_SIZE - 4):
            diag1 = [board[i+k, j+k] for k in range(5)]  # 斜め（\）
            diag2 = [board[i+k, j+4-k] for k in range(5)]  # 斜め（/）
            score += evaluate_line(diag1, symbol)
            score += evaluate_line(diag2, symbol)

    return score

def prevent_player_threat(board):
    """プレイヤーが3つ連続で並んでいる場合に片方を潰す動きを探す。"""
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE - 3):
            # 横方向で阻止
            if sum(board[i, j+k] == PLAYER for k in range(3)) == 3 and any(board[i, j+k] == EMPTY for k in range(4)):
                for k in range(4):
                    if board[i, j+k] == EMPTY:
                        return (i, j+k)
            # 縦方向で阻止
            if sum(board[j+k, i] == PLAYER for k in range(3)) == 3 and any(board[j+k, i] == EMPTY for k in range(4)):
                for k in range(4):
                    if board[j+k, i] == EMPTY:
                        return (j+k, i)

    for i in range(BOARD_SIZE - 3):
        for j in range(BOARD_SIZE - 3):
            # 斜め（\）方向で阻止
            if sum(board[i+k, j+k] == PLAYER for k in range(3)) == 3 and any(board[i+k, j+k] == EMPTY for k in range(4)):
                for k in range(4):
                    if board[i+k, j+k] == EMPTY:
                        return (i+k, j+k)
            # 斜め（/）方向で阻止
            if sum(board[i+k, j+3-k] == PLAYER for k in range(3)) == 3 and any(board[i+k, j+3-k] == EMPTY for k in range(4)):
                for k in range(4):
                    if board[i+k, j+3-k] == EMPTY:
                        return (i+k, j+3-k)

    return None

def prevent_player_win(board):
    """プレイヤーが5マス揃えそうな場合に阻止する動きを探す。"""
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE - 4):
            # 横方向で阻止
            if sum(board[i, j+k] == PLAYER for k in range(5)) == 4 and any(board[i, j+k] == EMPTY for k in range(5)):
                for k in range(5):
                    if board[i, j+k] == EMPTY:
                        return (i, j+k)
            # 縦方向で阻止
            if sum(board[j+k, i] == PLAYER for k in range(5)) == 4 and any(board[j+k, i] == EMPTY for k in range(5)):
                for k in range(5):
                    if board[j+k, i] == EMPTY:
                        return (j+k, i)

    for i in range(BOARD_SIZE - 4):
        for j in range(BOARD_SIZE - 4):
            # 斜め（\）方向で阻止
            if sum(board[i+k, j+k] == PLAYER for k in range(5)) == 4 and any(board[i+k, j+k] == EMPTY for k in range(5)):
                for k in range(5):
                    if board[i+k, j+k] == EMPTY:
                        return (i+k, j+k)
            # 斜め（/）方向で阻止
            if sum(board[i+k, j+4-k] == PLAYER for k in range(5)) == 4 and any(board[i+k, j+4-k] == EMPTY for k in range(5)):
                for k in range(5):
                    if board[i+k, j+4-k] == EMPTY:
                        return (i+k, j+4-k)

    return None

def find_ai_win(board):
    """AIが5マス揃えられる場合にその動きを探す。"""
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE - 4):
            # 横方向で勝利
            if sum(board[i, j+k] == AI for k in range(5)) == 4 and any(board[i, j+k] == EMPTY for k in range(5)):
                for k in range(5):
                    if board[i, j+k] == EMPTY:
                        return (i, j+k)
            # 縦方向で勝利
            if sum(board[j+k, i] == AI for k in range(5)) == 4 and any(board[j+k, i] == EMPTY for k in range(5)):
                for k in range(5):
                    if board[j+k, i] == EMPTY:
                        return (j+k, i)

    for i in range(BOARD_SIZE - 4):
        for j in range(BOARD_SIZE - 4):
            # 斜め（\）方向で勝利
            if sum(board[i+k, j+k] == AI for k in range(5)) == 4 and any(board[i+k, j+k] == EMPTY for k in range(5)):
                for k in range(5):
                    if board[i+k, j+k] == EMPTY:
                        return (i+k, j+k)
            # 斜め（/）方向で勝利
            if sum(board[i+k, j+4-k] == AI for k in range(5)) == 4 and any(board[i+k, j+4-k] == EMPTY for k in range(5)):
                for k in range(5):
                    if board[i+k, j+4-k] == EMPTY:
                        return (i+k, j+4-k)

    return None

def best_move(board):
    """AIの最善手を探索する。"""
    win_move = find_ai_win(board)
    if win_move:
        return win_move

    block_move = prevent_player_win(board)
    if block_move:
        return block_move

    threat_move = prevent_player_threat(board)
    if threat_move:
        return threat_move

    # 戦略的なスコアリング
    best_score = -float('inf')
    possible_moves = []
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if board[i, j] == EMPTY:
                board[i, j] = AI
                score = evaluate_board(board, AI)
                board[i, j] = EMPTY

                if score > best_score:
                    best_score = score
                    possible_moves = [(i, j)]
                elif score == best_score:
                    possible_moves.append((i, j))

    # ランダムに最善の動きを選択
    return random.choice(possible_moves) if possible_moves else None

def main():
    board = create_board()

    def update_board(row, col):
        nonlocal board
        if board[row, col] == EMPTY:
            # プレイヤーのターン
            board[row, col] = PLAYER
            buttons[row][col].config(text=PLAYER, state="disabled")
            turn_label.config(text="現在のターン: AI")
            root.update_idletasks()

            if check_winner(board, PLAYER):
                result_label.config(text="あなたの勝利です！")
                disable_all_buttons()
                return

            if is_full(board):
                result_label.config(text="引き分けです！")
                disable_all_buttons()
                return

            # AIのターンを別スレッドで処理
            threading.Thread(target=ai_turn).start()

    def ai_turn():
        nonlocal board
        ai_move = best_move(board)
        if ai_move:
            board[ai_move] = AI
            buttons[ai_move[0]][ai_move[1]].config(text=AI, state="disabled")
            turn_label.config(text="現在のターン: プレイヤー")
            root.update_idletasks()

        if check_winner(board, AI):
            result_label.config(text="AIの勝利です！")
            disable_all_buttons()
            return

        if is_full(board):
            result_label.config(text="引き分けです！")
            disable_all_buttons()

    def disable_all_buttons():
        for row_buttons in buttons:
            for button in row_buttons:
                button.config(state="disabled")

    # GUIの設定
    root = tk.Tk()
    root.title("五目並べ - プレイヤー vs AI")

    buttons = []
    for i in range(BOARD_SIZE):
        row_buttons = []
        for j in range(BOARD_SIZE):
            button = tk.Button(root, text=EMPTY, width=2, height=1, font=("Arial", 14),
                               command=lambda r=i, c=j: update_board(r, c))
            button.grid(row=i, column=j)
            row_buttons.append(button)
        buttons.append(row_buttons)

    turn_label = tk.Label(root, text="現在のターン: プレイヤー", font=("Arial", 14))
    turn_label.grid(row=BOARD_SIZE, column=0, columnspan=BOARD_SIZE)

    result_label = tk.Label(root, text="", font=("Arial", 16))
    result_label.grid(row=BOARD_SIZE + 1, column=0, columnspan=BOARD_SIZE)

    root.mainloop()

if __name__ == "__main__":
    main()
