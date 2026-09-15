import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import csv
import os
from datetime import datetime, date, timedelta


APP_TITLE = "TaskFlow Pro"
DATA_FILE = "tasks.json"
FEEDBACK_FILE = "feedback.json"

CATEGORIES = [
    "General",
    "Study",
    "Work",
    "Personal",
    "Shopping",
    "Health",
    "Finance",
    "Travel",
    "Fitness",
    "Family",
    "Projects",
    "Meetings",
    "Learning",
    "Home",
    "Errands",
    "Other",
]

PRIORITIES = ["Low", "Medium", "High", "Urgent"]
STATUSES = ["Pending", "In Progress", "Completed"]


DARK = {
    "bg": "#0B0B12",
    "sidebar": "#11111B",
    "surface": "#151522",
    "card": "#191927",
    "input": "#202033",
    "border": "#2B2B40",
    "text": "#F5F3FF",
    "muted": "#9693AA",
    "primary": "#8B5CF6",
    "primary_dark": "#6D28D9",
    "accent": "#38BDF8",
    "green": "#34D399",
    "orange": "#F59E0B",
    "red": "#F87171",
    "white": "#FFFFFF",
    "hover": "#24243A",
}

LIGHT = {
    "bg": "#F4F5FA",
    "sidebar": "#FFFFFF",
    "surface": "#FFFFFF",
    "card": "#FFFFFF",
    "input": "#F7F7FB",
    "border": "#E2E3EC",
    "text": "#1F2030",
    "muted": "#6F7183",
    "primary": "#6D4AFF",
    "primary_dark": "#5635E8",
    "accent": "#0284C7",
    "green": "#059669",
    "orange": "#D97706",
    "red": "#DC2626",
    "white": "#FFFFFF",
    "hover": "#F0EEFF",
}


class TaskFlowApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("1240x820")
        self.root.minsize(1050, 700)

        self.is_dark = True
        self.theme = DARK
        self.tasks = []
        self.current_page = "dashboard"
        self.selected_task_id = None

        self.name_var = tk.StringVar()
        self.category_var = tk.StringVar(value="General")
        self.priority_var = tk.StringVar(value="Medium")
        self.status_var = tk.StringVar(value="Pending")
        self.due_date_var = tk.StringVar()
        self.due_time_var = tk.StringVar()

        self.search_var = tk.StringVar()
        self.filter_status_var = tk.StringVar(value="All")
        self.filter_category_var = tk.StringVar(value="All")

        self.feedback_name = tk.StringVar()
        self.feedback_email = tk.StringVar()

        self.load_tasks()
        self.setup_styles()
        self.build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    # =========================================================
    # DATA
    # =========================================================
    def load_tasks(self):
        if not os.path.exists(DATA_FILE):
            self.tasks = []
            return

        try:
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)

            if isinstance(data, list):
                self.tasks = data
            elif isinstance(data, dict) and isinstance(data.get("tasks"), list):
                self.tasks = data["tasks"]
            else:
                self.tasks = []

            # Normalize older/incomplete records.
            for task in self.tasks:
                task.setdefault("id", self.generate_id())
                task.setdefault("title", "Untitled")
                task.setdefault("description", "")
                task.setdefault("category", "General")
                task.setdefault("priority", "Medium")
                task.setdefault("status", "Pending")
                task.setdefault("due_date", "")
                task.setdefault("due_time", "")
                task.setdefault("created_at", "")
                task.setdefault("updated_at", "")
        except (json.JSONDecodeError, OSError) as exc:
            messagebox.showwarning(
                "Could not load tasks",
                f"tasks.json could not be read.\n\n{exc}\n\nStarting with an empty task list.",
            )
            self.tasks = []

    def save_tasks(self):
        try:
            temp_file = DATA_FILE + ".tmp"
            with open(temp_file, "w", encoding="utf-8") as file:
                json.dump(self.tasks, file, indent=4, ensure_ascii=False)
            os.replace(temp_file, DATA_FILE)
            return True
        except OSError as exc:
            messagebox.showerror("Save Error", f"Could not save tasks.json.\n\n{exc}")
            return False

    def generate_id(self):
        ids = [t.get("id") for t in self.tasks if isinstance(t.get("id"), int)]
        return max(ids, default=0) + 1

    def find_task(self, task_id):
        for task in self.tasks:
            if task.get("id") == task_id:
                return task
        return None

    # =========================================================
    # STYLE
    # =========================================================
    def setup_styles(self):
        self.style = ttk.Style()
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass
        self.apply_ttk_styles()

    def apply_ttk_styles(self):
        t = self.theme

        self.style.configure(
            "Treeview",
            background=t["card"],
            foreground=t["text"],
            fieldbackground=t["card"],
            rowheight=42,
            borderwidth=0,
            font=("Segoe UI", 10),
        )
        self.style.map(
            "Treeview",
            background=[("selected", t["primary"])],
            foreground=[("selected", t["white"])],
        )

        self.style.configure(
            "Treeview.Heading",
            background=t["surface"],
            foreground=t["muted"],
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            padding=10,
        )
        self.style.map(
            "Treeview.Heading",
            background=[("active", t["hover"])],
            foreground=[("active", t["text"])],
        )

        self.style.configure(
            "TCombobox",
            fieldbackground=t["input"],
            background=t["input"],
            foreground=t["text"],
            arrowcolor=t["primary"],
            bordercolor=t["border"],
            padding=8,
            font=("Segoe UI", 10),
        )
        self.style.map(
            "TCombobox",
            fieldbackground=[("readonly", t["input"])],
            selectbackground=[("readonly", t["input"])],
            selectforeground=[("readonly", t["text"])],
        )

        self.style.configure(
            "Vertical.TScrollbar",
            background=t["border"],
            troughcolor=t["surface"],
            arrowcolor=t["muted"],
            borderwidth=0,
        )

    # =========================================================
    # BASIC UI HELPERS
    # =========================================================
    def clear_root(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def make_button(self, parent, text, command, kind="primary", width=None):
        t = self.theme
        colors = {
            "primary": (t["primary"], t["primary_dark"], t["white"]),
            "secondary": (t["input"], t["hover"], t["text"]),
            "green": (t["green"], "#047857", t["white"]),
            "red": (t["red"], "#B91C1C", t["white"]),
            "orange": (t["orange"], "#B45309", t["white"]),
            "accent": (t["accent"], "#0369A1", t["white"]),
        }
        bg, active, fg = colors[kind]

        button = tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg,
            fg=fg,
            activebackground=active,
            activeforeground=fg,
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            bd=0,
            highlightthickness=0,
            cursor="hand2",
            padx=16,
            pady=9,
        )
        if width:
            button.config(width=width)
        return button

    def card(self, parent, **kwargs):
        return tk.Frame(
            parent,
            bg=self.theme["card"],
            highlightbackground=self.theme["border"],
            highlightthickness=1,
            bd=0,
            **kwargs,
        )

    def title_label(self, parent, text, size=22):
        return tk.Label(
            parent,
            text=text,
            font=("Segoe UI", size, "bold"),
            bg=self.theme["card"],
            fg=self.theme["text"],
        )

    def field_label(self, parent, text):
        return tk.Label(
            parent,
            text=text,
            font=("Segoe UI", 9, "bold"),
            bg=self.theme["card"],
            fg=self.theme["muted"],
        )

    def entry(self, parent, variable, **kwargs):
        return tk.Entry(
            parent,
            textvariable=variable,
            font=("Segoe UI", 10),
            bg=self.theme["input"],
            fg=self.theme["text"],
            insertbackground=self.theme["text"],
            relief="flat",
            highlightthickness=1,
            highlightbackground=self.theme["border"],
            highlightcolor=self.theme["primary"],
            **kwargs,
        )

    # =========================================================
    # MAIN UI
    # =========================================================
    def build_ui(self):
        self.clear_root()
        self.root.configure(bg=self.theme["bg"])

        self.build_sidebar()

        self.content = tk.Frame(self.root, bg=self.theme["bg"])
        self.content.pack(side="left", fill="both", expand=True)

        self.build_topbar()
        self.page_container = tk.Frame(self.content, bg=self.theme["bg"])
        self.page_container.pack(fill="both", expand=True, padx=28, pady=(4, 22))

        self.show_page(self.current_page)

    def choose_date(self, target_var):
        """Open a simple calendar dialog and put the selected date in target_var."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Select Date")
        dialog.geometry("340x390")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg=self.theme["card"])

        current = (
            datetime.strptime(target_var.get(), "%Y-%m-%d").date()
            if self._valid_date(target_var.get())
            else date.today()
        )

        state = {"year": current.year, "month": current.month}

        header = tk.Frame(dialog, bg=self.theme["card"])
        header.pack(fill="x", padx=16, pady=(16, 8))

        month_label = tk.Label(
            header,
            text="",
            font=("Segoe UI", 13, "bold"),
            bg=self.theme["card"],
            fg=self.theme["text"],
        )
        month_label.pack(side="left", expand=True)

        def shift_month(delta):
            y, m = state["year"], state["month"] + delta
            if m == 0:
                y, m = y - 1, 12
            elif m == 13:
                y, m = y + 1, 1
            state["year"], state["month"] = y, m
            render()

        tk.Button(
            header,
            text="‹",
            command=lambda: shift_month(-1),
            font=("Segoe UI", 16, "bold"),
            bd=0,
            bg=self.theme["card"],
            fg=self.theme["text"],
            activebackground=self.theme["card"],
            cursor="hand2",
        ).pack(side="left", before=month_label)

        tk.Button(
            header,
            text="›",
            command=lambda: shift_month(1),
            font=("Segoe UI", 16, "bold"),
            bd=0,
            bg=self.theme["card"],
            fg=self.theme["text"],
            activebackground=self.theme["card"],
            cursor="hand2",
        ).pack(side="right")

        grid = tk.Frame(dialog, bg=self.theme["card"])
        grid.pack(fill="both", expand=True, padx=16)

        def select_day(day):
            target_var.set(f"{state['year']:04d}-{state['month']:02d}-{day:02d}")
            dialog.destroy()

        def render():
            for widget in grid.winfo_children():
                widget.destroy()

            month_label.config(
                text=datetime(state["year"], state["month"], 1).strftime("%B %Y")
            )

            for col, name in enumerate(["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]):
                tk.Label(
                    grid,
                    text=name,
                    font=("Segoe UI", 9, "bold"),
                    bg=self.theme["card"],
                    fg=self.theme["muted"],
                ).grid(row=0, column=col, padx=2, pady=5)

            first = date(state["year"], state["month"], 1)
            next_month = date(
                state["year"] + (1 if state["month"] == 12 else 0),
                1 if state["month"] == 12 else state["month"] + 1,
                1,
            )
            days = (next_month - first).days
            start_col = first.weekday()

            for day_num in range(1, days + 1):
                index = start_col + day_num - 1
                row, col = 1 + index // 7, index % 7
                is_selected = target_var.get() == (
                    f"{state['year']:04d}-{state['month']:02d}-{day_num:02d}"
                )
                is_today = date.today() == date(state["year"], state["month"], day_num)

                btn = tk.Button(
                    grid,
                    text=str(day_num),
                    width=3,
                    command=lambda d=day_num: select_day(d),
                    bd=0,
                    cursor="hand2",
                    font=(
                        "Segoe UI",
                        9,
                        "bold" if (is_selected or is_today) else "normal",
                    ),
                    bg=self.theme["accent"] if is_selected else self.theme["input"],
                    fg="white" if is_selected else self.theme["text"],
                    activebackground=self.theme["accent"],
                    activeforeground="white",
                )
                btn.grid(row=row, column=col, padx=3, pady=3)

            footer = tk.Frame(dialog, bg=self.theme["card"])
            footer.pack(fill="x", padx=16, pady=12)

            tk.Button(
                footer,
                text="Today",
                command=lambda: (
                    target_var.set(date.today().strftime("%Y-%m-%d")),
                    dialog.destroy(),
                ),
                bd=0,
                padx=14,
                pady=7,
                cursor="hand2",
                bg=self.theme["accent"],
                fg="white",
                activebackground=self.theme["accent"],
            ).pack(side="left")

            tk.Button(
                footer,
                text="Cancel",
                command=dialog.destroy,
                bd=0,
                padx=14,
                pady=7,
                cursor="hand2",
                bg=self.theme["input"],
                fg=self.theme["text"],
                activebackground=self.theme["border"],
            ).pack(side="right")

        render()

    def choose_time(self, target_var):
        """Open a simple hour/minute/AM-PM picker and put 24-hour time in target_var."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Select Time")
        dialog.geometry("330x250")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg=self.theme["card"])

        current = target_var.get().strip()
        hour, minute, ampm = 9, 0, "AM"

        try:
            parsed = datetime.strptime(current, "%H:%M")
            hour = parsed.hour % 12 or 12
            minute = parsed.minute
            ampm = "AM" if parsed.hour < 12 else "PM"
        except ValueError:
            pass

        tk.Label(
            dialog,
            text="Select time",
            font=("Segoe UI", 14, "bold"),
            bg=self.theme["card"],
            fg=self.theme["text"],
        ).pack(pady=(18, 12))

        box = tk.Frame(dialog, bg=self.theme["card"])
        box.pack(pady=5)

        hours = [f"{h:02d}" for h in range(1, 13)]
        minutes = [f"{m:02d}" for m in range(0, 60, 5)]

        hour_var = tk.StringVar(value=f"{hour:02d}")
        minute_var = tk.StringVar(value=f"{minute:02d}")
        ampm_var = tk.StringVar(value=ampm)

        for values, variable, label in [
            (hours, hour_var, "Hour"),
            (minutes, minute_var, "Minute"),
            (["AM", "PM"], ampm_var, "AM / PM"),
        ]:
            frame = tk.Frame(box, bg=self.theme["card"])
            frame.pack(side="left", padx=5)
            tk.Label(
                frame,
                text=label,
                font=("Segoe UI", 8),
                bg=self.theme["card"],
                fg=self.theme["muted"],
            ).pack()
            ttk.Combobox(
                frame,
                textvariable=variable,
                values=values,
                state="readonly",
                width=7,
                justify="center",
            ).pack(pady=4)

        buttons = tk.Frame(dialog, bg=self.theme["card"])
        buttons.pack(fill="x", padx=18, pady=20)

        def save_time():
            h = int(hour_var.get())
            if ampm_var.get() == "PM" and h != 12:
                h += 12
            elif ampm_var.get() == "AM" and h == 12:
                h = 0
            target_var.set(f"{h:02d}:{int(minute_var.get()):02d}")
            dialog.destroy()

        tk.Button(
            buttons,
            text="Set Time",
            command=save_time,
            bd=0,
            padx=18,
            pady=8,
            cursor="hand2",
            bg=self.theme["accent"],
            fg="white",
            activebackground=self.theme["accent"],
        ).pack(side="left")

        tk.Button(
            buttons,
            text="Clear",
            command=lambda: (target_var.set(""), dialog.destroy()),
            bd=0,
            padx=18,
            pady=8,
            cursor="hand2",
            bg=self.theme["input"],
            fg=self.theme["text"],
            activebackground=self.theme["border"],
        ).pack(side="left", padx=8)

        tk.Button(
            buttons,
            text="Cancel",
            command=dialog.destroy,
            bd=0,
            padx=18,
            pady=8,
            cursor="hand2",
            bg=self.theme["input"],
            fg=self.theme["text"],
            activebackground=self.theme["border"],
        ).pack(side="right")

    @staticmethod
    def _valid_date(value):
        try:
            datetime.strptime(value.strip(), "%Y-%m-%d")
            return True
        except (ValueError, AttributeError):
            return False

    def build_sidebar(self):
        t = self.theme
        sidebar = tk.Frame(self.root, bg=t["sidebar"], width=225)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        logo = tk.Frame(sidebar, bg=t["sidebar"])
        logo.pack(fill="x", padx=20, pady=(25, 30))

        tk.Label(
            logo,
            text="✓",
            font=("Segoe UI", 22, "bold"),
            bg=t["primary"],
            fg=t["white"],
            width=2,
            pady=4,
        ).pack(side="left")

        brand = tk.Frame(logo, bg=t["sidebar"])
        brand.pack(side="left", padx=10)
        tk.Label(
            brand,
            text="TaskFlow",
            font=("Segoe UI", 17, "bold"),
            bg=t["sidebar"],
            fg=t["text"],
        ).pack(anchor="w")
        tk.Label(
            brand,
            text="PRODUCTIVITY",
            font=("Segoe UI", 7, "bold"),
            bg=t["sidebar"],
            fg=t["primary"],
        ).pack(anchor="w")

        tk.Label(
            sidebar,
            text="WORKSPACE",
            font=("Segoe UI", 8, "bold"),
            bg=t["sidebar"],
            fg=t["muted"],
        ).pack(anchor="w", padx=22, pady=(0, 8))

        self.nav_buttons = {}
        navigation = [
            ("dashboard", "⌂  Dashboard"),
            ("add", "＋  Add Task"),
            ("tasks", "☷  All Tasks"),
            ("edit", "✎  Edit Task"),
            ("delete", "⌫  Delete Task"),
            ("reports", "▥  Reports"),
            ("feedback", "✉  Feedback"),
        ]

        for key, label in navigation:
            btn = tk.Button(
                sidebar,
                text=label,
                command=lambda k=key: self.show_page(k),
                anchor="w",
                bg=t["sidebar"],
                fg=t["muted"],
                activebackground=t["hover"],
                activeforeground=t["text"],
                font=("Segoe UI", 10, "bold"),
                relief="flat",
                bd=0,
                highlightthickness=0,
                cursor="hand2",
                padx=20,
                pady=11,
            )
            btn.pack(fill="x", padx=10, pady=2)
            self.nav_buttons[key] = btn

        spacer = tk.Frame(sidebar, bg=t["sidebar"])
        spacer.pack(fill="both", expand=True)

        theme_box = tk.Frame(
            sidebar, bg=t["card"], highlightbackground=t["border"], highlightthickness=1
        )
        theme_box.pack(fill="x", padx=15, pady=15)

        tk.Label(
            theme_box,
            text="Appearance",
            font=("Segoe UI", 9, "bold"),
            bg=t["card"],
            fg=t["text"],
        ).pack(anchor="w", padx=12, pady=(10, 2))

        tk.Label(
            theme_box,
            text="Switch between light and dark",
            font=("Segoe UI", 8),
            bg=t["card"],
            fg=t["muted"],
        ).pack(anchor="w", padx=12)

        self.theme_button = self.make_button(
            theme_box,
            "☀  Light Mode" if self.is_dark else "☾  Dark Mode",
            self.toggle_theme,
            "secondary",
        )
        self.theme_button.pack(fill="x", padx=10, pady=10)

        tk.Label(
            sidebar,
            text="Python + Tkinter + JSON",
            font=("Segoe UI", 8),
            bg=t["sidebar"],
            fg=t["muted"],
        ).pack(pady=(0, 12))

    def build_topbar(self):
        t = self.theme
        topbar = tk.Frame(self.content, bg=t["bg"], height=82)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)

        left = tk.Frame(topbar, bg=t["bg"])
        left.pack(side="left", fill="y", padx=28)

        tk.Label(
            left,
            text=datetime.now().strftime("%A, %d %B %Y"),
            font=("Segoe UI", 9, "bold"),
            bg=t["bg"],
            fg=t["muted"],
        ).pack(anchor="w", pady=(16, 2))

        self.page_heading = tk.Label(
            left,
            text="Dashboard",
            font=("Segoe UI", 20, "bold"),
            bg=t["bg"],
            fg=t["text"],
        )
        self.page_heading.pack(anchor="w")

        right = tk.Frame(topbar, bg=t["bg"])
        right.pack(side="right", padx=28, pady=22)

        self.make_button(
            right, "＋ New Task", lambda: self.show_page("add"), "primary"
        ).pack(side="left")

    def show_page(self, page):
        self.current_page = page
        headings = {
            "dashboard": "Dashboard",
            "add": "Add New Task",
            "tasks": "All Tasks",
            "edit": "Edit Task",
            "delete": "Delete Task",
            "reports": "Reports & Export",
            "feedback": "Contact & Feedback",
        }
        if hasattr(self, "page_heading"):
            self.page_heading.config(text=headings.get(page, "TaskFlow"))

        for key, button in self.nav_buttons.items():
            active = key == page
            button.config(
                bg=self.theme["primary"] if active else self.theme["sidebar"],
                fg=self.theme["white"] if active else self.theme["muted"],
            )

        for widget in self.page_container.winfo_children():
            widget.destroy()

        builders = {
            "dashboard": self.build_dashboard,
            "add": self.build_add_page,
            "tasks": self.build_tasks_page,
            "edit": self.build_edit_page,
            "delete": self.build_delete_page,
            "reports": self.build_reports_page,
            "feedback": self.build_feedback_page,
        }
        builders[page]()

    # =========================================================
    # DASHBOARD
    # =========================================================
    def build_dashboard(self):
        t = self.theme

        welcome = tk.Frame(self.page_container, bg=t["bg"])
        welcome.pack(fill="x", pady=(0, 16))

        tk.Label(
            welcome,
            text="Welcome back 👋",
            font=("Segoe UI", 14, "bold"),
            bg=t["bg"],
            fg=t["text"],
        ).pack(anchor="w")
        tk.Label(
            welcome,
            text="Here is your productivity overview for today.",
            font=("Segoe UI", 9),
            bg=t["bg"],
            fg=t["muted"],
        ).pack(anchor="w", pady=(2, 0))

        pending = self.count_status("Pending")
        progress = self.count_status("In Progress")
        completed = self.count_status("Completed")
        total = len(self.tasks)
        percent = int(completed / total * 100) if total else 0

        stats = tk.Frame(self.page_container, bg=t["bg"])
        stats.pack(fill="x", pady=(0, 18))

        cards = [
            ("Active Tasks", pending + progress, t["accent"], "Pending + In Progress"),
            ("In Progress", progress, t["primary"], "Currently working"),
            ("Completed", completed, t["green"], f"{percent}% completion rate"),
            ("Total Tasks", total, t["orange"], "All saved tasks"),
        ]

        for title, value, color, subtitle in cards:
            box = self.card(stats)
            box.pack(side="left", fill="both", expand=True, padx=(0, 12))
            tk.Frame(box, bg=color, height=4).pack(fill="x")
            tk.Label(
                box,
                text=str(value),
                font=("Segoe UI", 25, "bold"),
                bg=t["card"],
                fg=color,
            ).pack(anchor="w", padx=18, pady=(14, 0))
            tk.Label(
                box,
                text=title,
                font=("Segoe UI", 10, "bold"),
                bg=t["card"],
                fg=t["text"],
            ).pack(anchor="w", padx=18, pady=(0, 2))
            tk.Label(
                box, text=subtitle, font=("Segoe UI", 8), bg=t["card"], fg=t["muted"]
            ).pack(anchor="w", padx=18, pady=(0, 14))

        lower = tk.Frame(self.page_container, bg=t["bg"])
        lower.pack(fill="both", expand=True)

        recent_card = self.card(lower)
        recent_card.pack(side="left", fill="both", expand=True, padx=(0, 8))

        tk.Label(
            recent_card,
            text="Recent Tasks",
            font=("Segoe UI", 13, "bold"),
            bg=t["card"],
            fg=t["text"],
        ).pack(anchor="w", padx=18, pady=(16, 2))
        tk.Label(
            recent_card,
            text="Your latest saved tasks",
            font=("Segoe UI", 8),
            bg=t["card"],
            fg=t["muted"],
        ).pack(anchor="w", padx=18, pady=(0, 10))

        recent = list(reversed(self.tasks))[:7]
        if not recent:
            tk.Label(
                recent_card,
                text="No tasks yet.\nClick “New Task” to get started.",
                font=("Segoe UI", 10),
                bg=t["card"],
                fg=t["muted"],
                justify="left",
            ).pack(anchor="w", padx=18, pady=25)
        else:
            for task in recent:
                row = tk.Frame(recent_card, bg=t["card"])
                row.pack(fill="x", padx=16, pady=5)

                status_color = {
                    "Pending": t["orange"],
                    "In Progress": t["accent"],
                    "Completed": t["green"],
                }.get(task.get("status"), t["muted"])

                tk.Label(
                    row, text="●", font=("Segoe UI", 10), bg=t["card"], fg=status_color
                ).pack(side="left", padx=(2, 8))

                info = tk.Frame(row, bg=t["card"])
                info.pack(side="left", fill="x", expand=True)
                tk.Label(
                    info,
                    text=task.get("title", "Untitled"),
                    font=("Segoe UI", 9, "bold"),
                    bg=t["card"],
                    fg=t["text"],
                ).pack(anchor="w")
                tk.Label(
                    info,
                    text=f"{task.get('category', 'General')}  •  {task.get('priority', 'Medium')}",
                    font=("Segoe UI", 8),
                    bg=t["card"],
                    fg=t["muted"],
                ).pack(anchor="w")

                tk.Label(
                    row,
                    text=task.get("status", ""),
                    font=("Segoe UI", 8, "bold"),
                    bg=t["card"],
                    fg=status_color,
                ).pack(side="right")

        quick = self.card(lower)
        quick.pack(side="left", fill="both", expand=True, padx=(8, 0))

        tk.Label(
            quick,
            text="Quick Actions",
            font=("Segoe UI", 13, "bold"),
            bg=t["card"],
            fg=t["text"],
        ).pack(anchor="w", padx=18, pady=(16, 12))

        actions = [
            ("＋  Create a Task", lambda: self.show_page("add"), "primary"),
            ("☷  View All Tasks", lambda: self.show_page("tasks"), "secondary"),
            ("▥  Open Reports", lambda: self.show_page("reports"), "secondary"),
            ("🗑  Delete Completed", self.delete_all_completed, "red"),
        ]
        for label, command, kind in actions:
            self.make_button(quick, label, command, kind).pack(
                fill="x", padx=18, pady=5
            )

    def count_status(self, status):
        return sum(1 for task in self.tasks if task.get("status") == status)

    # =========================================================
    # ADD PAGE
    # =========================================================
    def build_add_page(self):
        t = self.theme
        outer = self.card(self.page_container)
        outer.pack(fill="both", expand=True)

        tk.Label(
            outer,
            text="Create a new task",
            font=("Segoe UI", 16, "bold"),
            bg=t["card"],
            fg=t["text"],
        ).pack(anchor="w", padx=24, pady=(22, 2))
        tk.Label(
            outer,
            text="Add the details below. Your task is automatically saved to tasks.json.",
            font=("Segoe UI", 9),
            bg=t["card"],
            fg=t["muted"],
        ).pack(anchor="w", padx=24, pady=(0, 20))

        body = tk.Frame(outer, bg=t["card"])
        body.pack(fill="both", expand=True, padx=24, pady=(0, 20))

        self.field_label(body, "Task Name *").pack(anchor="w")
        self.add_name_entry = self.entry(body, self.name_var)
        self.add_name_entry.pack(fill="x", ipady=9, pady=(5, 14))
        self.add_name_entry.focus_set()

        self.field_label(body, "Description").pack(anchor="w")
        self.add_desc = tk.Text(
            body,
            height=5,
            font=("Segoe UI", 10),
            bg=t["input"],
            fg=t["text"],
            insertbackground=t["text"],
            relief="flat",
            highlightthickness=1,
            highlightbackground=t["border"],
            highlightcolor=t["primary"],
            wrap="word",
        )
        self.add_desc.pack(fill="x", pady=(5, 14))

        grid = tk.Frame(body, bg=t["card"])
        grid.pack(fill="x")
        for i in range(4):
            grid.columnconfigure(i, weight=1)

        fields = [
            ("Category", self.category_var, CATEGORIES),
            ("Priority", self.priority_var, PRIORITIES),
            ("Status", self.status_var, STATUSES),
        ]
        for i, (label, var, values) in enumerate(fields):
            box = tk.Frame(grid, bg=t["card"])
            box.grid(row=0, column=i, sticky="ew", padx=(0 if i == 0 else 6, 6))
            self.field_label(box, label).pack(anchor="w")
            ttk.Combobox(
                box,
                textvariable=var,
                values=values,
                state="readonly",
                font=("Segoe UI", 10),
            ).pack(fill="x", pady=(5, 0))

        date_box = tk.Frame(grid, bg=t["card"])
        date_box.grid(row=0, column=3, sticky="ew", padx=(6, 0))
        self.field_label(date_box, "Due Date").pack(anchor="w")
        date_controls = tk.Frame(date_box, bg=t["card"])
        date_controls.pack(fill="x", pady=(5, 0))

        self.entry(date_controls, self.due_date_var).pack(
            side="left", fill="x", expand=True, ipady=7
        )
        tk.Button(
            date_controls,
            text="📅 Select",
            command=lambda: self.choose_date(self.due_date_var),
            font=("Segoe UI", 9, "bold"),
            bg=t["primary"],
            fg="white",
            activebackground=t["primary_dark"],
            activeforeground="white",
            relief="flat",
            bd=0,
            padx=10,
            pady=7,
            cursor="hand2",
        ).pack(side="left", padx=(6, 0))

        time_box = tk.Frame(body, bg=t["card"])
        time_box.pack(fill="x", pady=(14, 0))
        time_box.columnconfigure(0, weight=1)
        time_box.columnconfigure(1, weight=1)

        tb1 = tk.Frame(time_box, bg=t["card"])
        tb1.grid(row=0, column=0, sticky="ew", padx=(0, 6))

        self.field_label(tb1, "Due Time").pack(anchor="w")

        time_controls = tk.Frame(tb1, bg=t["card"])
        time_controls.pack(fill="x", pady=(5, 0))

        self.entry(time_controls, self.due_time_var).pack(
            side="left", fill="x", expand=True, ipady=7
        )

        tk.Button(
            time_controls,
            text="🕐 Select",
            command=lambda: self.choose_time(self.due_time_var),
            font=("Segoe UI", 9, "bold"),
            bg=t["primary"],
            fg="white",
            activebackground=t["primary_dark"],
            activeforeground="white",
            relief="flat",
            bd=0,
            padx=10,
            pady=7,
            cursor="hand2",
        ).pack(side="left", padx=(6, 0))

        hint = tk.Frame(time_box, bg=t["card"])
        hint.grid(row=0, column=1, sticky="ew", padx=(6, 0))

        tk.Label(
            hint,
            text="📅 Choose a date and time",
            font=("Segoe UI", 10, "bold"),
            bg=t["card"],
            fg=t["text"],
        ).pack(anchor="w", pady=(10, 0))

        tk.Label(
            hint,
            text="Use the Select buttons instead of typing manually.",
            font=("Segoe UI", 8),
            bg=t["card"],
            fg=t["muted"],
        ).pack(anchor="w", pady=(4, 0))

        buttons = tk.Frame(body, bg=t["card"])
        buttons.pack(fill="x", pady=(22, 0))
        self.make_button(buttons, "Save Task", self.save_new_task, "primary").pack(
            side="left", fill="x", expand=True, padx=(0, 6)
        )
        self.make_button(buttons, "Clear Form", self.clear_add_form, "secondary").pack(
            side="left", fill="x", expand=True, padx=(6, 0)
        )

    def clear_add_form(self):
        self.name_var.set("")
        self.category_var.set("General")
        self.priority_var.set("Medium")
        self.status_var.set("Pending")
        self.due_date_var.set("")
        self.due_time_var.set("")
        if hasattr(self, "add_desc"):
            self.add_desc.delete("1.0", "end")
        if hasattr(self, "add_name_entry"):
            self.add_name_entry.focus_set()

    # =========================================================
    # VALIDATION / SAVE
    # =========================================================
    def validate_task(self, title, category, priority, status, due_date, due_time):
        if not title:
            messagebox.showwarning("Missing Task Name", "Please enter a task name.")
            return False
        if len(title) > 100:
            messagebox.showwarning(
                "Task Name Too Long", "Task name must be 100 characters or fewer."
            )
            return False
        if category not in CATEGORIES:
            messagebox.showwarning(
                "Invalid Category", "Please select a valid category."
            )
            return False
        if priority not in PRIORITIES:
            messagebox.showwarning(
                "Invalid Priority", "Please select a valid priority."
            )
            return False
        if status not in STATUSES:
            messagebox.showwarning("Invalid Status", "Please select a valid status.")
            return False

        if due_date:
            try:
                datetime.strptime(due_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showwarning(
                    "Invalid Date", "Use YYYY-MM-DD, for example 2026-09-15."
                )
                return False

        if due_time:
            try:
                datetime.strptime(due_time, "%H:%M")
            except ValueError:
                messagebox.showwarning("Invalid Time", "Use HH:MM, for example 18:30.")
                return False

        return True

    def save_new_task(self):
        title = self.name_var.get().strip()
        description = self.add_desc.get("1.0", "end-1c").strip()
        category = self.category_var.get().strip()
        priority = self.priority_var.get().strip()
        status = self.status_var.get().strip()
        due_date = self.due_date_var.get().strip()
        due_time = self.due_time_var.get().strip()

        if not self.validate_task(
            title, category, priority, status, due_date, due_time
        ):
            return

        now = datetime.now().isoformat(timespec="seconds")
        self.tasks.append(
            {
                "id": self.generate_id(),
                "title": title,
                "description": description,
                "category": category,
                "priority": priority,
                "status": status,
                "due_date": due_date,
                "due_time": due_time,
                "created_at": now,
                "updated_at": now,
            }
        )

        if self.save_tasks():
            messagebox.showinfo("Task Saved", f'"{title}" has been added successfully.')
            self.clear_add_form()
            self.show_page("tasks")

    # =========================================================
    # TASKS PAGE
    # =========================================================
    def build_tasks_page(self):
        t = self.theme
        card = self.card(self.page_container)
        card.pack(fill="both", expand=True)

        toolbar = tk.Frame(card, bg=t["card"])
        toolbar.pack(fill="x", padx=18, pady=(18, 10))

        left = tk.Frame(toolbar, bg=t["card"])
        left.pack(side="left", fill="x", expand=True)

        tk.Label(
            left,
            text="Task List",
            font=("Segoe UI", 14, "bold"),
            bg=t["card"],
            fg=t["text"],
        ).pack(anchor="w")
        tk.Label(
            left,
            text=f"{len(self.tasks)} saved task(s)",
            font=("Segoe UI", 8),
            bg=t["card"],
            fg=t["muted"],
        ).pack(anchor="w")

        self.make_button(toolbar, "Export", self.download_report, "secondary").pack(
            side="right"
        )

        filters = tk.Frame(card, bg=t["card"])
        filters.pack(fill="x", padx=18, pady=(0, 12))

        search_frame = tk.Frame(filters, bg=t["input"])
        search_frame.pack(side="left", fill="x", expand=True, padx=(0, 8))
        tk.Label(
            search_frame, text="⌕", font=("Segoe UI", 14), bg=t["input"], fg=t["muted"]
        ).pack(side="left", padx=(10, 2))
        search = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=("Segoe UI", 10),
            bg=t["input"],
            fg=t["text"],
            insertbackground=t["text"],
            relief="flat",
            bd=0,
        )
        search.pack(side="left", fill="x", expand=True, ipady=8, padx=5)
        self.search_var.trace_add("write", lambda *_: self.refresh_tree())

        ttk.Combobox(
            filters,
            textvariable=self.filter_category_var,
            values=["All"] + CATEGORIES,
            state="readonly",
            width=15,
        ).pack(side="left", padx=4)
        cat_combo = filters.winfo_children()[-1]
        cat_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_tree())

        ttk.Combobox(
            filters,
            textvariable=self.filter_status_var,
            values=["All"] + STATUSES,
            state="readonly",
            width=14,
        ).pack(side="left", padx=4)
        status_combo = filters.winfo_children()[-1]
        status_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_tree())

        table = tk.Frame(card, bg=t["card"])
        table.pack(fill="both", expand=True, padx=18)

        columns = ("title", "category", "priority", "status", "due")
        self.tree = ttk.Treeview(
            table, columns=columns, show="headings", selectmode="browse"
        )

        widths = {
            "title": 300,
            "category": 130,
            "priority": 100,
            "status": 125,
            "due": 160,
        }
        headings = {
            "title": "TASK",
            "category": "CATEGORY",
            "priority": "PRIORITY",
            "status": "STATUS",
            "due": "DUE",
        }

        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(
                col, width=widths[col], anchor="w" if col == "title" else "center"
            )

        self.tree.tag_configure("urgent", foreground=t["red"])
        self.tree.tag_configure("high", foreground=t["orange"])
        self.tree.tag_configure("completed", foreground=t["green"])

        scrollbar = ttk.Scrollbar(table, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.tree.bind("<Double-1>", lambda e: self.edit_selected())

        actions = tk.Frame(card, bg=t["card"])
        actions.pack(fill="x", padx=18, pady=14)

        self.make_button(actions, "✓ Complete", self.complete_selected, "green").pack(
            side="left", padx=(0, 6)
        )
        self.make_button(actions, "✎ Edit", self.edit_selected, "primary").pack(
            side="left", padx=6
        )
        self.make_button(actions, "⌫ Delete", self.delete_selected, "red").pack(
            side="left", padx=6
        )

        self.refresh_tree()

    def filtered_tasks(self):
        query = self.search_var.get().strip().lower()
        category = self.filter_category_var.get()
        status = self.filter_status_var.get()

        result = []
        for task in self.tasks:
            if category != "All" and task.get("category") != category:
                continue
            if status != "All" and task.get("status") != status:
                continue

            text = " ".join(
                [
                    str(task.get("title", "")),
                    str(task.get("description", "")),
                    str(task.get("category", "")),
                    str(task.get("priority", "")),
                    str(task.get("status", "")),
                ]
            ).lower()

            if query and query not in text:
                continue
            result.append(task)

        return list(reversed(result))

    def refresh_tree(self):
        if not hasattr(self, "tree"):
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        for task in self.filtered_tasks():
            tag = ""
            if task.get("status") == "Completed":
                tag = "completed"
            elif task.get("priority") == "Urgent":
                tag = "urgent"
            elif task.get("priority") == "High":
                tag = "high"

            self.tree.insert(
                "",
                "end",
                iid=str(task.get("id")),
                values=(
                    task.get("title", ""),
                    task.get("category", ""),
                    task.get("priority", ""),
                    task.get("status", ""),
                    self.format_due(task.get("due_date"), task.get("due_time")),
                ),
                tags=(tag,) if tag else (),
            )

    def format_due(self, due_date, due_time):
        if due_date and due_time:
            return f"{due_date}  {due_time}"
        return due_date or due_time or "No due date"

    def selected_task(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Select a Task", "Please select a task first.")
            return None
        try:
            task_id = int(selection[0])
        except ValueError:
            return None
        return self.find_task(task_id)

    def complete_selected(self):
        task = self.selected_task()
        if not task:
            return
        if task.get("status") == "Completed":
            messagebox.showinfo("Already Complete", "This task is already completed.")
            return

        task["status"] = "Completed"
        task["updated_at"] = datetime.now().isoformat(timespec="seconds")
        self.save_tasks()
        self.refresh_tree()

    def edit_selected(self):
        task = self.selected_task()
        if not task:
            return
        self.selected_task_id = task.get("id")
        self.show_page("edit")

    def delete_selected(self):
        task = self.selected_task()
        if not task:
            return
        self.confirm_delete(task)

    def confirm_delete(self, task):
        if messagebox.askyesno(
            "Delete Task",
            f'Are you sure you want to delete:\n\n"{task.get("title", "Untitled")}"?',
        ):
            self.tasks = [
                item for item in self.tasks if item.get("id") != task.get("id")
            ]
            self.save_tasks()
            self.refresh_tree()

    # =========================================================
    # EDIT PAGE
    # =========================================================
    def build_edit_page(self):
        t = self.theme
        card = self.card(self.page_container)
        card.pack(fill="both", expand=True)

        tk.Label(
            card,
            text="Update Task",
            font=("Segoe UI", 16, "bold"),
            bg=t["card"],
            fg=t["text"],
        ).pack(anchor="w", padx=24, pady=(22, 3))
        tk.Label(
            card,
            text="Choose a task and update any of its details.",
            font=("Segoe UI", 9),
            bg=t["card"],
            fg=t["muted"],
        ).pack(anchor="w", padx=24, pady=(0, 18))

        body = tk.Frame(card, bg=t["card"])
        body.pack(fill="both", expand=True, padx=24, pady=(0, 20))

        self.edit_choice_var = tk.StringVar()
        choices = [self.choice_text(task) for task in self.tasks]

        self.field_label(body, "Select Task").pack(anchor="w")
        self.edit_combo = ttk.Combobox(
            body, textvariable=self.edit_choice_var, values=choices, state="readonly"
        )
        self.edit_combo.pack(fill="x", pady=(5, 14))
        self.edit_combo.bind("<<ComboboxSelected>>", lambda e: self.load_edit_fields())

        self.edit_title_var = tk.StringVar()
        self.edit_category_var = tk.StringVar()
        self.edit_priority_var = tk.StringVar()
        self.edit_status_var = tk.StringVar()
        self.edit_date_var = tk.StringVar()
        self.edit_time_var = tk.StringVar()

        self.field_label(body, "Task Name").pack(anchor="w")
        self.entry(body, self.edit_title_var).pack(fill="x", ipady=8, pady=(5, 12))

        self.field_label(body, "Description").pack(anchor="w")
        self.edit_desc = tk.Text(
            body,
            height=5,
            font=("Segoe UI", 10),
            bg=t["input"],
            fg=t["text"],
            insertbackground=t["text"],
            relief="flat",
            highlightthickness=1,
            highlightbackground=t["border"],
            highlightcolor=t["primary"],
            wrap="word",
        )
        self.edit_desc.pack(fill="x", pady=(5, 14))

        grid = tk.Frame(body, bg=t["card"])
        grid.pack(fill="x")
        for i in range(4):
            grid.columnconfigure(i, weight=1)

        edit_fields = [
            ("Category", self.edit_category_var, CATEGORIES),
            ("Priority", self.edit_priority_var, PRIORITIES),
            ("Status", self.edit_status_var, STATUSES),
        ]
        for i, (label, var, values) in enumerate(edit_fields):
            box = tk.Frame(grid, bg=t["card"])
            box.grid(row=0, column=i, sticky="ew", padx=(0 if i == 0 else 6, 6))
            self.field_label(box, label).pack(anchor="w")
            ttk.Combobox(box, textvariable=var, values=values, state="readonly").pack(
                fill="x", pady=(5, 0)
            )

        date_box = tk.Frame(grid, bg=t["card"])
        date_box.grid(row=0, column=3, sticky="ew", padx=(6, 0))

        self.field_label(date_box, "Due Date").pack(anchor="w")

        edit_date_controls = tk.Frame(date_box, bg=t["card"])
        edit_date_controls.pack(fill="x", pady=(5, 0))

        self.entry(edit_date_controls, self.edit_date_var).pack(
            side="left", fill="x", expand=True, ipady=7
        )

        tk.Button(
            edit_date_controls,
            text="📅 Select",
            command=lambda: self.choose_date(self.edit_date_var),
            font=("Segoe UI", 9, "bold"),
            bg=t["primary"],
            fg="white",
            activebackground=t["primary_dark"],
            activeforeground="white",
            relief="flat",
            bd=0,
            padx=10,
            pady=7,
            cursor="hand2",
        ).pack(side="left", padx=(6, 0))

        time_row = tk.Frame(body, bg=t["card"])
        time_row.pack(fill="x", pady=(14, 0))
        time_row.columnconfigure(0, weight=1)
        time_row.columnconfigure(1, weight=1)

        tb = tk.Frame(time_row, bg=t["card"])
        tb.grid(row=0, column=0, sticky="ew", padx=(0, 6))

        self.field_label(tb, "Due Time").pack(anchor="w")

        edit_time_controls = tk.Frame(tb, bg=t["card"])
        edit_time_controls.pack(fill="x", pady=(5, 0))

        self.entry(edit_time_controls, self.edit_time_var).pack(
            side="left", fill="x", expand=True, ipady=7
        )

        tk.Button(
            edit_time_controls,
            text="🕐 Select",
            command=lambda: self.choose_time(self.edit_time_var),
            font=("Segoe UI", 9, "bold"),
            bg=t["primary"],
            fg="white",
            activebackground=t["primary_dark"],
            activeforeground="white",
            relief="flat",
            bd=0,
            padx=10,
            pady=7,
            cursor="hand2",
        ).pack(side="left", padx=(6, 0))

        if self.selected_task_id:
            for index, task in enumerate(self.tasks):
                if task.get("id") == self.selected_task_id:
                    self.edit_choice_var.set(self.choice_text(task))
                    break
        elif choices:
            self.edit_choice_var.set(choices[0])

        if self.edit_choice_var.get():
            self.load_edit_fields()

        self.make_button(body, "Save Changes", self.apply_edit, "primary").pack(
            fill="x", pady=(22, 0)
        )

    def choice_text(self, task):
        return f"{task.get('id')}  •  {task.get('title', 'Untitled')[:45]}  •  {task.get('status', 'Pending')}"

    def parse_choice_id(self, text):
        try:
            return int(str(text).split("•")[0].strip())
        except (ValueError, IndexError):
            return None

    def load_edit_fields(self):
        task = self.find_task(self.parse_choice_id(self.edit_choice_var.get()))
        if not task:
            return

        self.selected_task_id = task.get("id")
        self.edit_title_var.set(task.get("title", ""))
        self.edit_category_var.set(task.get("category", "General"))
        self.edit_priority_var.set(task.get("priority", "Medium"))
        self.edit_status_var.set(task.get("status", "Pending"))
        self.edit_date_var.set(task.get("due_date", ""))
        self.edit_time_var.set(task.get("due_time", ""))

        self.edit_desc.delete("1.0", "end")
        self.edit_desc.insert("1.0", task.get("description", ""))

    def apply_edit(self):
        task = self.find_task(self.parse_choice_id(self.edit_choice_var.get()))
        if not task:
            messagebox.showwarning("Select a Task", "Please select a task to edit.")
            return

        title = self.edit_title_var.get().strip()
        category = self.edit_category_var.get().strip()
        priority = self.edit_priority_var.get().strip()
        status = self.edit_status_var.get().strip()
        due_date = self.edit_date_var.get().strip()
        due_time = self.edit_time_var.get().strip()
        description = self.edit_desc.get("1.0", "end-1c").strip()

        if not self.validate_task(
            title, category, priority, status, due_date, due_time
        ):
            return

        task.update(
            {
                "title": title,
                "description": description,
                "category": category,
                "priority": priority,
                "status": status,
                "due_date": due_date,
                "due_time": due_time,
                "updated_at": datetime.now().isoformat(timespec="seconds"),
            }
        )

        if self.save_tasks():
            messagebox.showinfo("Updated", "Task updated successfully.")
            self.selected_task_id = task.get("id")
            self.show_page("tasks")

    # =========================================================
    # DELETE PAGE
    # =========================================================
    def build_delete_page(self):
        t = self.theme
        card = self.card(self.page_container)
        card.pack(fill="both", expand=True)

        tk.Label(
            card,
            text="Delete Tasks",
            font=("Segoe UI", 16, "bold"),
            bg=t["card"],
            fg=t["text"],
        ).pack(anchor="w", padx=24, pady=(22, 3))
        tk.Label(
            card,
            text="Delete one task safely or remove all completed tasks.",
            font=("Segoe UI", 9),
            bg=t["card"],
            fg=t["muted"],
        ).pack(anchor="w", padx=24, pady=(0, 18))

        body = tk.Frame(card, bg=t["card"])
        body.pack(fill="both", expand=True, padx=24)

        self.delete_choice_var = tk.StringVar()
        self.field_label(body, "Select Task").pack(anchor="w")
        self.delete_combo = ttk.Combobox(
            body,
            textvariable=self.delete_choice_var,
            values=[self.choice_text(task) for task in self.tasks],
            state="readonly",
        )
        self.delete_combo.pack(fill="x", pady=(5, 12))
        self.delete_combo.bind(
            "<<ComboboxSelected>>", lambda e: self.show_delete_preview()
        )

        self.delete_preview = tk.Label(
            body,
            text="Select a task to preview its details.",
            font=("Segoe UI", 10),
            bg=t["input"],
            fg=t["text"],
            justify="left",
            anchor="nw",
            padx=16,
            pady=16,
            wraplength=900,
        )
        self.delete_preview.pack(fill="x", pady=(0, 18))

        if self.delete_combo["values"]:
            self.delete_combo.current(0)
            self.show_delete_preview()

        buttons = tk.Frame(body, bg=t["card"])
        buttons.pack(fill="x")

        self.make_button(
            buttons, "⌫ Delete Selected", self.delete_from_page, "red"
        ).pack(side="left", fill="x", expand=True, padx=(0, 6))

        self.make_button(
            buttons, "Delete All Completed", self.delete_all_completed, "orange"
        ).pack(side="left", fill="x", expand=True, padx=(6, 0))

    def show_delete_preview(self):
        task = self.find_task(self.parse_choice_id(self.delete_choice_var.get()))
        if not task:
            self.delete_preview.config(text="No task selected.")
            return

        due = self.format_due(task.get("due_date"), task.get("due_time"))
        text = (
            f"TITLE     {task.get('title', 'Untitled')}\n"
            f"CATEGORY  {task.get('category', 'General')}\n"
            f"PRIORITY  {task.get('priority', 'Medium')}\n"
            f"STATUS    {task.get('status', 'Pending')}\n"
            f"DUE       {due}\n\n"
            f"DESCRIPTION\n{task.get('description') or 'No description'}"
        )
        self.delete_preview.config(text=text)

    def delete_from_page(self):
        task = self.find_task(self.parse_choice_id(self.delete_choice_var.get()))
        if not task:
            messagebox.showwarning("Select a Task", "Please select a task.")
            return
        self.confirm_delete(task)
        self.show_page("delete")

    def delete_all_completed(self):
        completed = self.count_status("Completed")
        if completed == 0:
            messagebox.showinfo("Nothing to Delete", "There are no completed tasks.")
            return

        if messagebox.askyesno(
            "Delete Completed Tasks",
            f"Delete all {completed} completed task(s)?\n\nThis cannot be undone.",
        ):
            self.tasks = [
                task for task in self.tasks if task.get("status") != "Completed"
            ]
            self.save_tasks()
            messagebox.showinfo("Deleted", "Completed tasks have been removed.")
            if self.current_page == "delete":
                self.show_page("delete")

    # =========================================================
    # REPORTS
    # =========================================================
    def build_reports_page(self):
        t = self.theme
        card = self.card(self.page_container)
        card.pack(fill="both", expand=True)

        tk.Label(
            card,
            text="Reports & Export",
            font=("Segoe UI", 16, "bold"),
            bg=t["card"],
            fg=t["text"],
        ).pack(anchor="w", padx=24, pady=(22, 3))
        tk.Label(
            card,
            text="Export your task data in TXT, CSV, or JSON format.",
            font=("Segoe UI", 9),
            bg=t["card"],
            fg=t["muted"],
        ).pack(anchor="w", padx=24, pady=(0, 20))

        summary = tk.Frame(card, bg=t["card"])
        summary.pack(fill="x", padx=24)

        stats = [
            ("Pending", self.count_status("Pending"), t["orange"]),
            ("In Progress", self.count_status("In Progress"), t["accent"]),
            ("Completed", self.count_status("Completed"), t["green"]),
            ("Total", len(self.tasks), t["primary"]),
        ]
        for label, value, color in stats:
            box = tk.Frame(
                summary,
                bg=t["input"],
                highlightbackground=t["border"],
                highlightthickness=1,
            )
            box.pack(side="left", fill="both", expand=True, padx=5)
            tk.Label(
                box,
                text=str(value),
                font=("Segoe UI", 22, "bold"),
                bg=t["input"],
                fg=color,
            ).pack(pady=(12, 0))
            tk.Label(
                box,
                text=label,
                font=("Segoe UI", 9, "bold"),
                bg=t["input"],
                fg=t["muted"],
            ).pack(pady=(0, 12))

        export_box = self.card(card)
        export_box.pack(fill="x", padx=24, pady=24)

        tk.Label(
            export_box,
            text="Download Data",
            font=("Segoe UI", 12, "bold"),
            bg=t["card"],
            fg=t["text"],
        ).pack(anchor="w", padx=18, pady=(16, 3))
        tk.Label(
            export_box,
            text="Choose the format you need.",
            font=("Segoe UI", 8),
            bg=t["card"],
            fg=t["muted"],
        ).pack(anchor="w", padx=18)

        row = tk.Frame(export_box, bg=t["card"])
        row.pack(fill="x", padx=18, pady=16)

        self.make_button(row, "TXT Report", self.download_txt, "primary").pack(
            side="left", fill="x", expand=True, padx=(0, 6)
        )
        self.make_button(row, "CSV File", self.download_csv, "accent").pack(
            side="left", fill="x", expand=True, padx=6
        )
        self.make_button(row, "JSON File", self.download_json, "secondary").pack(
            side="left", fill="x", expand=True, padx=(6, 0)
        )

        note = self.card(card)
        note.pack(fill="x", padx=24)
        tk.Label(
            note,
            text="✓  Automatic storage",
            font=("Segoe UI", 10, "bold"),
            bg=t["card"],
            fg=t["green"],
        ).pack(anchor="w", padx=18, pady=(14, 2))
        tk.Label(
            note,
            text="Tasks are automatically saved to tasks.json whenever you add, edit, complete, or delete data.",
            font=("Segoe UI", 9),
            bg=t["card"],
            fg=t["muted"],
            wraplength=900,
            justify="left",
        ).pack(anchor="w", padx=18, pady=(0, 14))

    def ensure_tasks_for_export(self):
        if not self.tasks:
            messagebox.showinfo("No Data", "There are no tasks to export.")
            return False
        return True

    def download_report(self):
        if not self.ensure_tasks_for_export():
            return

        path = filedialog.asksaveasfilename(
            title="Export TaskFlow Report",
            defaultextension=".txt",
            filetypes=[
                ("Text report", "*.txt"),
                ("CSV file", "*.csv"),
                ("JSON file", "*.json"),
            ],
            initialfile=f"TaskFlow_Report_{datetime.now().strftime('%Y%m%d_%H%M')}",
        )
        if not path:
            return

        ext = os.path.splitext(path)[1].lower()
        try:
            if ext == ".csv":
                self.write_csv(path)
            elif ext == ".json":
                self.write_json(path)
            else:
                self.write_txt(path)
            messagebox.showinfo("Export Complete", f"Report saved to:\n{path}")
        except OSError as exc:
            messagebox.showerror("Export Error", str(exc))

    def download_txt(self):
        self.export_single(".txt", [("Text report", "*.txt")], self.write_txt)

    def download_csv(self):
        self.export_single(".csv", [("CSV file", "*.csv")], self.write_csv)

    def download_json(self):
        self.export_single(".json", [("JSON file", "*.json")], self.write_json)

    def export_single(self, extension, filetypes, writer):
        if not self.ensure_tasks_for_export():
            return

        path = filedialog.asksaveasfilename(
            title="Save TaskFlow Export",
            defaultextension=extension,
            filetypes=filetypes,
            initialfile=f"TaskFlow_Report_{datetime.now().strftime('%Y%m%d_%H%M')}",
        )
        if not path:
            return

        try:
            writer(path)
            messagebox.showinfo("Export Complete", f"Saved to:\n{path}")
        except OSError as exc:
            messagebox.showerror("Export Error", str(exc))

    def write_txt(self, path):
        with open(path, "w", encoding="utf-8") as file:
            file.write("=" * 70 + "\n")
            file.write("TASKFLOW PRO REPORT\n")
            file.write("=" * 70 + "\n")
            file.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            file.write(
                f"Total: {len(self.tasks)} | "
                f"Pending: {self.count_status('Pending')} | "
                f"In Progress: {self.count_status('In Progress')} | "
                f"Completed: {self.count_status('Completed')}\n"
            )
            file.write("-" * 70 + "\n\n")

            for index, task in enumerate(self.tasks, 1):
                file.write(f"{index}. {task.get('title', 'Untitled')}\n")
                file.write(f"   Category : {task.get('category', '')}\n")
                file.write(f"   Priority : {task.get('priority', '')}\n")
                file.write(f"   Status   : {task.get('status', '')}\n")
                file.write(
                    f"   Due      : {self.format_due(task.get('due_date'), task.get('due_time'))}\n"
                )
                if task.get("description"):
                    file.write(f"   Notes    : {task.get('description')}\n")
                file.write("\n")

    def write_csv(self, path):
        with open(path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(
                [
                    "ID",
                    "Title",
                    "Description",
                    "Category",
                    "Priority",
                    "Status",
                    "Due Date",
                    "Due Time",
                    "Created At",
                    "Updated At",
                ]
            )
            for task in self.tasks:
                writer.writerow(
                    [
                        task.get("id"),
                        task.get("title"),
                        task.get("description"),
                        task.get("category"),
                        task.get("priority"),
                        task.get("status"),
                        task.get("due_date"),
                        task.get("due_time"),
                        task.get("created_at"),
                        task.get("updated_at"),
                    ]
                )

    def write_json(self, path):
        with open(path, "w", encoding="utf-8") as file:
            json.dump(self.tasks, file, indent=4, ensure_ascii=False)

    # =========================================================
    # FEEDBACK
    # =========================================================
    def build_feedback_page(self):
        t = self.theme
        card = self.card(self.page_container)
        card.pack(fill="both", expand=True)

        tk.Label(
            card,
            text="Contact & Feedback",
            font=("Segoe UI", 16, "bold"),
            bg=t["card"],
            fg=t["text"],
        ).pack(anchor="w", padx=24, pady=(22, 3))
        tk.Label(
            card,
            text="Send feedback or suggestions. Your message is stored locally.",
            font=("Segoe UI", 9),
            bg=t["card"],
            fg=t["muted"],
        ).pack(anchor="w", padx=24, pady=(0, 20))

        body = tk.Frame(card, bg=t["card"])
        body.pack(fill="both", expand=True, padx=24)

        self.field_label(body, "Name *").pack(anchor="w")
        self.entry(body, self.feedback_name).pack(fill="x", ipady=8, pady=(5, 12))

        self.field_label(body, "Email (optional)").pack(anchor="w")
        self.entry(body, self.feedback_email).pack(fill="x", ipady=8, pady=(5, 12))

        self.field_label(body, "Message *").pack(anchor="w")
        self.feedback_message = tk.Text(
            body,
            height=8,
            font=("Segoe UI", 10),
            bg=t["input"],
            fg=t["text"],
            insertbackground=t["text"],
            relief="flat",
            highlightthickness=1,
            highlightbackground=t["border"],
            highlightcolor=t["primary"],
            wrap="word",
        )
        self.feedback_message.pack(fill="x", pady=(5, 15))

        self.make_button(body, "Send Feedback", self.submit_feedback, "primary").pack(
            fill="x"
        )

    def submit_feedback(self):
        name = self.feedback_name.get().strip()
        email = self.feedback_email.get().strip()
        message = self.feedback_message.get("1.0", "end-1c").strip()

        if not name or not message:
            messagebox.showwarning(
                "Required Fields", "Please enter your name and message."
            )
            return

        data = []
        if os.path.exists(FEEDBACK_FILE):
            try:
                with open(FEEDBACK_FILE, "r", encoding="utf-8") as file:
                    loaded = json.load(file)
                    if isinstance(loaded, list):
                        data = loaded
            except (OSError, json.JSONDecodeError):
                data = []

        data.append(
            {
                "name": name,
                "email": email,
                "message": message,
                "time": datetime.now().isoformat(timespec="seconds"),
            }
        )

        try:
            with open(FEEDBACK_FILE, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
        except OSError as exc:
            messagebox.showerror("Feedback Error", str(exc))
            return

        self.feedback_name.set("")
        self.feedback_email.set("")
        self.feedback_message.delete("1.0", "end")
        messagebox.showinfo("Thank You", "Your feedback has been saved successfully.")

    # =========================================================
    # THEME
    # =========================================================
    def toggle_theme(self):
        self.is_dark = not self.is_dark
        self.theme = DARK if self.is_dark else LIGHT
        self.setup_styles()
        self.build_ui()

    # =========================================================
    # CLOSE
    # =========================================================
    def on_close(self):
        self.save_tasks()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = TaskFlowApp(root)
    root.mainloop()
