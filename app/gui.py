import tkinter as tk
import tkinter.font as tkFont
from tkinter import filedialog, messagebox, ttk
from app.game_logic import MemoryGameLogic
from app.leaderboard import LeaderboardManager
import time
import json
import os

# Predefined templates
TEMPLATES = {
    "Custom": [],
    "Numbers 4x4": [(str(i), str(i)) for i in range(1, 9)],
    "English Words A1": [
        ("hello", "ciao"),
        ("goodbye", "arrivederci"),
        ("thank you", "grazie"),
        ("yes", "sì"),
        ("no", "no"),
        ("book", "libro"),
        ("car", "macchina"),
        ("house", "casa")
    ],
    "Italian Food": [
        ("pizza", "pizza"),
        ("pasta", "pasta"),
        ("gelato", "ice cream"),
        ("espresso", "espresso"),
        ("mozzarella", "mozzarella"),
        ("bruschetta", "bruschetta"),
        ("lasagna", "lasagna"),
        ("carbonara", "carbonara")
    ],
    "World Capitals": [
        ("France", "Paris"),
        ("Italy", "Rome"),
        ("Germany", "Berlin"),
        ("Spain", "Madrid"),
        ("Japan", "Tokyo"),
        ("Brazil", "Brasília"),
        ("Canada", "Ottawa"),
        ("Australia", "Canberra")
    ]
}

class MemoryGameGUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Memo Trainer - Enhanced")
        self.window.configure(bg="#f0f4f8")
        self.window.geometry("800x600")
        self.window.resizable(True, True)

        # Improved font configuration
        default_font = tkFont.nametofont("TkDefaultFont")
        default_font.configure(family="Segoe UI", size=11)
        self.window.option_add("*Font", default_font)

        # Game state
        self.logic = None
        self.buttons = {}
        self.first_choice = None
        self.timer_label = None
        self.start_time = None
        self.timer_running = False
        self.after_id = None
        self.waiting = False
        self.current_difficulty = "Easy"
        self.moves_count = 0
        self.moves_label = None

        # User data
        self.entries = []
        self.selected_template = tk.StringVar(value="Custom")
        self.username_var = tk.StringVar(value="Guest")
        self.is_guest_mode = tk.BooleanVar(value=True)
        
        # Leaderboard manager
        self.leaderboard = LeaderboardManager()
        
        self._show_main_menu()

    def _show_main_menu(self):
        """Show the main menu with options"""
        self._clear_window()
        
        # Title
        title_frame = tk.Frame(self.window, bg="#f0f4f8")
        title_frame.pack(pady=30)
        
        title = tk.Label(title_frame, text="🎓 Memo Trainer", 
                        font=("Segoe UI", 24, "bold"),
                        bg="#f0f4f8", fg="#2c3e50")
        title.pack()
        
        subtitle = tk.Label(title_frame, text="Train Your Memory with Custom Content",
                           font=("Segoe UI", 14), bg="#f0f4f8", fg="#7f8c8d")
        subtitle.pack(pady=(5, 0))

        # Menu buttons
        menu_frame = tk.Frame(self.window, bg="#f0f4f8")
        menu_frame.pack(pady=40)

        buttons_data = [
            ("🎮 Play Game", self._show_input_screen, "#3498db"),
            ("🏆 View Leaderboard", self._show_leaderboard, "#e74c3c"),
            ("📊 Statistics", self._show_statistics, "#f39c12"),
            ("❓ How to Play", self._show_help, "#9b59b6"),
        ]

        for text, command, color in buttons_data:
            btn = tk.Button(menu_frame, text=text, command=command,
                           font=("Segoe UI", 14, "bold"), bg=color, fg="white",
                           width=20, height=2, relief="flat", cursor="hand2")
            btn.pack(pady=8)
            
            # Hover effects
            def on_enter(e, btn=btn, color=color):
                btn.config(bg=self._darken_color(color))
            def on_leave(e, btn=btn, color=color):
                btn.config(bg=color)
            
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)

    def _darken_color(self, hex_color):
        """Darken a hex color for hover effect"""
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        darkened = tuple(max(0, int(c * 0.8)) for c in rgb)
        return f"#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}"

    def _show_input_screen(self):
        """Show the game setup screen"""
        self._clear_window()

        # Back button
        back_btn = tk.Button(self.window, text="← Back to Menu", command=self._show_main_menu,
                            font=("Segoe UI", 10), bg="#95a5a6", fg="white")
        back_btn.pack(anchor="nw", padx=10, pady=5)

        # Title
        title = tk.Label(self.window, text="🎓 Setup Your Memory Game", 
                        font=("Segoe UI", 18, "bold"),
                        bg="#f0f4f8", fg="#2c3e50")
        title.pack(pady=15)

        # Player settings frame
        player_frame = tk.LabelFrame(self.window, text="Player Settings", 
                                   font=("Segoe UI", 12, "bold"),
                                   bg="#f0f4f8", fg="#2c3e50", padx=10, pady=10)
        player_frame.pack(pady=10, padx=20, fill="x")

        # Player mode selection
        mode_frame = tk.Frame(player_frame, bg="#f0f4f8")
        mode_frame.pack(fill="x", pady=5)

        tk.Radiobutton(mode_frame, text="Play as Guest (no score saving)", 
                      variable=self.is_guest_mode, value=True,
                      command=self._toggle_guest_mode,
                      font=("Segoe UI", 11), bg="#f0f4f8").pack(anchor="w")

        tk.Radiobutton(mode_frame, text="Play with registered name", 
                      variable=self.is_guest_mode, value=False,
                      command=self._toggle_guest_mode,
                      font=("Segoe UI", 11), bg="#f0f4f8").pack(anchor="w")

        # Name entry
        self.name_frame = tk.Frame(player_frame, bg="#f0f4f8")
        self.name_frame.pack(fill="x", pady=5)
        
        tk.Label(self.name_frame, text="Player Name:", bg="#f0f4f8", 
                font=("Segoe UI", 11)).pack(side=tk.LEFT)
        self.name_entry = tk.Entry(self.name_frame, textvariable=self.username_var, 
                                  width=25, font=("Segoe UI", 11))
        self.name_entry.pack(side=tk.LEFT, padx=10)

        # Template selection frame
        template_frame = tk.LabelFrame(self.window, text="Content Selection", 
                                     font=("Segoe UI", 12, "bold"),
                                     bg="#f0f4f8", fg="#2c3e50", padx=10, pady=10)
        template_frame.pack(pady=10, padx=20, fill="x")

        dropdown_frame = tk.Frame(template_frame, bg="#f0f4f8")
        dropdown_frame.pack(fill="x", pady=5)

        tk.Label(dropdown_frame, text="Select Template:", font=("Segoe UI", 11), 
                bg="#f0f4f8").pack(side=tk.LEFT)
        
        style = ttk.Style()
        style.configure("Custom.TCombobox", fieldbackground="white")
        
        dropdown = ttk.Combobox(dropdown_frame, textvariable=self.selected_template,
                               values=list(TEMPLATES.keys()), state="readonly",
                               width=25, style="Custom.TCombobox")
        dropdown.pack(side=tk.LEFT, padx=10)
        dropdown.bind("<<ComboboxSelected>>", lambda e: self._load_template(self.selected_template.get()))

        # Pairs input frame
        pairs_frame = tk.LabelFrame(self.window, text="Memory Pairs", 
                                  font=("Segoe UI", 12, "bold"),
                                  bg="#f0f4f8", fg="#2c3e50", padx=10, pady=10)
        pairs_frame.pack(pady=10, padx=20, fill="both", expand=True)

        # Scrollable frame for pairs
        canvas = tk.Canvas(pairs_frame, bg="#f0f4f8", highlightthickness=0)
        scrollbar = ttk.Scrollbar(pairs_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg="#f0f4f8")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.form_frame = self.scrollable_frame

        # Control buttons
        control_frame = tk.Frame(pairs_frame, bg="#f0f4f8")
        control_frame.pack(fill="x", pady=5)

        buttons_data = [
            ("➕ Add Pair", self._add_pair_fields, "#27ae60"),
            ("💾 Save Set", self._save_set, "#f39c12"),
            ("📂 Load Set", self._load_set, "#3498db"),
        ]

        for text, command, color in buttons_data:
            btn = tk.Button(control_frame, text=text, command=command,
                           font=("Segoe UI", 10), bg=color, fg="white", relief="flat")
            btn.pack(side=tk.LEFT, padx=5)

        # Start game button
        start_btn = tk.Button(self.window, text="▶ Start Memory Game", 
                             command=self._start_game,
                             font=("Segoe UI", 16, "bold"), bg="#e74c3c", fg="white", 
                             height=2, relief="flat", cursor="hand2")
        start_btn.pack(pady=20)

        # Initialize
        self.entries.clear()
        for _ in range(3):
            self._add_pair_fields()
        
        self._toggle_guest_mode()
        self._load_template(self.selected_template.get())

    def _toggle_guest_mode(self):
        """Toggle between guest and registered player mode"""
        if self.is_guest_mode.get():
            self.username_var.set("Guest")
            self.name_entry.config(state="disabled")
        else:
            if self.username_var.get() == "Guest":
                self.username_var.set("")
            self.name_entry.config(state="normal")
            self.name_entry.focus_set()

    def _load_template(self, template_name):
        """Load predefined template"""
        # Clear existing entries
        for _, _, frame in self.entries:
            frame.destroy()
        self.entries.clear()

        # Load template data
        template_pairs = TEMPLATES.get(template_name, [])
        if template_pairs:
            for key, value in template_pairs:
                self._add_pair_fields(key, value)
        else:
            # Add empty pairs for custom template
            for _ in range(3):
                self._add_pair_fields()

    def _add_pair_fields(self, key="", value=""):
        """Add input fields for a new pair"""
        pair_frame = tk.Frame(self.form_frame, bg="#f0f4f8")
        pair_frame.pack(fill="x", pady=3)

        term_entry = tk.Entry(pair_frame, width=25, font=("Segoe UI", 10))
        arrow_label = tk.Label(pair_frame, text="↔", font=("Segoe UI", 12), 
                              bg="#f0f4f8", fg="#7f8c8d")
        def_entry = tk.Entry(pair_frame, width=25, font=("Segoe UI", 10))
        
        term_entry.insert(0, key)
        def_entry.insert(0, value)

        remove_btn = tk.Button(pair_frame, text="🗑", 
                              command=lambda: self._remove_pair(pair_frame, term_entry, def_entry),
                              font=("Segoe UI", 10), fg="#e74c3c", bg="#fff2f2", 
                              relief="flat", width=3, cursor="hand2")

        term_entry.pack(side=tk.LEFT, padx=5)
        arrow_label.pack(side=tk.LEFT)
        def_entry.pack(side=tk.LEFT, padx=5)
        remove_btn.pack(side=tk.LEFT, padx=5)

        self.entries.append((term_entry, def_entry, pair_frame))

    def _remove_pair(self, frame, term_entry, def_entry):
        """Remove a pair from the list"""
        if len(self.entries) <= 2:
            messagebox.showwarning("Warning", "You need at least 2 pairs to play!")
            return

        try:
            for i, (t, d, f) in enumerate(self.entries):
                if f == frame:
                    self.entries.pop(i)
                    break
            frame.destroy()
        except Exception as e:
            print(f"Error removing pair: {e}")

    def _start_game(self):
        """Start the memory game"""
        # Validate input
        pairs = []
        for term_entry, def_entry, _ in self.entries:
            term = term_entry.get().strip()
            definition = def_entry.get().strip()
            if term and definition:
                pairs.append((term, definition))

        if len(pairs) < 2:
            messagebox.showwarning("Error", "Please enter at least 2 valid pairs.")
            return

        # Validate player name for non-guest mode
        if not self.is_guest_mode.get():
            name = self.username_var.get().strip()
            if not name or name == "Guest":
                messagebox.showwarning("Error", "Please enter a valid player name.")
                return

        # Initialize game
        self.logic = MemoryGameLogic(pairs)
        self.first_choice = None
        self.buttons = {}
        self.moves_count = 0
        
        # Determine difficulty based on number of pairs
        num_pairs = len(pairs)
        if num_pairs <= 4:
            self.current_difficulty = "Easy"
        elif num_pairs <= 8:
            self.current_difficulty = "Medium"
        else:
            self.current_difficulty = "Hard"

        self._show_game_screen()

    def _show_game_screen(self):
        """Display the game interface"""
        self._clear_window()

        # Game info header
        info_frame = tk.Frame(self.window, bg="#34495e", height=80)
        info_frame.pack(fill="x", pady=(0, 10))
        info_frame.pack_propagate(False)

        # Player info
        player_info = f"Player: {self.username_var.get()}" if not self.is_guest_mode.get() else "Guest Mode"
        player_label = tk.Label(info_frame, text=player_info, 
                               font=("Segoe UI", 12, "bold"), bg="#34495e", fg="white")
        player_label.pack(side="left", padx=20, pady=10)

        # Timer and moves
        stats_frame = tk.Frame(info_frame, bg="#34495e")
        stats_frame.pack(side="right", padx=20, pady=10)

        self.timer_label = tk.Label(stats_frame, text="Time: 0s", 
                                   font=("Segoe UI", 12, "bold"), bg="#34495e", fg="#3498db")
        self.timer_label.pack()

        self.moves_label = tk.Label(stats_frame, text="Moves: 0", 
                                   font=("Segoe UI", 12, "bold"), bg="#34495e", fg="#e74c3c")
        self.moves_label.pack()

        difficulty_label = tk.Label(stats_frame, text=f"Difficulty: {self.current_difficulty}", 
                                   font=("Segoe UI", 10), bg="#34495e", fg="#f39c12")
        difficulty_label.pack()

        # Game grid
        self._create_grid()

        # Control buttons
        control_frame = tk.Frame(self.window, bg="#f0f4f8")
        control_frame.pack(pady=15)

        reset_btn = tk.Button(control_frame, text="🔄 New Game", 
                             command=self._show_input_screen,
                             font=("Segoe UI", 12, "bold"), bg="#95a5a6", fg="white")
        reset_btn.pack(side="left", padx=10)

        menu_btn = tk.Button(control_frame, text="🏠 Main Menu", 
                            command=self._show_main_menu,
                            font=("Segoe UI", 12, "bold"), bg="#34495e", fg="white")
        menu_btn.pack(side="left", padx=10)

        # Start timer
        self.start_time = time.time()
        self.timer_running = True
        self._start_timer()

    def _create_grid(self):
        """Create the game grid with cards"""
        game_frame = tk.Frame(self.window, bg="#f0f4f8")
        game_frame.pack(expand=True, fill="both", padx=20, pady=10)

        keys = list(self.logic.blocks.keys())
        num_cards = len(keys)
        
        # Determine grid layout
        if num_cards <= 8:
            cols = 4
        elif num_cards <= 16:
            cols = 4
        else:
            cols = 6

        for i, key in enumerate(keys):
            row, col = i // cols, i % cols
            
            btn = tk.Button(game_frame, text="?", font=("Segoe UI", 12, "bold"),
                           width=15, height=3, wraplength=120,
                           bg="#ecf0f1", fg="#2c3e50", relief="raised", bd=2,
                           cursor="hand2", command=lambda k=key: self._on_click(k))
            
            btn.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            self.buttons[key] = btn

        # Configure grid weights for responsiveness
        for i in range(cols):
            game_frame.columnconfigure(i, weight=1)

    def _on_click(self, key):
        """Handle card click"""
        if not self.logic or key not in self.logic.blocks or self.waiting:
            return

        if self.first_choice == key:
            return

        value = self.logic.get_value(key)
        self.buttons[key].config(text=value, state="disabled", 
                                bg="#3498db", fg="white", relief="flat")

        if not self.first_choice:
            self.first_choice = key
        else:
            second_choice = key
            self.moves_count += 1
            self.moves_label.config(text=f"Moves: {self.moves_count}")

            val1 = self.logic.get_value(self.first_choice)
            val2 = self.logic.get_value(second_choice)

            if self.logic.check_match(val1, val2):
                # Match found
                self.logic.remove_blocks(self.first_choice, second_choice)
                self.buttons[self.first_choice].config(bg="#27ae60", fg="white")
                self.buttons[second_choice].config(bg="#27ae60", fg="white")
                self.first_choice = None

                if self.logic.has_won():
                    self._game_won()
            else:
                # No match
                self.waiting = True
                first = self.first_choice
                self.first_choice = None

                def reset():
                    if first in self.buttons:
                        self.buttons[first].config(text="?", state="normal", 
                                                  bg="#ecf0f1", fg="#2c3e50", relief="raised")
                    if second_choice in self.buttons:
                        self.buttons[second_choice].config(text="?", state="normal", 
                                                          bg="#ecf0f1", fg="#2c3e50", relief="raised")
                    self.waiting = False

                self.window.after(1200, reset)

    def _game_won(self):
        """Handle game completion"""
        self.timer_running = False
        elapsed_time = int(time.time() - self.start_time)
        
        # Calculate score
        score = self._calculate_score(elapsed_time, self.moves_count)
        
        # Save score if not guest
        if not self.is_guest_mode.get():
            player_name = self.username_var.get().strip()
            self.leaderboard.add_score(player_name, score, elapsed_time, 
                                     self.moves_count, self.current_difficulty)

        # Show win dialog
        self._show_win_dialog(elapsed_time, score)

    def _calculate_score(self, time_taken, moves):
        """Calculate game score based on time, moves, and difficulty"""
        base_score = 1000
        
        # Difficulty multiplier
        difficulty_multipliers = {"Easy": 1.0, "Medium": 1.5, "Hard": 2.0}
        multiplier = difficulty_multipliers.get(self.current_difficulty, 1.0)
        
        # Time penalty (lose points for every second over 30)
        time_penalty = max(0, time_taken - 30) * 2
        
        # Move penalty (lose points for extra moves)
        expected_moves = len(self.entries)
        move_penalty = max(0, moves - expected_moves) * 5
        
        final_score = max(50, int((base_score - time_penalty - move_penalty) * multiplier))
        return final_score

    def _show_win_dialog(self, time_taken, score):
        """Show win dialog with results"""
        win_window = tk.Toplevel(self.window)
        win_window.title("Congratulations!")
        win_window.geometry("400x300")
        win_window.configure(bg="#f0f4f8")
        win_window.transient(self.window)
        win_window.grab_set()

        # Center the window
        win_window.geometry("+%d+%d" % (self.window.winfo_rootx() + 50, 
                                       self.window.winfo_rooty() + 50))

        # Congratulations message
        tk.Label(win_window, text="🎉 Congratulations! 🎉", 
                font=("Segoe UI", 20, "bold"), bg="#f0f4f8", fg="#27ae60").pack(pady=20)

        # Results frame
        results_frame = tk.Frame(win_window, bg="#fff", relief="raised", bd=2)
        results_frame.pack(pady=20, padx=30, fill="x")

        results_data = [
            ("Time:", f"{time_taken} seconds"),
            ("Moves:", str(self.moves_count)),
            ("Difficulty:", self.current_difficulty),
            ("Score:", f"{score} points")
        ]

        for label, value in results_data:
            row_frame = tk.Frame(results_frame, bg="#fff")
            row_frame.pack(fill="x", padx=20, pady=5)
            
            tk.Label(row_frame, text=label, font=("Segoe UI", 12, "bold"), 
                    bg="#fff", fg="#2c3e50").pack(side="left")
            tk.Label(row_frame, text=value, font=("Segoe UI", 12), 
                    bg="#fff", fg="#7f8c8d").pack(side="right")

        if not self.is_guest_mode.get():
            tk.Label(win_window, text="Score saved to leaderboard!", 
                    font=("Segoe UI", 11, "italic"), bg="#f0f4f8", fg="#27ae60").pack(pady=5)

        # Buttons frame
        btn_frame = tk.Frame(win_window, bg="#f0f4f8")
        btn_frame.pack(pady=20)

        tk.Button(btn_frame, text="🎮 Play Again", command=lambda: [win_window.destroy(), self._show_input_screen()],
                 font=("Segoe UI", 12, "bold"), bg="#3498db", fg="white").pack(side="left", padx=10)

        tk.Button(btn_frame, text="🏆 View Leaderboard", command=lambda: [win_window.destroy(), self._show_leaderboard()],
                 font=("Segoe UI", 12, "bold"), bg="#e74c3c", fg="white").pack(side="left", padx=10)

        tk.Button(btn_frame, text="🏠 Main Menu", command=lambda: [win_window.destroy(), self._show_main_menu()],
                 font=("Segoe UI", 12, "bold"), bg="#95a5a6", fg="white").pack(side="left", padx=10)

    def _show_leaderboard(self):
        """Display the leaderboard"""
        self._clear_window()

        # Back button
        back_btn = tk.Button(self.window, text="← Back to Menu", command=self._show_main_menu,
                            font=("Segoe UI", 10), bg="#95a5a6", fg="white")
        back_btn.pack(anchor="nw", padx=10, pady=5)

        # Title
        title = tk.Label(self.window, text="🏆 Leaderboard", 
                        font=("Segoe UI", 24, "bold"), bg="#f0f4f8", fg="#2c3e50")
        title.pack(pady=20)

        # Difficulty filter
        filter_frame = tk.Frame(self.window, bg="#f0f4f8")
        filter_frame.pack(pady=10)

        tk.Label(filter_frame, text="Filter by difficulty:", 
                font=("Segoe UI", 12), bg="#f0f4f8").pack(side="left")

        difficulty_var = tk.StringVar(value="All")
        difficulties = ["All", "Easy", "Medium", "Hard"]
        
        for diff in difficulties:
            tk.Radiobutton(filter_frame, text=diff, variable=difficulty_var, value=diff,
                          command=lambda: self._update_leaderboard_display(difficulty_var.get()),
                          font=("Segoe UI", 11), bg="#f0f4f8").pack(side="left", padx=10)

        # Leaderboard display
        self.leaderboard_frame = tk.Frame(self.window, bg="#f0f4f8")
        self.leaderboard_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self._update_leaderboard_display("All")

    def _update_leaderboard_display(self, difficulty_filter):
        """Update leaderboard display based on filter"""
        # Clear existing display
        for widget in self.leaderboard_frame.winfo_children():
            widget.destroy()

        scores = self.leaderboard.get_top_scores(difficulty_filter if difficulty_filter != "All" else None)

        if not scores:
            tk.Label(self.leaderboard_frame, text="No scores recorded yet!", 
                    font=("Segoe UI", 16), bg="#f0f4f8", fg="#7f8c8d").pack(pady=50)
            return

        # Header
        header_frame = tk.Frame(self.leaderboard_frame, bg="#34495e", height=50)
        header_frame.pack(fill="x", pady=(0, 10))

        headers = ["Rank", "Player", "Score", "Time", "Moves", "Difficulty", "Date"]
        header_widths = [8, 20, 10, 10, 10, 12, 15]

        for i, (header, width) in enumerate(zip(headers, header_widths)):
            tk.Label(header_frame, text=header, font=("Segoe UI", 12, "bold"),
                    bg="#34495e", fg="white", width=width).grid(row=0, column=i, padx=2, pady=10)

        # Scores
        for rank, score_data in enumerate(scores[:20], 1):  # Top 20
            row_color = "#ecf0f1" if rank % 2 == 0 else "#fff"
            
            if rank <= 3:
                rank_text = ["🥇", "🥈", "🥉"][rank-1]
            else:
                rank_text = str(rank)

            score_frame = tk.Frame(self.leaderboard_frame, bg=row_color, height=40)
            score_frame.pack(fill="x", pady=1)

            values = [
                rank_text,
                score_data['player_name'],
                str(score_data['score']),
                f"{score_data['time']}s",
                str(score_data['moves']),
                score_data['difficulty'],
                score_data['date'].strftime("%Y-%m-%d")
            ]

            for i, (value, width) in enumerate(zip(values, header_widths)):
                tk.Label(score_frame, text=value, font=("Segoe UI", 11),
                        bg=row_color, fg="#2c3e50", width=width).grid(row=0, column=i, padx=2, pady=5)

    def _show_statistics(self):
        """Show player statistics"""
        self._clear_window()

        # Back button
        back_btn = tk.Button(self.window, text="← Back to Menu", command=self._show_main_menu,
                            font=("Segoe UI", 10), bg="#95a5a6", fg="white")
        back_btn.pack(anchor="nw", padx=10, pady=5)

        # Title
        title = tk.Label(self.window, text="📊 Statistics", 
                        font=("Segoe UI", 24, "bold"), bg="#f0f4f8", fg="#2c3e50")
        title.pack(pady=20)

        stats = self.leaderboard.get_statistics()

        if not stats:
            tk.Label(self.window, text="No game data available yet!", 
                    font=("Segoe UI", 16), bg="#f0f4f8", fg="#7f8c8d").pack(pady=50)
            return

        # Statistics display
        stats_frame = tk.Frame(self.window, bg="#f0f4f8")
        stats_frame.pack(pady=30, padx=50, fill="both", expand=True)

        # General stats
        general_frame = tk.LabelFrame(stats_frame, text="General Statistics", 
                                    font=("Segoe UI", 14, "bold"), bg="#f0f4f8", fg="#2c3e50")
        general_frame.pack(fill="x", pady=10, padx=10, ipady=10)

        general_stats = [
            ("Total Games Played:", stats['total_games']),
            ("Total Players:", stats['total_players']),
            ("Average Score:", f"{stats['avg_score']:.1f}"),
            ("Average Time:", f"{stats['avg_time']:.1f}s"),
            ("Average Moves:", f"{stats['avg_moves']:.1f}")
        ]

        for i, (label, value) in enumerate(general_stats):
            row = i // 2
            col = i % 2 * 2
            
            tk.Label(general_frame, text=label, font=("Segoe UI", 12, "bold"),
                    bg="#f0f4f8", anchor="w").grid(row=row, column=col, sticky="w", padx=10, pady=5)
            tk.Label(general_frame, text=str(value), font=("Segoe UI", 12),
                    bg="#f0f4f8", fg="#3498db").grid(row=row, column=col+1, sticky="w", padx=20)

        # Difficulty breakdown
        if stats['difficulty_breakdown']:
            difficulty_frame = tk.LabelFrame(stats_frame, text="Difficulty Breakdown", 
                                           font=("Segoe UI", 14, "bold"), bg="#f0f4f8", fg="#2c3e50")
            difficulty_frame.pack(fill="x", pady=10, padx=10, ipady=10)

            for i, (difficulty, count) in enumerate(stats['difficulty_breakdown'].items()):
                tk.Label(difficulty_frame, text=f"{difficulty}:", font=("Segoe UI", 12, "bold"),
                        bg="#f0f4f8", anchor="w").grid(row=i, column=0, sticky="w", padx=10, pady=3)
                tk.Label(difficulty_frame, text=f"{count} games", font=("Segoe UI", 12),
                        bg="#f0f4f8", fg="#e74c3c").grid(row=i, column=1, sticky="w", padx=20)

        # Top performers
        if stats['top_players']:
            top_frame = tk.LabelFrame(stats_frame, text="Top Performers", 
                                    font=("Segoe UI", 14, "bold"), bg="#f0f4f8", fg="#2c3e50")
            top_frame.pack(fill="x", pady=10, padx=10, ipady=10)

            for i, (player, score) in enumerate(stats['top_players'][:5]):
                rank_text = ["🥇", "🥈", "🥉", "4th", "5th"][i]
                tk.Label(top_frame, text=f"{rank_text} {player}", font=("Segoe UI", 12, "bold"),
                        bg="#f0f4f8", anchor="w").grid(row=i, column=0, sticky="w", padx=10, pady=3)
                tk.Label(top_frame, text=f"{score} points", font=("Segoe UI", 12),
                        bg="#f0f4f8", fg="#27ae60").grid(row=i, column=1, sticky="w", padx=20)

    def _show_help(self):
        """Show help/instructions"""
        self._clear_window()

        # Back button
        back_btn = tk.Button(self.window, text="← Back to Menu", command=self._show_main_menu,
                            font=("Segoe UI", 10), bg="#95a5a6", fg="white")
        back_btn.pack(anchor="nw", padx=10, pady=5)

        # Title
        title = tk.Label(self.window, text="❓ How to Play", 
                        font=("Segoe UI", 24, "bold"), bg="#f0f4f8", fg="#2c3e50")
        title.pack(pady=20)

        # Help content
        help_frame = tk.Frame(self.window, bg="#f0f4f8")
        help_frame.pack(fill="both", expand=True, padx=30, pady=20)

        help_sections = [
            ("🎯 Objective", 
             "Match all pairs of cards by remembering their positions. Find all matching pairs in the shortest time with the fewest moves possible."),
            
            ("🎮 How to Play",
             "1. Choose to play as Guest or enter your name to save scores\n"
             "2. Select a template or create custom pairs\n"
             "3. Click cards to reveal their content\n"
             "4. Find matching pairs - they will stay revealed\n"
             "5. Continue until all pairs are matched"),
            
            ("🏆 Scoring System",
             "Your score is based on:\n"
             "• Time taken (faster = higher score)\n"
             "• Number of moves (fewer moves = higher score)\n"
             "• Difficulty level (harder = score multiplier)\n"
             "• Base score: 1000 points"),
            
            ("📊 Difficulty Levels",
             "• Easy: 2-4 pairs\n"
             "• Medium: 5-8 pairs\n"
             "• Hard: 9+ pairs"),
            
            ("💡 Tips",
             "• Pay attention to card positions\n"
             "• Try to remember revealed cards\n"
             "• Start with corner and edge cards\n"
             "• Practice with easier templates first")
        ]

        for section_title, content in help_sections:
            section_frame = tk.LabelFrame(help_frame, text=section_title, 
                                        font=("Segoe UI", 14, "bold"), 
                                        bg="#f0f4f8", fg="#2c3e50", padx=15, pady=10)
            section_frame.pack(fill="x", pady=10)

            tk.Label(section_frame, text=content, font=("Segoe UI", 11),
                    bg="#f0f4f8", fg="#34495e", justify="left", wraplength=600).pack(fill="x")

    def _save_set(self):
        """Save current pairs to file"""
        pairs = []
        for term_entry, def_entry, _ in self.entries:
            key = term_entry.get().strip()
            value = def_entry.get().strip()
            if key and value:
                pairs.append((key, value))

        if not pairs:
            messagebox.showwarning("Error", "No valid pairs to save.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Save Memory Set"
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(pairs, f, ensure_ascii=False, indent=4)
                messagebox.showinfo("Success", "Set saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save the file:\n{e}")

    def _load_set(self):
        """Load pairs from file"""
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Load Memory Set"
        )

        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    pairs = json.load(f)

                # Clear existing entries
                for _, _, frame in self.entries:
                    frame.destroy()
                self.entries.clear()

                # Load new pairs
                for key, value in pairs:
                    self._add_pair_fields(key, value)

                self.selected_template.set("Custom")
                messagebox.showinfo("Success", "Set loaded successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Invalid JSON or file error:\n{e}")

    def _start_timer(self):
        """Update game timer"""
        if self.timer_running:
            elapsed = int(time.time() - self.start_time)
            try:
                self.timer_label.config(text=f"Time: {elapsed}s")
            except tk.TclError:
                return
            self.after_id = self.window.after(1000, self._start_timer)

    def _clear_window(self):
        """Clear all widgets from window"""
        if self.after_id:
            self.window.after_cancel(self.after_id)
            self.after_id = None

        for widget in self.window.winfo_children():
            widget.destroy()

    def run(self):
        """Start the application"""
        self.window.mainloop()
