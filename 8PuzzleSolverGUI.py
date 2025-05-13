import heapq
import tkinter as tk
from tkinter import messagebox
import time

# THE MAIN CLASS, INCLUDES THE GUI AND THE A* ALGORITHM TO SOLVE THE 8-PUZZLE PROBLEM
class PuzzleSolverGUI:
    def __init__(self, master): # CONSTRUCTOR , DEFINES

        self.master = master # THE ROOT (MAIN) TKINTER WINDOW
        self.master.title("8-Puzzle Solver with A*") # THIS IS THE TITLE
        self.master.resizable(False, False) # MAKES SURE THAT THE WINDOW'S SIZE IS FIXED

        # THE GOAL STATE
        self.goal_board = [
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 0]
        ]
        # INVERSES MUST BE ODD, OTHERWISE IT'S UNSOLVABLE
        # THE INITIAL STATE
        self.start_board = [
            [1, 2, 5],
            [4, 0, 3],
            [6, 8, 7]
        ]

        # CREATE THE 3X3 GRID
        self.tiles = [[None for _ in range(3)] for _ in range(3)]
        self._create_board_frame()

        # CREATES AND CONTROLS THE "SOLVE" AND THE "SHUFFLE" BUTTONS IN THE GUI
        self._create_control_buttons()

    def _create_board_frame(self): # CREATE THE 3X3 GRID

        board_frame = tk.Frame(self.master)
        board_frame.grid(row=0, column=0, padx=10, pady=10)

        for i in range(3):
            for j in range(3):
                # Fetch the tile number; 0 means empty
                num = self.start_board[i][j]

                # Create a button with the tile number
                btn = tk.Button(
                    board_frame,
                    text=str(num) if num != 0 else "",
                    font=("Helvetica", 24),
                    width=4,
                    height=2,
                    state=tk.DISABLED
                )
                btn.grid(row=i, column=j, padx=5, pady=5)
                self.tiles[i][j] = btn

    # CREATES AND CONTROLS THE "SOLVE" AND THE "SHUFFLE" BUTTONS IN THE GUI
    def _create_control_buttons(self):

        control_frame = tk.Frame(self.master)
        control_frame.grid(row=1, column=0, pady=(0, 10))

        shuffle_btn = tk.Button(
            control_frame,
            text="Shuffle",
            command=self._shuffle_board,
            width=10
        )
        shuffle_btn.pack(side=tk.LEFT, padx=5)

        solve_btn = tk.Button(
            control_frame,
            text="Solve",
            command=self._solve_puzzle,
            width=10
        )
        solve_btn.pack(side=tk.LEFT, padx=5)

    # SHUFFLES THE TILES ( JUST MAKES RANDOM MOVES FROM THE GOAL STATE TO MAKE SURE THAT THE PUZZLE IS SOLVABLE )
    def _shuffle_board(self):
        import random

        # Reset to goal and perform random valid moves
        self.start_board = [row[:] for row in self.goal_board]
        zero_x, zero_y = 2, 2  # Empty tile starts at bottom-right in goal

        moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        # Perform 50 random moves for shuffle
        for _ in range(50):
            dx, dy = random.choice(moves)
            nx, ny = zero_x + dx, zero_y + dy
            if 0 <= nx < 3 and 0 <= ny < 3:
                # Swap empty with neighboring tile
                self.start_board[zero_x][zero_y], self.start_board[nx][ny] = (
                    self.start_board[nx][ny],
                    self.start_board[zero_x][zero_y]
                )
                zero_x, zero_y = nx, ny

        # Update the GUI display after shuffle
        self._update_tiles(self.start_board)

    # STARTS THE A* ALGORITHM TO FIND THE OPTIMAL PATH FROM START TO GOAL
    def _solve_puzzle(self):
        start_time = time.localtime().tm_sec
        

        # Run A* and retrieve path
        result = self.a_star(self.start_board)
        if not result:
            messagebox.showerror("No Solution", "No solution found for this puzzle state.")
            return

        steps, path = result
        # Animate the solution path
        for state in path:
            self._update_tiles([list(row) for row in state])
            self.master.update()  # Refresh GUI
            time.sleep(0.5)      # Brief pause for animation

            end_time = time.localtime().tm_sec

            total_time = end_time - start_time

        messagebox.showinfo("Solved", f"Puzzle solved in {steps} steps!\n\n Puzzle solved in {total_time} seconds")

    #UPDATES THE TEXT ON EACH BUTTON TO DISPLAY THE NEXT STATE
    def _update_tiles(self, board_state):
        for i in range(3):
            for j in range(3):
                num = board_state[i][j]
                # Update button text: blank for zero
                self.tiles[i][j].config(text=str(num) if num != 0 else "")

    # ---------------- A* ALGORITHM IMPLEMENTATION  ---------------- #
    # THIS IS THE CORE IMPLEMENTATION OF THE PROGRAM TO SOLVE THE 8-PUZZLE

    # THE HEURISTIC FUNCTION FOR THE A* ALGORITHM
    # COUNTS THE NUMBER OF MISPLACES TILES
    def heuristic(self, board):

        misplaced = 0 # Reset misplaced count for each function call
        for i in range(3):
            for j in range(3):
                if board[i][j] != 0 and board[i][j] != self.goal_board[i][j]:
                    misplaced += 1
        return misplaced # Return the fresh misplaced value instead of modifying a global variable

    ## FUNCTION USED TO DETECTED THE PLACE OF THE ZERO IN THE BOARD
    def detect_zero(self, board):
        for i in range(3):
            for j in range(3):
                if board[i][j] == 0:
                    return i, j
    #GENERATES ALL VALID BOARDS BY SLIDING A TILES INTO THE EMPTY SPACE
    def move_checking(self, board):

        x, y = self.detect_zero(board)
        moves = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for dx, dy in directions:
            moved_x = x + dx
            moved_y = y + dy

            if 0 <= moved_x < 3 and 0 <= moved_y < 3:
                new_board = [row[:] for row in board]
                new_board[x][y], new_board[moved_x][moved_y] = new_board[moved_x][moved_y], new_board[x][y]
                moves.append(new_board)
        return moves
    #TAKES THE 3×3 BOARD STORED AS A LIST OF LISTS AND CONVERTS IT INTO A TUPLE OF TUPLES ( BECAUSE PYTHON DOES NOT ACCEPT LISTS AS A KEY IN A DICTIONARY FOR HASHING PURPOSING  ), SO IT'S HERE  JUST FOR TECHNICAL STUFF ONLY
    def board_to_tuple(self, board):
        return tuple(tuple(row) for row in board)

    # ----- THIS IS THE MAIN A* IMPLEMENTATION -------#

    def a_star(self, start_state):
        queue = []
        visited = set()
        path = {}

        start_tuple = self.board_to_tuple(start_state)
        g_cost = 0
        f_cost = g_cost + self.heuristic(start_state)

        heapq.heappush(queue, (f_cost, g_cost, start_state))
        visited.add(start_tuple)

        while queue:
            f, g, board = heapq.heappop(queue)

            if board == self.goal_board:
                goal_path = []

                current = self.board_to_tuple(board)

                while current in path:
                    goal_path.append(current)
                    current = path[current]

                goal_path.append(start_tuple)
                goal_path.reverse()

                return g, goal_path

            else:
                for move in self.move_checking(board):
                    move_tuple = self.board_to_tuple(move)

                    if move_tuple not in visited:
                        visited.add(move_tuple)
                        path[move_tuple] = self.board_to_tuple(board)
                        h = self.heuristic(move)

                        f = h + g
                        heapq.heappush(queue, (f + 1, g + 1, move))
        return None


if __name__ == "__main__":
    # Entry point for the application
    root = tk.Tk()
    app = PuzzleSolverGUI(root)
    root.mainloop()
