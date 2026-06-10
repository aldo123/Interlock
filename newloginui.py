import customtkinter as ctk
from PIL import Image
from datetime import datetime
import tkinter as tk

from interlockform import InterlockForm
from database import DatabaseManager


# ==========================================================
# CONFIG
# ==========================================================
WIDTH  = 1400
HEIGHT = 720

GREEN       = "#22C55E"
LIGHT_GREEN = "#3CB371"
DARK_BG     = "#0F172A"
PANEL_BG    = "#111827"
CARD_BG     = "#1E293B"
BORDER      = "#334155"
TEXT        = "#E2E8F0"
TEXT2       = "#94A3B8"

ctk.set_appearance_mode("dark")
# color_theme tidak di-set di sini — dihandle oleh newmainform.py


class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.overrideredirect(True)

        screen_width  = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = int((screen_width  - WIDTH)  / 2)
        y = int((screen_height - HEIGHT) / 2)

        self.geometry(f"{WIDTH}x{HEIGHT}+{x}+{y}")
        self.configure(fg_color=DARK_BG)

        self.login_mode      = "card"
        self.clock_job       = None
        self.loading_job     = None
        self.loading_percent = 0

        self.db = DatabaseManager()
        self.db.connect()

        self.build_ui()
        self.update_clock()
        self.animate_loading()

    # ======================================================
    # DESTROY — batalkan semua after jobs
    # ======================================================
    def destroy(self):
        try:
            for after_id in self.tk.call('after', 'info').split():
                try:
                    self.after_cancel(after_id)
                except Exception:
                    pass
        except Exception:
            pass
        super().destroy()

    # ======================================================
    # UI
    # ======================================================
    def build_ui(self):

        # ── DRAG support (karena overrideredirect) ────────
        self.bind("<ButtonPress-1>",   self._drag_start)
        self.bind("<B1-Motion>",       self._drag_motion)

        # MAIN container — warna sama dengan background gelap
        self.main = ctk.CTkFrame(self, fg_color=DARK_BG, corner_radius=0)
        self.main.pack(fill="both", expand=True)

        # ==================================================
        # LEFT — gambar dengan overlay gelap agar menyatu
        # ==================================================
        self.left_panel = ctk.CTkFrame(
            self.main,
            fg_color=DARK_BG,
            corner_radius=0
        )
        self.left_panel.pack(side="left", fill="both", expand=True)

        # Canvas untuk gambar + overlay
        self.canvas = tk.Canvas(
            self.left_panel,
            bg=DARK_BG,
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)

        # Load gambar dengan overlay gelap
        self._load_bg_image()

        # Bind resize
        self.canvas.bind("<Configure>", self._on_canvas_resize)

        # ==================================================
        # RIGHT LOGIN PANEL
        # ==================================================
        self.right_panel = ctk.CTkFrame(
            self.main,
            width=400,
            fg_color=PANEL_BG,
            corner_radius=0,
            border_width=1,
            border_color=BORDER
        )
        self.right_panel.pack(side="right", fill="y")
        self.right_panel.pack_propagate(False)

        # ── Title bar kustom ──────────────────────────────
        title_bar = ctk.CTkFrame(self.right_panel, fg_color="transparent", height=40)
        title_bar.pack(fill="x")
        title_bar.pack_propagate(False)

        self.close_btn = ctk.CTkButton(
            title_bar,
            text="✖",
            width=32, height=32,
            fg_color="transparent",
            hover_color="#7F1D1D",
            text_color="#EF4444",
            font=("Segoe UI", 13),
            corner_radius=4,
            command=self.destroy
        )
        self.close_btn.pack(anchor="ne", padx=8, pady=4)

        # ── LOGO ──────────────────────────────────────────
        logo_frame = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        logo_frame.pack(pady=(8, 0))

        ctk.CTkLabel(
            logo_frame,
            text="WIK",
            font=("Segoe UI", 46, "bold"),
            text_color=GREEN
        ).pack()

        ctk.CTkLabel(
            logo_frame,
            text="Technology  ·  attuned to Nature",
            font=("Segoe UI", 12),
            text_color=TEXT2
        ).pack()

        # Divider tipis
        ctk.CTkFrame(
            logo_frame,
            height=1,
            fg_color=BORDER,
            width=260
        ).pack(pady=(10, 0))

        ctk.CTkLabel(
            logo_frame,
            text="EE — Interlock & Traceability",
            font=("Segoe UI", 15, "bold"),
            text_color=TEXT
        ).pack(pady=(8, 0))

        # ── TABS ──────────────────────────────────────────
        tab_frame = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        tab_frame.pack(fill="x", padx=40, pady=(28, 0))

        self.card_tab = ctk.CTkButton(
            tab_frame,
            text="Card Number",
            fg_color="transparent",
            hover=False,
            text_color=GREEN,
            font=("Segoe UI", 12),
            width=80,
            command=lambda: self.switch_mode("card")
        )
        self.card_tab.pack(side="left")

        self.pass_tab = ctk.CTkButton(
            tab_frame,
            text="Password",
            fg_color="transparent",
            hover=False,
            text_color=TEXT2,
            font=("Segoe UI", 12),
            width=80,
            command=lambda: self.switch_mode("password")
        )
        self.pass_tab.pack(side="left", padx=16)

        self.tab_line = ctk.CTkFrame(
            self.right_panel, height=2, fg_color=GREEN
        )
        self.tab_line.pack(fill="x", padx=40, pady=(6, 0))

        # ── LOGIN FIELDS ──────────────────────────────────
        self.login_frame = ctk.CTkFrame(
            self.right_panel, fg_color="transparent"
        )
        self.login_frame.pack(fill="x", padx=40, pady=(20, 0))

        entry_cfg = dict(
            height=44,
            corner_radius=8,
            fg_color=CARD_BG,
            border_color=BORDER,
            border_width=1,
            text_color=TEXT,
            font=("Segoe UI", 13)
        )

        self.card_entry = ctk.CTkEntry(
            self.login_frame,
            placeholder_text="  🪪  Scan Card Number",
            **entry_cfg
        )
        self.card_entry.bind("<Return>", self.card_login)

        self.username_entry = ctk.CTkEntry(
            self.login_frame,
            placeholder_text="  👤  Username",
            **entry_cfg
        )

        self.password_entry = ctk.CTkEntry(
            self.login_frame,
            show="*",
            placeholder_text="  🔒  Password",
            **entry_cfg
        )
        self.password_entry.bind("<Return>", lambda e: self.login())

        # ── LOGIN BUTTON ──────────────────────────────────
        self.login_btn = ctk.CTkButton(
            self.right_panel,
            text="LOGIN",
            height=46,
            fg_color=GREEN,
            hover_color="#16A34A",
            text_color="#052E16",
            font=("Segoe UI", 15, "bold"),
            corner_radius=8,
            state="disabled",
            command=self.login
        )
        self.login_btn.pack(fill="x", padx=40, pady=24)

        # ── CLOCK ─────────────────────────────────────────
        self.clock_label = ctk.CTkLabel(
            self.right_panel,
            text="",
            font=("Segoe UI", 11),
            text_color=TEXT2
        )
        self.clock_label.pack()

        # spacer
        ctk.CTkFrame(self.right_panel, fg_color="transparent").pack(
            fill="both", expand=True
        )

        # ── FOOTER ────────────────────────────────────────
        footer = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        footer.place(relx=0.05, rely=0.968, relwidth=0.90, anchor="sw")

        self.version_label = ctk.CTkLabel(
            footer,
            text="v1.0.0.1008",
            font=("Segoe UI", 10),
            text_color=TEXT2
        )
        self.version_label.pack(side="left")

        self.db_label = ctk.CTkLabel(
            footer,
            text="● Database",
            font=("Segoe UI", 10, "bold")
        )
        self.db_label.pack(side="left", padx=(12, 0))
        self.update_database_status()

        self.setting_btn = ctk.CTkButton(
            footer,
            text="⚙",
            width=28, height=28,
            fg_color="transparent",
            hover_color=CARD_BG,
            text_color=TEXT2,
            font=("Segoe UI Symbol", 16),
            command=self.open_interlock_setting
        )
        self.setting_btn.pack(side="right")

        # ── STATUS BAR (bawah panel kiri) ─────────────────
        status_bar = ctk.CTkFrame(
            self.left_panel,
            fg_color=PANEL_BG,
            height=28,
            corner_radius=0
        )
        status_bar.pack(side="bottom", fill="x")
        status_bar.pack_propagate(False)

        self.progress = ctk.CTkProgressBar(
            status_bar,
            height=4,
            progress_color=GREEN,
            fg_color=CARD_BG,
            corner_radius=0
        )
        self.progress.pack(fill="x")
        self.progress.set(0)

        self.loading_label = ctk.CTkLabel(
            status_bar,
            text="System Loading... 0%",
            text_color=GREEN,
            font=("Segoe UI", 9, "bold")
        )
        self.loading_label.pack(anchor="w", padx=10)

        self.switch_mode("card")

    # ======================================================
    # BACKGROUND IMAGE dengan overlay gelap
    # ======================================================
    def _load_bg_image(self):
        """Load & proses gambar SEKALI saja saat startup — simpan sebagai _raw_img."""
        self._raw_img = None
        try:
            import numpy as np
            img = Image.open("factory.png").convert("RGB")

            # Gelap-kan 45% brightness dengan numpy (cepat)
            arr = np.array(img, dtype=np.float32)
            arr *= 0.45
            arr = np.clip(arr, 0, 255).astype(np.uint8)
            self._raw_img = Image.fromarray(arr)
        except Exception:
            pass
        self._draw_bg()

    def _draw_bg(self):
        if not hasattr(self, 'canvas'):
            return
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 2 or h < 2:
            self.after(50, self._draw_bg)
            return

        self.canvas.delete("all")

        if self._raw_img:
            import numpy as np

            # Resize gambar ke ukuran canvas
            img = self._raw_img.copy().resize((w, h), Image.BILINEAR)
            arr = np.array(img, dtype=np.float32)   # shape: (h, w, 3)

            # ── Gradient kiri→kanan (makin kanan makin gelap) ──
            # alpha 0 di kiri, 0.7 di kanan
            grad_x = np.linspace(0, 0.7, w, dtype=np.float32)  # (w,)
            grad_x = grad_x[np.newaxis, :, np.newaxis]          # (1, w, 1)

            bg_color = np.array([15, 23, 42], dtype=np.float32) # #0F172A

            # blend: pixel = pixel*(1-alpha) + bg*alpha
            arr = arr * (1 - grad_x) + bg_color * grad_x

            # ── Gradient bawah (60px terakhir fade ke gelap) ──
            fade_h = 60
            if h > fade_h:
                grad_y = np.linspace(0, 0.85, fade_h, dtype=np.float32)
                grad_y = grad_y[:, np.newaxis, np.newaxis]              # (fade_h,1,1)
                arr[-fade_h:] = (
                    arr[-fade_h:] * (1 - grad_y) + bg_color * grad_y
                )

            arr = np.clip(arr, 0, 255).astype(np.uint8)
            img_out = Image.fromarray(arr)

            from PIL import ImageTk
            self._tk_img = ImageTk.PhotoImage(img_out)
            self.canvas.create_image(0, 0, anchor="nw", image=self._tk_img)
        else:
            self.canvas.create_rectangle(0, 0, w, h, fill=DARK_BG, outline="")

        # Teks overlay pojok kiri bawah
        self.canvas.create_text(
            20, h - 70,
            text="WIK Manufacturing Execution System",
            font=("Segoe UI", 18, "bold"),
            fill="#22C55E",
            anchor="sw"
        )
        self.canvas.create_text(
            20, h - 46,
            text="Real-time Interlock & Traceability Platform",
            font=("Segoe UI", 11),
            fill="#94A3B8",
            anchor="sw"
        )

    def _on_canvas_resize(self, event):
        self._draw_bg()

    # ======================================================
    # DRAG (karena overrideredirect)
    # ======================================================
    def _drag_start(self, event):
        self._drag_x = event.x_root - self.winfo_x()
        self._drag_y = event.y_root - self.winfo_y()

    def _drag_motion(self, event):
        x = event.x_root - self._drag_x
        y = event.y_root - self._drag_y
        self.geometry(f"+{x}+{y}")

    # ======================================================
    # CLOCK
    # ======================================================
    def update_clock(self):
        if not self.winfo_exists():
            return
        now = datetime.now().strftime("%A, %d %B %Y   %H:%M:%S")
        self.clock_label.configure(text=now)
        self.clock_job = self.after(1000, self.update_clock)

    # ======================================================
    # DATABASE STATUS
    # ======================================================
    def update_database_status(self):
        try:
            if self.db.is_connected():
                self.db_label.configure(
                    text="● DB Connected", text_color=GREEN
                )
            else:
                self.db_label.configure(
                    text="● DB Disconnected", text_color="#EF4444"
                )
        except Exception:
            self.db_label.configure(
                text="● B Disconnected", text_color="#EF4444"
            )

    # ======================================================
    # LOADING ANIMATION
    # ======================================================
    def animate_loading(self):
        if self.loading_percent <= 100:
            self.progress.set(self.loading_percent / 100)
            self.loading_label.configure(
                text=f"System Loading...  {self.loading_percent}%"
            )
            self.loading_percent += 1
            self.loading_job = self.after(25, self.animate_loading)
        else:
            self.progress.set(1)
            self.loading_label.configure(text="✓  System Ready")
            self.loading_job = None
            self.login_btn.configure(state="normal")

    # ======================================================
    # SETTING
    # ======================================================
    def open_interlock_setting(self):
        try:
            InterlockForm().show(self)
        except Exception as e:
            print("Interlock Error:", e)

    # ======================================================
    # LOGIN
    # ======================================================
    def card_login(self, event=None):
        card_id = self.card_entry.get().strip()
        if not card_id:
            return
        sql = """
            SELECT username, role, id_card
            FROM users
            WHERE id_card = %s
            LIMIT 1
        """
        user = self.db.fetch_one(sql, (card_id,))
        if user:
            self.open_main_ui(user)
        else:
            tk.messagebox.showerror("Login Failed", "Card Number Not Registered")
            self.card_entry.delete(0, "end")

    def login(self):
        if self.login_mode == "card":
            self.card_login()
        else:
            username = self.username_entry.get().strip()
            password = self.password_entry.get().strip()
            if not username or not password:
                tk.messagebox.showwarning("Warning", "Please enter username and password")
                return
            sql = """
                SELECT username, role, id_card
                FROM users
                WHERE username=%s AND password=%s
                LIMIT 1
            """
            user = self.db.fetch_one(sql, (username, password))
            if user:
                self.open_main_ui(user)
            else:
                tk.messagebox.showerror("Login Failed", "Invalid Username or Password")

    def open_main_ui(self, user):
        self.destroy()
        from newmainform import NewMainForm
        app = NewMainForm(user)
        app.mainloop()

    # ======================================================
    # SWITCH MODE
    # ======================================================
    def switch_mode(self, mode):
        self.login_mode = mode
        self.card_entry.pack_forget()
        self.username_entry.pack_forget()
        self.password_entry.pack_forget()

        if mode == "card":
            self.card_tab.configure(text_color=GREEN)
            self.pass_tab.configure(text_color=TEXT2)
            self.tab_line.configure(fg_color=GREEN)
            self.card_entry.pack(fill="x")
        else:
            self.card_tab.configure(text_color=TEXT2)
            self.pass_tab.configure(text_color=GREEN)
            self.tab_line.configure(fg_color=GREEN)
            self.username_entry.pack(fill="x", pady=(0, 10))
            self.password_entry.pack(fill="x")


if __name__ == "__main__":
    app = LoginWindow()
    app.mainloop()