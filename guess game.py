import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont
import random
import math

BASE_W, BASE_H = 360, 640  # Reference design size for responsive scaling

class GuessApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Guess the Number")
        self.root.geometry("360x640")
        self.root.minsize(320, 520)
        self.fullscreen = False

        # Game state
        self.score = 0
        self.number = None
        self.min_val = 1
        self.max_val = 100
        self.tries = 0
        self.max_tries = 10

        # Fonts (will be scaled on resize)
        self.font_title = tkfont.Font(family="Arial", size=18, weight="bold")
        self.font_label = tkfont.Font(family="Arial", size=14)
        self.font_entry = tkfont.Font(family="Arial", size=14)
        self.font_button = tkfont.Font(family="Arial", size=14, weight="bold")
        self.font_small = tkfont.Font(family="Arial", size=11)

        # Optional ttk style for progressbar
        self.style = ttk.Style()
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass
        self.style.configure(
            "Tries.Horizontal.TProgressbar",
            troughcolor="#0f172a",
            background="#38bdf8",
            bordercolor="#0f172a",
            lightcolor="#38bdf8",
            darkcolor="#0ea5e9"
        )

        # Main container
        self.container = tk.Frame(self.root, bg="#0f172a")
        self.container.pack(fill="both", expand=True)

        # Screens
        self.frame_menu = tk.Frame(self.container, bg="#0f172a")
        self.frame_game = tk.Frame(self.container, bg="#0f172a")

        self.build_menu()
        self.build_game()

        # Show menu first
        self.frame_menu.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Shortcuts
        self.root.bind("<Return>", lambda e: self.check_guess() if self.frame_game.winfo_ismapped() else None)
        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<Escape>", self.exit_fullscreen)
        self.root.bind("<Configure>", self.on_resize)

    # ---------- Menu screen ----------
    def build_menu(self):
        title = tk.Label(self.frame_menu, text="Select Difficulty",
                         fg="#e2e8f0", bg="#0f172a", font=self.font_title)
        title.pack(pady=24)

        btn_easy = tk.Button(
            self.frame_menu, text="Easy (1–50)",
            command=lambda: self.start_game(1, 50),
            font=self.font_button, fg="#0f172a", bg="#38bdf8",
            activebackground="#0ea5e9", relief="flat", cursor="hand2"
        )
        btn_medium = tk.Button(
            self.frame_menu, text="Medium (1–100)",
            command=lambda: self.start_game(1, 100),
            font=self.font_button, fg="#0f172a", bg="#34d399",
            activebackground="#059669", relief="flat", cursor="hand2"
        )
        btn_hard = tk.Button(
            self.frame_menu, text="Hard (1–500)",
            command=lambda: self.start_game(1, 500),
            font=self.font_button, fg="#0f172a", bg="#f59e0b",
            activebackground="#d97706", relief="flat", cursor="hand2"
        )

        btn_easy.pack(pady=8, ipady=8, fill="x", padx=16)
        btn_medium.pack(pady=8, ipady=8, fill="x", padx=16)
        btn_hard.pack(pady=8, ipady=8, fill="x", padx=16)

        tip = tk.Label(self.frame_menu, text="F11: Fullscreen • Esc: Exit Fullscreen",
                       fg="#94a3b8", bg="#0f172a", font=self.font_small)
        tip.pack(side="bottom", pady=12)

    # ---------- Game screen ----------
    def build_game(self):
        # Top: score + range
        top = tk.Frame(self.frame_game, bg="#0f172a")
        top.pack(fill="x", pady=12, padx=16)

        self.lbl_score = tk.Label(top, text="Score: 0",
                                  fg="#e2e8f0", bg="#0f172a", font=self.font_title)
        self.lbl_score.pack(side="left")

        self.lbl_range = tk.Label(top, text="Range: 1–100",
                                  fg="#cbd5e1", bg="#0f172a", font=self.font_label)
        self.lbl_range.pack(side="right")

        # Center: prompt + entry + button + result
        center = tk.Frame(self.frame_game, bg="#0f172a")
        center.pack(expand=True, fill="both", padx=16)

        self.lbl_prompt = tk.Label(center, text="Guess a number between 1 and 100:",
                                   fg="#cbd5e1", bg="#0f172a", font=self.font_label)
        self.lbl_prompt.pack(pady=8)

        self.var_entry = tk.StringVar()
        self.entry = tk.Entry(center, textvariable=self.var_entry, justify="center",
                              font=self.font_entry, fg="#0f172a", bg="#e2e8f0", relief="flat")
        self.entry.pack(pady=8, ipadx=8, ipady=6, fill="x")

        self.btn_guess = tk.Button(center, text="Guess", command=self.check_guess,
                                   font=self.font_button, fg="#0f172a", bg="#38bdf8",
                                   activebackground="#0ea5e9", relief="flat", cursor="hand2")
        self.btn_guess.pack(pady=10, ipady=8, fill="x")

        self.lbl_result = tk.Label(center, text="", fg="#f1f5f9", bg="#0f172a", font=self.font_label)
        self.lbl_result.pack(pady=8)

        # Bottom: tries bar (left) + back to menu (right-bottom)
        bottom = tk.Frame(self.frame_game, bg="#0f172a")
        bottom.pack(side="bottom", anchor="w", padx=16, pady=14, fill="x")

        self.lbl_tries = tk.Label(bottom, text="Tries: 0/0",
                                  fg="#94a3b8", bg="#0f172a", font=self.font_small)
        self.lbl_tries.pack(side="left", padx=(0, 8))

        self.pbar = ttk.Progressbar(bottom, style="Tries.Horizontal.TProgressbar",
                                    orient="horizontal", mode="determinate", length=160)
        self.pbar.pack(side="left")

        self.btn_menu = tk.Button(self.frame_game, text="Change Difficulty", command=self.back_to_menu,
                                  font=self.font_small, fg="#0f172a", bg="#e5e7eb",
                                  activebackground="#cbd5e1", relief="flat", cursor="hand2")
        self.btn_menu.place(relx=1.0, rely=1.0, x=-16, y=-16, anchor="se")

    # ---------- Start game with selected range ----------
    def start_game(self, min_v, max_v):
        self.min_val, self.max_val = min_v, max_v
        self.score = 0
        self.new_round(reset_score_label=True)
        self.lbl_range.config(text=f"Range: {self.min_val}–{self.max_val}")
        self.lbl_prompt.config(text=f"Guess a number between {self.min_val} and {self.max_val}:")
        self.entry.focus_set()
        self.slide_to(self.frame_menu, self.frame_game, direction="left")

    # ---------- Start a new round ----------
    def new_round(self, reset_score_label=False):
        self.number = random.randint(self.min_val, self.max_val)
        self.tries = 0
        rng = self.max_val - self.min_val + 1
        self.max_tries = max(3, math.ceil(math.log2(rng)) + 1)  # smart limit
        self.update_try_ui()
        self.var_entry.set("")
        self.lbl_result.config(text="", fg="#f1f5f9")
        if reset_score_label:
            self.lbl_score.config(text=f"Score: {self.score}")

    # ---------- Check the user's guess ----------
    def check_guess(self):
        txt = self.var_entry.get().strip()
        if not txt:
            self.flash_result("Please enter a number.", color="#fca5a5")
            return
        try:
            guess = int(txt)
        except ValueError:
            self.flash_result("Please enter a valid integer.", color="#fca5a5")
            return

        if guess < self.min_val or guess > self.max_val:
            self.flash_result(f"Please enter a number between {self.min_val}–{self.max_val}.", color="#fca5a5")
            return

        self.tries += 1
        self.update_try_ui()

        if guess < self.number:
            self.flash_result("Try a bigger number.", color="#eab308")
        elif guess > self.number:
            self.flash_result("Try a smaller number.", color="#eab308")
        else:
            self.score += 1
            self.lbl_score.config(text=f"Score: {self.score}")
            self.flash_result("Correct! New number picked 🎉", color="#86efac")
            self.root.after(350, self.new_round)
            return

        if self.tries >= self.max_tries:
            self.flash_result(f"Out of tries! The correct number was {self.number}. New number picked.", color="#fca5a5")
            self.root.after(500, self.new_round)

        self.var_entry.set("")
        self.entry.focus_set()

    # ---------- Update tries UI ----------
    def update_try_ui(self):
        self.lbl_tries.config(text=f"Tries: {self.tries}/{self.max_tries}")
        self.pbar["maximum"] = self.max_tries
        self.pbar["value"] = self.tries

    # ---------- Small flash animation for result text ----------
    def flash_result(self, text, color="#f1f5f9"):
        self.lbl_result.config(text=text, fg=color)
        base_size = self.font_label.cget("size")
        self.font_label.configure(size=base_size + 2)
        self.root.after(120, lambda: self.font_label.configure(size=base_size))

    # ---------- Animated screen transition ----------
    def slide_to(self, old_frame, new_frame, direction="left", duration=260, steps=16):
        w = max(self.container.winfo_width(), 1)
        h = max(self.container.winfo_height(), 1)
        dx = w // steps
        if direction == "left":
            start_x_new = w
            delta = -dx
        else:
            start_x_new = -w
            delta = dx

        new_frame.place(x=start_x_new, y=0, width=w, height=h)

        def step(i, x_old=0, x_new=start_x_new):
            if i >= steps:
                old_frame.place_forget()
                new_frame.place(x=0, y=0, width=w, height=h)
                return
            x_old += delta
            x_new += delta
            old_frame.place(x=x_old, y=0, width=w, height=h)
            new_frame.place(x=x_new, y=0, width=w, height=h)
            self.root.after(max(1, duration // steps), lambda: step(i + 1, x_old, x_new))

        old_frame.place(x=0, y=0, width=w, height=h)
        step(0)

    # ---------- Back to menu ----------
    def back_to_menu(self):
        self.slide_to(self.frame_game, self.frame_menu, direction="right")

    # ---------- Fullscreen ----------
    def toggle_fullscreen(self, event=None):
        self.fullscreen = not self.fullscreen
        self.root.attributes("-fullscreen", self.fullscreen)

    def exit_fullscreen(self, event=None):
        self.fullscreen = False
        self.root.attributes("-fullscreen", False)

    # ---------- Responsive scaling ----------
    def on_resize(self, event):
        w = max(self.root.winfo_width(), 1)
        h = max(self.root.winfo_height(), 1)
        scale = min(w / BASE_W, h / BASE_H)

        self.font_title.configure(size=max(14, int(18 * scale)))
        self.font_label.configure(size=max(12, int(14 * scale)))
        self.font_entry.configure(size=max(12, int(14 * scale)))
        self.font_button.configure(size=max(12, int(14 * scale)))
        self.font_small.configure(size=max(10, int(11 * scale)))


if __name__ == "__main__":
    root = tk.Tk()
    app = GuessApp(root)
    root.mainloop()
