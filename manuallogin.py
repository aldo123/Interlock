import customtkinter as ctk

# ==========================================================
# CONFIG
# ==========================================================
GREEN      = "#22C55E"
DARK_BG    = "#0F172A"
PANEL_BG   = "#111827"
CARD_BG    = "#1E293B"
BORDER     = "#334155"
TEXT       = "#E2E8F0"
TEXT2      = "#94A3B8"
PURPLE     = "#7C3AED"
PURPLE_HOV = "#6D28D9"

ctk.set_appearance_mode("dark")


class ManualLoginDialog(ctk.CTkToplevel):

    def __init__(self, parent):
        super().__init__(parent)

        # Hapus title bar (minimize/maximize/close)
        self.overrideredirect(True)

        self.grab_set()
        self.lift()
        self.focus_force()

        W, H = 400, 480
        px = parent.winfo_rootx() + (parent.winfo_width()  - W) // 2
        py = parent.winfo_rooty() + (parent.winfo_height() - H) // 2
        self.geometry(f"{W}x{H}+{px}+{py}")
        self.configure(fg_color=DARK_BG)

        self._show_pwd = False
        self._build_ui()

        self.bind("<Escape>", lambda e: self.destroy())

    def _build_ui(self):
        # Card utama dengan border hijau seperti screenshot
        card = ctk.CTkFrame(self, fg_color=PANEL_BG, corner_radius=16,
                            border_width=2, border_color=GREEN)
        card.pack(fill="both", expand=True, padx=10, pady=10)

        # ── Lock badge — center ──────────────────────────────
        badge = ctk.CTkFrame(card, width=64, height=64,
                             corner_radius=32, fg_color=GREEN)
        badge.pack(pady=(24, 0), anchor="center")
        badge.pack_propagate(False)
        ctk.CTkLabel(badge, text="🔒", font=("Segoe UI", 24),
                     text_color="#052E16").place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(card, text="Engineer Access Required",
                     font=("Segoe UI", 11), text_color=TEXT2,
                     justify="center").pack(pady=(8, 0), anchor="center")

        # ── Fields ──────────────────────────────────────────
        f = ctk.CTkFrame(card, fg_color="transparent")
        f.pack(fill="x", padx=32, pady=(16, 0))

        entry_cfg = dict(
            height=44, corner_radius=8,
            fg_color=CARD_BG, border_color=BORDER, border_width=1,
            text_color=TEXT, font=("Segoe UI", 13)
        )

        # UserName
        ctk.CTkLabel(f, text="UserName", font=("Segoe UI", 11),
                     text_color=TEXT2, anchor="w").pack(fill="x")
        self.username_entry = ctk.CTkEntry(
            f, placeholder_text="  👤  Username", **entry_cfg)
        self.username_entry.pack(fill="x", pady=(4, 12))
        self.username_entry.bind("<FocusIn>",
            lambda e: self.username_entry.configure(border_color=GREEN))
        self.username_entry.bind("<FocusOut>",
            lambda e: self.username_entry.configure(border_color=BORDER))

        # Password
        ctk.CTkLabel(f, text="Password", font=("Segoe UI", 11),
                     text_color=TEXT2, anchor="w").pack(fill="x")

        pwd_row = ctk.CTkFrame(f, fg_color="transparent")
        pwd_row.pack(fill="x", pady=(4, 0))

        self.password_entry = ctk.CTkEntry(
            pwd_row, show="*",
            placeholder_text="  🔒  Password", **entry_cfg)
        self.password_entry.pack(side="left", fill="x", expand=True)
        self.password_entry.bind("<FocusIn>",
            lambda e: self.password_entry.configure(border_color=GREEN))
        self.password_entry.bind("<FocusOut>",
            lambda e: self.password_entry.configure(border_color=BORDER))

        self.eye_btn = ctk.CTkButton(
            pwd_row, text="👁", width=44, height=44,
            fg_color="#1A5C34", hover_color="#166534",
            text_color=TEXT, corner_radius=8,
            font=("Segoe UI", 15), command=self._toggle_pwd)
        self.eye_btn.pack(side="left", padx=(5, 0))

        # ── Cancel / OK ──────────────────────────────────────
        btn_row = ctk.CTkFrame(f, fg_color="transparent")
        btn_row.pack(fill="x", pady=(16, 0))

        ctk.CTkButton(
            btn_row, text="Cancel", height=44,
            fg_color="#374151", hover_color="#4B5563",
            text_color=TEXT, font=("Segoe UI", 13),
            corner_radius=8, border_width=1, border_color=BORDER,
            command=self.destroy
        ).pack(side="left", fill="x", expand=True, padx=(0, 6))

        ctk.CTkButton(
            btn_row, text="OK", height=44,
            fg_color=PURPLE, hover_color=PURPLE_HOV,
            text_color="#FFFFFF", font=("Segoe UI", 13, "bold"),
            corner_radius=8, command=self._on_ok
        ).pack(side="left", fill="x", expand=True, padx=(6, 0))

        # ── Divider ──────────────────────────────────────────
        ctk.CTkFrame(card, height=1, fg_color=BORDER).pack(
            fill="x", padx=32, pady=(18, 0))

        # ── ID Card field ─────────────────────────────────────
        bot = ctk.CTkFrame(card, fg_color="transparent")
        bot.pack(fill="x", padx=32, pady=(12, 20))

        card_row = ctk.CTkFrame(bot, fg_color="transparent")
        card_row.pack(fill="x")

        card_icon = ctk.CTkFrame(card_row, width=44, height=44,
                                 corner_radius=8, fg_color=CARD_BG,
                                 border_width=1, border_color=BORDER)
        card_icon.pack(side="left", padx=(0, 5))
        card_icon.pack_propagate(False)
        ctk.CTkLabel(card_icon, text="🪪", font=("Segoe UI", 18),
                     text_color=TEXT2).place(relx=0.5, rely=0.5, anchor="center")

        self.card_entry = ctk.CTkEntry(
            card_row,
            placeholder_text="  Scan / tempel ID Card di sini...",
            height=44, corner_radius=8,
            fg_color=CARD_BG, border_color=BORDER, border_width=1,
            text_color=TEXT, font=("Segoe UI", 12))
        self.card_entry.pack(side="left", fill="x", expand=True)
        # AUTO LOGIN SAAT ENTER
        self.card_entry.bind("<Return>", lambda e: self._on_ok())
        self.card_entry.bind("<FocusIn>",
            lambda e: self.card_entry.configure(border_color=GREEN))
        self.card_entry.bind("<FocusOut>",
            lambda e: self.card_entry.configure(border_color=BORDER))

        self.username_entry.focus()

    def _toggle_pwd(self):
        self._show_pwd = not self._show_pwd
        self.password_entry.configure(show="" if self._show_pwd else "*")
        self.eye_btn.configure(fg_color="#15803D" if self._show_pwd else "#1A5C34")

    def _on_ok(self):
        self.username = self.username_entry.get().strip()
        self.password = self.password_entry.get().strip()
        self.card_id  = self.card_entry.get().strip()
        self.destroy()