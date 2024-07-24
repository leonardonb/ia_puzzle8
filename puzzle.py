import tkinter as tk
import random
import time
from collections import deque

class PuzzleGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Puzzle Game")
        self.timer_label = tk.Label(self.root, text="Tempo: 0s", font=("Arial", 14))
        self.timer_label.pack()
        self.board = self.create_solvable_board()
        self.buttons = []
        self.create_widgets()
        self.solve_button = tk.Button(self.root, text="Resolver", command=self.solve_puzzle)
        self.solve_button.pack(side=tk.RIGHT)
        self.restart_button = tk.Button(self.root, text="(Re)iniciar", command=self.restart_game)
        self.restart_button.pack(side=tk.LEFT)
        self.start_time = None
        self.timer_running = False
        self.congrats_label = None
        self.update_buttons()
        self.start_timer()

    def create_solvable_board(self):
        # Cria um tabuleiro que é garantidamente solucionável
        while True:
            numbers = list(range(1, 9)) + [None]
            random.shuffle(numbers)
            if self.is_solvable(numbers):
                break
        board = [numbers[i:i+3] for i in range(0, 9, 3)]
        return board

    def is_solvable(self, tiles):
        # Verifica se o tabuleiro é solucionável
        inv_count = 0
        for i in range(len(tiles)):
            for j in range(i + 1, len(tiles)):
                if tiles[i] is not None and tiles[j] is not None and tiles[i] > tiles[j]:
                    inv_count += 1
        return inv_count % 2 == 0

    def create_widgets(self):
        # Cria os botões para o tabuleiro
        frame = tk.Frame(self.root)
        frame.pack()
        for i in range(3):
            row = []
            for j in range(3):
                num = self.board[i][j]
                if num is not None:
                    button = tk.Button(frame, text=str(num), width=10, height=5,
                                       command=lambda i=i, j=j: self.move_tile(i, j))
                else:
                    button = tk.Button(frame, text=' ', width=10, height=5,
                                       command=lambda i=i, j=j: self.move_tile(i, j))
                button.grid(row=i, column=j)
                row.append(button)
            self.buttons.append(row)

    def move_tile(self, i, j):
        # Move a peça clicada para o espaço em branco, se for um movimento válido
        blank_i, blank_j = self.find_blank()
        if (abs(blank_i - i) == 1 and blank_j == j) or (abs(blank_j - j) == 1 and blank_i == i):
            self.board[blank_i][blank_j], self.board[i][j] = self.board[i][j], self.board[blank_i][blank_j]
            self.update_buttons()
            if self.is_solved():
                self.timer_running = False
                self.root.after(3000, self.show_congratulations)

    def find_blank(self):
        # Encontra a posição do espaço em branco no tabuleiro
        for i in range(3):
            for j in range(3):
                if self.board[i][j] is None:
                    return i, j

    def update_buttons(self):
        # Atualiza os textos dos botões com os valores do tabuleiro
        for i in range(3):
            for j in range(3):
                num = self.board[i][j]
                self.buttons[i][j].config(text=str(num) if num is not None else ' ')

    def is_solved(self):
        # Verifica se o tabuleiro está na configuração de solução
        solution = [1, 2, 3, 4, 5, 6, 7, 8, None]
        flat_board = [num for row in self.board for num in row]
        return flat_board == solution

    def show_congratulations(self):
        # Mostra uma mensagem de parabéns e desativa os botões
        for row in self.buttons:
            for button in row:
                button.config(state="disabled")
        self.congrats_label = tk.Label(self.root, text="Parabéns! o quebra-cabeça foi resolvido!", font=("Arial", 18))
        self.congrats_label.pack()

    def solve_puzzle(self):
        # Tenta resolver o quebra-cabeça usando busca em largura (BFS)
        print("solve_puzzle() foi chamada")
        solution = self.bfs_solve()
        if solution:
            print("Solução encontrada:", solution)
            self.animate_solution(solution)
        else:
            print("Nenhuma solução encontrada")

    def bfs_solve(self):
        # Algoritmo de busca em largura (BFS) para encontrar a solução do quebra-cabeça
        print("bfs_solve() foi chamada")
        start = tuple(tuple(row) for row in self.board)
        goal = (1, 2, 3, 4, 5, 6, 7, 8, None)
        queue = deque([(start, [])])  # Fila para estados a serem explorados
        visited = set()  # Conjunto para estados já visitados
        directions = {'up': (-1, 0), 'down': (1, 0), 'left': (0, -1), 'right': (0, 1)}

        def get_next_state(state, blank_i, blank_j, di, dj):
            # Gera o próximo estado movendo o espaço em branco na direção especificada
            ni, nj = blank_i + di, blank_j + dj
            if 0 <= ni < 3 and 0 <= nj < 3:
                new_state = [list(row) for row in state]
                new_state[blank_i][blank_j], new_state[ni][nj] = new_state[ni][nj], new_state[blank_i][blank_j]
                return tuple(tuple(row) for row in new_state), ni, nj
            return None, blank_i, blank_j

        while queue:
            state, path = queue.popleft()
            if tuple(num for row in state for num in row) == goal:
                return path  # Retorna o caminho se o estado objetivo for encontrado

            blank_i, blank_j = [(i, row.index(None)) for i, row in enumerate(state) if None in row][0]

            for direction, (di, dj) in directions.items():
                new_state, ni, nj = get_next_state(state, blank_i, blank_j, di, dj)
                if new_state and new_state not in visited:
                    visited.add(new_state)
                    new_path = path + [(ni, nj)]
                    queue.append((new_state, new_path))
        return None

    def animate_solution(self, solution):
        # Anima a solução passo a passo
        if not solution:
            return
        print("Animando movimento:", solution[0])
        next_move = solution.pop(0)
        blank_i, blank_j = self.find_blank()
        self.move_tile(next_move[0], next_move[1])
        if solution:
            self.root.after(500, self.animate_solution, solution)

    def restart_game(self):
        # Reinicia o jogo
        if self.congrats_label:
            self.congrats_label.destroy()
            self.congrats_label = None
        self.board = self.create_solvable_board()
        self.update_buttons()
        self.start_timer()
        for row in self.buttons:
            for button in row:
                button.config(state="normal")

    def start_timer(self):
        # Inicia o temporizador
        self.start_time = time.time()
        self.timer_running = True
        self.update_timer()

    def update_timer(self):
        # Atualiza o temporizador a cada segundo
        if self.timer_running:
            elapsed_time = int(time.time() - self.start_time)
            self.timer_label.config(text=f"Tempo: {elapsed_time}s")
            self.root.after(1000, self.update_timer)

def main():
    root = tk.Tk()
    game = PuzzleGame(root)
    root.mainloop()

if __name__ == "__main__":
    main()
