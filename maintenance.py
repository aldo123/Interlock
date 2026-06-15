import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import csv, os
from tkcalendar import DateEntry

# ──────────────────────────────────────────────────────────
# COLOURS
# ──────────────────────────────────────────────────────────
GREEN      = "#22C55E"
GREEN_HOV  = "#16A34A"
DARK_BG    = "#0B1120"
PANEL_BG   = "#0F1729"
CARD_BG    = "#1A2540"
BORDER     = "#243050"
TEXT       = "#E2E8F0"
TEXT2      = "#7A8FB0"
RED        = "#EF4444"
ORANGE     = "#F97316"
BLUE       = "#3B82F6"
YELLOW     = "#EAB308"
PURPLE     = "#A855F7"

ctk.set_appearance_mode("dark")

# ──────────────────────────────────────────────────────────
# DATABASE
# ──────────────────────────────────────────────────────────
class MaintenanceDB:
    def __init__(self, path="maintenance.db"):
        self.path = path
        self._init_db()

    def cx(self):
        return sqlite3.connect(self.path)

    def _init_db(self):
        with self.cx() as c:
            c.execute("""CREATE TABLE IF NOT EXISTS downtime_events(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                downtime_id TEXT, start_time TEXT, end_time TEXT,
                duration TEXT, downtime_type TEXT, root_cause TEXT,
                corrective_action TEXT, technician TEXT, shift TEXT,
                notes TEXT, machine_code TEXT,
                created_at TEXT DEFAULT(datetime('now','localtime')))""")
            c.execute("""CREATE TABLE IF NOT EXISTS machine_config(
                key TEXT PRIMARY KEY, value TEXT)""")
            for k,v in [("machine_code","CP2-PCBAVM3"),("line_code","BW01-VM3"),
                        ("spec_code","CP2-PCBAVM3"),("technician","Aldo"),("shift","Shift A")]:
                c.execute("INSERT OR IGNORE INTO machine_config VALUES(?,?)",(k,v))

    def get_config(self):
        with self.cx() as c:
            return dict(c.execute("SELECT key,value FROM machine_config").fetchall())

    def insert_downtime(self, d):
        with self.cx() as c:
            c.execute("""INSERT INTO downtime_events
                (downtime_id,start_time,end_time,duration,downtime_type,
                 root_cause,corrective_action,technician,shift,notes,machine_code)
                VALUES(:downtime_id,:start_time,:end_time,:duration,:downtime_type,
                       :root_cause,:corrective_action,:technician,:shift,:notes,:machine_code)""", d)

    def update_downtime(self, dtid, d):
        d["downtime_id"] = dtid
        with self.cx() as c:
            c.execute("""UPDATE downtime_events SET
                end_time=:end_time,duration=:duration,root_cause=:root_cause,
                corrective_action=:corrective_action,downtime_type=:downtime_type,
                notes=:notes WHERE downtime_id=:downtime_id""", d)

    def today_stats(self, date_str):
        with self.cx() as c:
            rows = c.execute("""SELECT duration FROM downtime_events
                WHERE DATE(start_time)=? AND end_time IS NOT NULL""",(date_str,)).fetchall()
        total=0
        for r in rows:
            if r[0]:
                p=r[0].split(":")
                try: total+=int(p[0])*60+int(p[1])
                except: pass
        h,m=divmod(total,60)
        return f"{h:02d}:{m:02d}", len(rows), total

    def hourly(self, date_str):
        with self.cx() as c:
            rows=c.execute("""SELECT strftime('%H',start_time),
                SUM(CAST(substr(duration,1,instr(duration,':')-1)AS INT)*60+
                    CAST(substr(duration,instr(duration,':')+1,2)AS INT))
                FROM downtime_events
                WHERE DATE(start_time)=? AND end_time IS NOT NULL AND duration IS NOT NULL
                GROUP BY 1""",(date_str,)).fetchall()
        return {int(r[0]):int(r[1] or 0) for r in rows if r[0]}

    def get_page(
        self,
        start_date,
        end_date,
        start_time,
        end_time,
        page,
        per=5
    ):

        start_dt = f"{start_date} {start_time}:00"
        end_dt   = f"{end_date} {end_time}:59"

        q = """
            SELECT *
            FROM downtime_events
            WHERE datetime(start_time)
            BETWEEN datetime(?)
            AND datetime(?)
            ORDER BY start_time DESC
        """

        with self.cx() as c:

            cur = c.execute(
                q,
                (start_dt, end_dt)
            )

            cols = [d[0] for d in cur.description]

            all_rows = [
                dict(zip(cols, r))
                for r in cur.fetchall()
            ]

        total = len(all_rows)

        s = (page - 1) * per

        return (
            all_rows[s:s+per],
            total
        )

    def export_csv(
        self,
        start_date,
        end_date,
        start_time,
        end_time,
        path
    ):

        start_dt = f"{start_date} {start_time}:00"
        end_dt   = f"{end_date} {end_time}:59"

        q = """
            SELECT *
            FROM downtime_events
            WHERE datetime(start_time)
            BETWEEN datetime(?)
            AND datetime(?)
            ORDER BY start_time DESC
        """

        with self.cx() as c:

            cur = c.execute(
                q,
                (start_dt, end_dt)
            )

            cols = [d[0] for d in cur.description]

            rows = [
                dict(zip(cols, r))
                for r in cur.fetchall()
            ]

        if not rows:
            return 0

        with open(
            path,
            "w",
            newline="",
            encoding="utf-8"
        ) as f:

            writer = csv.DictWriter(
                f,
                fieldnames=cols
            )

            writer.writeheader()
            writer.writerows(rows)

        return len(rows)

# ──────────────────────────────────────────────────────────
# MAIN PAGE
# ──────────────────────────────────────────────────────────
class MaintenancePage(ctk.CTkFrame):
    def __init__(self, master, user=None, main_form=None, **kw):
        self.main_form = main_form
        super().__init__(master, fg_color=DARK_BG, corner_radius=0, **kw)
        self.db   = MaintenanceDB()
        self.cfg  = self.db.get_config()
        self.user = user
        self.machine_state  = "IDLE"
        self.dt_start       = None
        self.current_dt_id  = None
        self._dur_job = self._clk_job = None
        self.cur_page = 1
        self.per_page = 5
        self.total_pages = 1
        self.filter_start_date = datetime.now().strftime("%Y-%m-%d")
        self.filter_end_date   = datetime.now().strftime("%Y-%m-%d")

        self.filter_from_time  = "00:00"
        self.filter_to_time    = "23:59"
        self._build()
        if self.main_form:

            if self.main_form.machine_status == "MACHINE DOWN":

                self.ms_icon.configure(
                    text_color=RED
                )

                self.ms_text.configure(
                    text="MACHINE DOWN",
                    text_color=RED
                )

            elif self.main_form.machine_status == "WAITING MATERIAL":

                self.ms_icon.configure(
                    text_color=YELLOW
                )

                self.ms_text.configure(
                    text="WAITING MATERIAL",
                    text_color=YELLOW
                )
        self._refresh_all()
        self._tick_clock()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)

        r1 = ctk.CTkFrame(self, fg_color="transparent")
        r1.grid(row=0, column=0, sticky="ew", padx=10, pady=(8,4))
        self._build_r1(r1)

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0,8))
        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=0)
        body.grid_rowconfigure(0, weight=1)

        self.left_body = ctk.CTkFrame(body, fg_color="transparent")
        self.left_body.grid(row=0, column=0, sticky="nsew", padx=(0,6))
        self.left_body.grid_rowconfigure(0, weight=0)
        self.left_body.grid_rowconfigure(1, weight=1)
        self.left_body.grid_columnconfigure(0, weight=1)

        self.right_body = ctk.CTkFrame(body, fg_color=CARD_BG, corner_radius=8,
                                       border_width=1, border_color=BORDER, width=360)
        self.right_body.grid(row=0, column=1, sticky="ns")
        self.right_body.grid_propagate(False)
        self.right_body.grid_rowconfigure(0, weight=1)
        self.right_body.grid_columnconfigure(0, weight=1)

        self._build_r2_left()
        self._build_r3_left()
        self._build_r2_right()

    def _card(self, parent, **kw):
        defaults = dict(fg_color=CARD_BG, corner_radius=8,
                        border_width=1, border_color=BORDER)
        defaults.update(kw)
        return ctk.CTkFrame(parent, **defaults)

    def _build_r1(self, parent):
        parent.grid_columnconfigure(0, weight=1, minsize=180)
        parent.grid_columnconfigure(1, weight=1, minsize=100)
        parent.grid_columnconfigure(2, weight=1, minsize=100)
        parent.grid_columnconfigure(3, weight=1, minsize=100)
        parent.grid_columnconfigure(4, weight=1, minsize=100)
        parent.grid_columnconfigure(5, weight=1, minsize=160)
        parent.grid_rowconfigure(0, weight=1)

        ms = self._card(parent, border_color="#7F1D1D")
        ms.grid(row=0, column=0, sticky="nsew", padx=(0,4), pady=2)
        self._fill_status_card(ms)

        kpis = [
            ("TODAY DOWNTIME", "⏱", "00:00", "hh:mm",  ORANGE, "kpi_dt"),
            ("OCCURRENCES",    "⚡", "0",     "Times",   YELLOW, "kpi_occ"),
            ("MTTR",           "🛠", "0",     "min",     BLUE,   "kpi_mttr"),
            ("MTBF",           "📊", "04:20", "hh:mm",   GREEN,  "kpi_mtbf"),
        ]
        for i, (title, icon, val, sub, clr, attr) in enumerate(kpis):
            cf = self._card(parent)
            cf.grid(row=0, column=i+1, sticky="nsew", padx=(0,4), pady=2)
            self._fill_kpi_card(cf, title, icon, val, sub, clr, attr)

        ai = self._card(parent)
        ai.grid(row=0, column=5, sticky="nsew", padx=(4,0), pady=2)
        self._fill_active_info(ai)

    def _fill_status_card(self, card):
        ctk.CTkLabel(card, text="MACHINE STATUS", font=("Segoe UI",8,"bold"),
                     text_color=TEXT2).pack(anchor="center", pady=(8,2))

        status_row = ctk.CTkFrame(card, fg_color="transparent")
        status_row.pack(anchor="center", pady=(4,0))
        self.ms_icon = ctk.CTkLabel(status_row, text="●", font=("Segoe UI",18),
                                    text_color=GREEN)
        self.ms_icon.pack(side="left", padx=(0,6))
        self.ms_text = ctk.CTkLabel(status_row, text="RUNNING / IDLE",
                                    font=("Segoe UI",13,"bold"), text_color=GREEN)
        self.ms_text.pack(side="left")

        self.since_lbl = ctk.CTkLabel(card, text="Since        -",
                                      font=("Segoe UI",9), text_color=TEXT2)
        self.since_lbl.pack(anchor="center", pady=(6,0))
        self.dur_lbl = ctk.CTkLabel(card, text="Duration   00:00:00",
                                    font=("Segoe UI",11,"bold"), text_color=GREEN)
        self.dur_lbl.pack(anchor="center", pady=(2,10))

    def _fill_kpi_card(self, card, title, icon, val, sub, clr, attr):
        ctk.CTkLabel(card, text=title, font=("Segoe UI",8,"bold"),
                     text_color=TEXT2).pack(anchor="center", pady=(10,2))
        ctk.CTkLabel(card, text=icon, font=("Segoe UI",24),
                     text_color=clr).pack(anchor="center", pady=(0,2))
        lbl = ctk.CTkLabel(card, text=val, font=("Segoe UI",20,"bold"),
                           text_color=TEXT)
        lbl.pack(anchor="center")
        ctk.CTkLabel(card, text=sub, font=("Segoe UI",8),
                     text_color=TEXT2).pack(anchor="center", pady=(0,10))
        setattr(self, attr, lbl)

    def _fill_active_info(self, card):
        ctk.CTkLabel(card, text="ACTIVE DOWNTIME INFO",
                     font=("Segoe UI",8,"bold"), text_color=TEXT2).pack(anchor="center", pady=(8,4))

        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(fill="x", padx=10, pady=(2,8))
        info_frame.grid_columnconfigure(0, weight=1)
        info_frame.grid_columnconfigure(1, weight=0)
        info_frame.grid_columnconfigure(2, weight=2)

        self.adi = {}
        labels = [("Downtime ID","-"), ("Start Time","-"),
                  ("Technician", self.cfg.get("technician","-")),
                  ("Shift", self.cfg.get("shift","-"))]

        for i, (key, val) in enumerate(labels):
            ctk.CTkLabel(info_frame, text=key, font=("Segoe UI",8),
                         text_color=TEXT2, anchor="w").grid(row=i, column=0, sticky="w", pady=1)
            ctk.CTkLabel(info_frame, text=":", font=("Segoe UI",8),
                         text_color=TEXT2).grid(row=i, column=1, padx=(2,4), pady=1)
            v = ctk.CTkLabel(info_frame, text=val, font=("Segoe UI",8,"bold"),
                             text_color=TEXT, anchor="w")
            v.grid(row=i, column=2, sticky="w", pady=1)
            self.adi[key] = v

    def _build_r2_left(self):
        chart_frame = ctk.CTkFrame(self.left_body, fg_color=CARD_BG, corner_radius=8,
                                   border_width=1, border_color=BORDER, height=260)
        chart_frame.grid(row=0, column=0, sticky="ew", pady=(0,6))
        chart_frame.grid_propagate(False)

        hdr = ctk.CTkFrame(chart_frame, fg_color="transparent")
        hdr.pack(fill="x", padx=12, pady=(10,0))
        ctk.CTkLabel(hdr, text="HOURLY DOWNTIME (Today)", font=("Segoe UI",11,"bold"),
                     text_color=TEXT).pack(side="left")
        self.total_lbl = ctk.CTkLabel(hdr, text="Total : 0h 0m",
                                      font=("Segoe UI",10), text_color=GREEN)
        self.total_lbl.pack(side="right")

        self.chart_cv = tk.Canvas(chart_frame, bg=CARD_BG, highlightthickness=0)
        self.chart_cv.pack(fill="both", expand=True, padx=8, pady=(4,8))
        self.chart_cv.bind("<Configure>", lambda e: self._draw_chart())

    def _build_r3_left(self):
        table_card = ctk.CTkFrame(self.left_body, fg_color=CARD_BG, corner_radius=8,
                                  border_width=1, border_color=BORDER)
        table_card.grid(row=1, column=0, sticky="nsew")
        table_card.grid_rowconfigure(0, weight=0)
        table_card.grid_rowconfigure(1, weight=1)
        table_card.grid_rowconfigure(2, weight=0)
        table_card.grid_columnconfigure(0, weight=1)

        header_row = ctk.CTkFrame(table_card, fg_color="transparent")
        header_row.grid(row=0, column=0, sticky="ew", padx=10, pady=(10,6))
        title_frame = ctk.CTkFrame(header_row, fg_color="transparent")
        title_frame.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(title_frame, text="DOWNTIME HISTORY",
                     font=("Segoe UI",14,"bold"), text_color=TEXT).pack(anchor="w")

        fb = ctk.CTkFrame(header_row, fg_color="transparent")
        fb.pack(side="right")

        def lbl(t): ctk.CTkLabel(fb, text=t, font=("Segoe UI",10), text_color=TEXT2).pack(side="left")
        def entry_w(w=90):
            return ctk.CTkEntry(fb, width=w, height=30, fg_color=CARD_BG,
                                border_color=BORDER, border_width=1,
                                text_color=TEXT, font=("Segoe UI",11))
        def combo_w(vals, w=110):
            return ctk.CTkComboBox(fb, values=vals, width=w, height=30,
                                   fg_color=CARD_BG, border_color=BORDER,
                                   button_color=BORDER, text_color=TEXT,
                                   font=("Segoe UI",11))

        lbl("Date Start")

        self.date_start = DateEntry(
            fb,
            width=11,
            background="#1E3A5F",
            foreground="white",
            borderwidth=1,
            date_pattern="dd/mm/yyyy",
            font=("Segoe UI",10)
        )
        self.date_start.pack(side="left", padx=(4,12))

        lbl("Date End")

        self.date_end = DateEntry(
            fb,
            width=11,
            background="#1E3A5F",
            foreground="white",
            borderwidth=1,
            date_pattern="dd/mm/yyyy",
            font=("Segoe UI",10)
        )
        self.date_end.pack(side="left", padx=(4,12))

        time_list = [
            f"{h:02d}:{m:02d}"
            for h in range(24)
            for m in (0,30)
        ]
        self.from_cb = combo_w(
            time_list,
            90
        )

        self.to_cb = combo_w(
            time_list,
            90
        )

        ctk.CTkButton(fb, text="🔄  Refresh", height=30, width=100,
                      fg_color=GREEN, hover_color=GREEN_HOV,
                      text_color=DARK_BG, font=("Segoe UI",11,"bold"),
                      corner_radius=6, command=self._refresh_table
                      ).pack(side="left", padx=(0,8))
        ctk.CTkButton(fb, text="⬇  Export CSV", height=30, width=120,
                      fg_color=BLUE, hover_color="#2563EB",
                      text_color="#FFFFFF", font=("Segoe UI",11,"bold"),
                      corner_radius=6, command=self._export_csv
                      ).pack(side="left")

        style = ttk.Style()
        style.theme_use("default")
        style.configure("DT.Treeview", background=CARD_BG, foreground=TEXT,
                        rowheight=26, fieldbackground=CARD_BG, borderwidth=0,
                        font=("Segoe UI",10))
        style.configure("DT.Treeview.Heading", background=PANEL_BG, foreground=TEXT2,
                        relief="flat", font=("Segoe UI",10,"bold"))
        style.map("DT.Treeview", background=[("selected", BORDER)])

        cols = ("No","Start Time","End Time","Duration","Downtime Type",
                "Root Cause","Corrective Action","Technician","Shift")
        tree_frame = ctk.CTkFrame(table_card, fg_color="transparent")
        tree_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0,6))
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(tree_frame, columns=cols, show="headings",
                                 style="DT.Treeview")
        self.tree.grid(row=0, column=0, sticky="nsew")

        for col in cols:
            self.tree.heading(col, text=col)
            anchor = "center" if col in ("No","Duration","Shift") else "w"
            self.tree.column(col, anchor=anchor, stretch=True, minwidth=40)

        self.tree.bind("<Configure>", lambda e: self._adjust_tree_columns())

        pg = ctk.CTkFrame(table_card, fg_color="transparent")
        pg.grid(row=2, column=0, sticky="ew", padx=10, pady=(0,8))
        def pg_btn(txt, cmd):
            return ctk.CTkButton(pg, text=txt, width=28, height=26,
                                 fg_color=CARD_BG, hover_color=BORDER, text_color=TEXT2,
                                 corner_radius=4, font=("Segoe UI",11), command=cmd)
        pg_btn("<<", self._pg_first).pack(side="left", padx=1)
        pg_btn("<",  self._pg_prev).pack(side="left", padx=1)
        self.pg_inner = ctk.CTkFrame(pg, fg_color="transparent")
        self.pg_inner.pack(side="left", padx=2)
        pg_btn(">",  self._pg_next).pack(side="left", padx=1)
        pg_btn(">>", self._pg_last).pack(side="left", padx=1)
        self.rec_lbl = ctk.CTkLabel(pg, text="Total Records : 0",
                                    font=("Segoe UI",10), text_color=TEXT2)
        self.rec_lbl.pack(side="right")

    def _adjust_tree_columns(self):
        tree_width = self.tree.winfo_width()
        if tree_width < 20:
            return
        cols = self.tree["columns"]
        n = len(cols)
        col_width = tree_width // n
        for col in cols:
            self.tree.column(col, width=col_width, stretch=True)

    def _build_r2_right(self):
        right = ctk.CTkFrame(self.right_body, fg_color=CARD_BG, corner_radius=8,
                             border_width=1, border_color=BORDER)
        right.pack(fill="both", expand=True, padx=4, pady=4)

        ctk.CTkLabel(right, text="ROOT CAUSE & CORRECTIVE ACTION",
                     font=("Segoe UI",10,"bold"), text_color=TEXT).pack(anchor="w", padx=12, pady=(10,4))

        def txt_block(label, color, attr_txt, attr_cnt, h=60):
            ctk.CTkLabel(right, text=label, font=("Segoe UI",9),
                         text_color=color, anchor="w").pack(fill="x", padx=12, pady=(4,0))
            tb = ctk.CTkTextbox(right, height=h, corner_radius=6,
                                fg_color=DARK_BG, border_color=BORDER, border_width=1,
                                text_color=TEXT, font=("Segoe UI",11))
            tb.pack(fill="x", padx=12, pady=(2,0))
            cnt = ctk.CTkLabel(right, text="0 / 500", font=("Segoe UI",8),
                               text_color=TEXT2, anchor="e")
            cnt.pack(fill="x", padx=14, pady=(0,2))
            tb.bind("<KeyRelease>", lambda e,t=tb,c=cnt: c.configure(
                text=f"{len(t.get('1.0','end').strip())} / 500"))
            setattr(self, attr_txt, tb)
            setattr(self, attr_cnt, cnt)

        txt_block("Root Cause *",        RED,  "rc_txt",  "rc_cnt", h=60)
        txt_block("Corrective Action *", RED,  "ca_txt",  "ca_cnt", h=60)

        ctk.CTkLabel(right, text="Downtime Type *", font=("Segoe UI",9),
                     text_color=RED, anchor="w").pack(fill="x", padx=12, pady=(4,0))
        self.dt_var = ctk.StringVar(value="Select downtime type...")
        ctk.CTkComboBox(right, variable=self.dt_var,
                        values=["MECHANICAL","ELECTRICAL","QUALITY","SOFTWARE","OTHERS"],
                        fg_color=DARK_BG, border_color=BORDER, button_color=BORDER,
                        text_color=TEXT, font=("Segoe UI",11), corner_radius=6
                        ).pack(fill="x", padx=12, pady=(2,4))

        txt_block("Notes", TEXT2, "notes_txt", "notes_cnt", h=50)

        ctk.CTkButton(
            right,
            text="✔ SAVE RCA & RETURN TO IDLE",
            height=48,
            fg_color="#22C55E",
            hover_color="#16A34A",
            text_color="#0B1120",
            font=("Segoe UI",12,"bold"),
            corner_radius=8,
            command=self._return_idle
        ).pack(
            fill="x",
            padx=12,
            pady=(10,8)
        )

        def _complete_downtime(self):

            rc = self.rc_txt.get("1.0", "end").strip()
            ca = self.ca_txt.get("1.0", "end").strip()
            dt = self.dt_var.get()

            if not rc or not ca or dt.startswith("Select"):

                messagebox.showwarning(
                    "Validation",
                    "Root Cause, Corrective Action & Downtime Type wajib diisi!",
                    parent=self
                )
                return

            self._return_idle()

        ctk.CTkLabel(right, text="⚠  Root Cause and Corrective Action must be filled before returning to IDLE.",
                     font=("Segoe UI",8), text_color=YELLOW,
                     wraplength=290, justify="left").pack(padx=12, pady=(4,6))

    # ══════════════════════════════════════════════════════
    # CLOCK, DOWNTIME LOGIC, CHART, TABLE
    # ══════════════════════════════════════════════════════
    def _tick_clock(self):
        if not self.winfo_exists(): return
        self._clk_job = self.after(1000, self._tick_clock)

    def start_downtime(self):
        if self.machine_state == "DOWN": return
        self.machine_state = "DOWN"
        self.dt_start = datetime.now()
        dtid = f"DT-{self.dt_start.strftime('%Y%m%d%H%M%S')}"
        self.current_dt_id = dtid
        self.db.insert_downtime({
            "downtime_id": dtid,
            "start_time":  self.dt_start.strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": None, "duration": None, "downtime_type": None,
            "root_cause": None, "corrective_action": None,
            "technician": self.cfg.get("technician",""),
            "shift": self.cfg.get("shift",""),
            "notes": None,
            "machine_code": self.cfg.get("machine_code",""),
        })
        self._update_ui_down()
        self._tick_dur()

    def _tick_dur(self):
        if self.machine_state != "DOWN" or not self.dt_start: return
        d = int((datetime.now()-self.dt_start).total_seconds())
        h,r = divmod(d,3600); m,s = divmod(r,60)
        self.dur_lbl.configure(text=f"Duration   {h:02d}:{m:02d}:{s:02d} (hh:mm:ss)")
        self._dur_job = self.after(1000, self._tick_dur)

    def _update_ui_down(self):
        self.ms_icon.configure(text="●", text_color=RED)
        self.ms_text.configure(text="MACHINE DOWN", text_color=RED)
        self.since_lbl.configure(text=f"Since        {self.dt_start.strftime('%I:%M:%S %p')}")
        self.adi["Downtime ID"].configure(text=self.current_dt_id)
        self.adi["Start Time"].configure(text=self.dt_start.strftime('%I:%M:%S %p'))
        self.adi["Technician"].configure(text=self.cfg.get("technician","-"))
        self.adi["Shift"].configure(text=self.cfg.get("shift","-"))


    def _return_idle(self):
        rc = self.rc_txt.get("1.0","end").strip()
        ca = self.ca_txt.get("1.0","end").strip()
        dt = self.dt_var.get()
        if not rc or not ca or dt.startswith("Select"):
            messagebox.showwarning("Validation",
                "Root Cause, Corrective Action & Downtime Type wajib diisi!",parent=self)
            return
        if not self.dt_start:
            messagebox.showinfo("Info","Tidak ada downtime aktif.",parent=self); return
        end = datetime.now()
        d   = int((end-self.dt_start).total_seconds())
        h,r = divmod(d,3600); m,_ = divmod(r,60)
        self.db.update_downtime(self.current_dt_id,{
            "end_time":  end.strftime("%Y-%m-%d %H:%M:%S"),
            "duration":  f"{h:02d}:{m:02d}",
            "root_cause":        rc,
            "corrective_action": ca,
            "downtime_type":     dt,
            "notes":             self.notes_txt.get("1.0","end").strip(),
        })
        self.machine_state = "IDLE"; self.dt_start = None; self.current_dt_id = None
        if self._dur_job: self.after_cancel(self._dur_job)
        self.ms_icon.configure(text="●", text_color=GREEN)
        self.ms_text.configure(text="RUNNING / IDLE", text_color=GREEN)
        self.dur_lbl.configure(text="Duration   00:00:00 (hh:mm:ss)", text_color=GREEN)
        self.since_lbl.configure(text="Since        -")
        for v in self.adi.values(): v.configure(text="-")
        for tb in [self.rc_txt, self.ca_txt, self.notes_txt]: tb.delete("1.0","end")
        self.dt_var.set("Select downtime type...")
        self._refresh_all()

    def _draw_chart(self):
        cv = self.chart_cv
        cv.delete("all")
        W = cv.winfo_width(); H = cv.winfo_height()
        if W < 20 or H < 20:
            self.after(100, self._draw_chart); return
        today = datetime.now().strftime("%Y-%m-%d")

        data = self.db.hourly(
            today
        )
        max_v = max(data.values(), default=0) or 1
        PL,PR,PT,PB = 42,8,18,28
        CW = W-PL-PR; CH = H-PT-PB
        bw = CW/24*0.55; gp = CW/24
        for pct in [0.25,0.5,0.75,1.0]:
            yy = PT+CH-CH*pct
            cv.create_line(PL,yy,W-PR,yy,fill="#1E3A5F",dash=(3,3))
            cv.create_text(PL-4,yy,text=str(int(max_v*pct)),
                           font=("Segoe UI",7),fill=TEXT2,anchor="e")
        cv.create_text(10,PT+CH//2,text="Minutes",
                       font=("Segoe UI",7),fill=TEXT2,angle=90)
        for hr in range(24):
            m = data.get(hr,0)
            bh = CH*(m/max_v) if m else 0
            x1 = PL+hr*gp+(gp-bw)/2; x2=x1+bw
            y1 = PT+CH-bh; y2=PT+CH
            if m:
                cv.create_rectangle(x1,y1,x2,y2,fill=BLUE,outline="")
                label = f"{m}m" if m<60 else f"{m//60}h{m%60}m"
                cv.create_text((x1+x2)/2,y1-3,text=label,
                               font=("Segoe UI",7,"bold"),fill=TEXT2,anchor="s")
            cv.create_text((x1+x2)/2,H-PB+8,
                           text=f"{hr:02d}",font=("Segoe UI",7),fill=TEXT2)
        cv.create_text(PL,H-4,text="Hour",font=("Segoe UI",7),fill=TEXT2,anchor="w")

    def _refresh_table(self):

        self.filter_start_date = (
            self.date_start
            .get_date()
            .strftime("%Y-%m-%d")
        )

        self.filter_end_date = (
            self.date_end
            .get_date()
            .strftime("%Y-%m-%d")
        )

        self.filter_from_time = (
            self.from_cb.get()
        )

        self.filter_to_time = (
            self.to_cb.get()
        )

        self.cur_page = 1

        self._load_table()

    def _load_table(self):
        for r in self.tree.get_children(): self.tree.delete(r)
        TC={"MECHANICAL":RED,"ELECTRICAL":BLUE,"QUALITY":PURPLE,
            "SOFTWARE":ORANGE,"OTHERS":TEXT2}
        rows,total = self.db.get_page(
            self.filter_start_date,
            self.filter_end_date,
            self.filter_from_time,
            self.filter_to_time,
            self.cur_page,
            self.per_page
        )
        self.total_pages=max(1,(total+self.per_page-1)//self.per_page)
        for i,r in enumerate(rows,start=(self.cur_page-1)*self.per_page+1):
            dt=(r.get("downtime_type") or "").upper()
            st=r.get("start_time",""); et=r.get("end_time","")
            self.tree.insert("","end",values=(
                i,
                st[11:16] if st else "-",
                et[11:16] if et else "-",
                r.get("duration","-") or "-",
                dt or "-",
                r.get("root_cause","") or "Not Filled",
                r.get("corrective_action","") or "Not Filled",
                r.get("technician","-") or "-",
                (r.get("shift","") or "")[-1] if r.get("shift") else "-",
            ), tags=(dt,))
        for dt,clr in TC.items():
            self.tree.tag_configure(dt,foreground=clr)
        self.rec_lbl.configure(text=f"Total Records : {total}")
        self._build_pg()
        self.after(50, self._adjust_tree_columns)

    def _build_pg(self):
        for w in self.pg_inner.winfo_children(): w.destroy()
        for p in range(1,self.total_pages+1):
            cur=(p==self.cur_page)
            ctk.CTkButton(self.pg_inner,text=str(p),width=28,height=26,
                fg_color=GREEN if cur else CARD_BG,
                hover_color=GREEN_HOV if cur else BORDER,
                text_color=DARK_BG if cur else TEXT,
                corner_radius=4,font=("Segoe UI",10),
                command=lambda pg=p:self._goto(pg)).pack(side="left",padx=1)

    def _goto(self,p): self.cur_page=p; self._load_table()
    def _pg_first(self): self._goto(1)
    def _pg_last(self):  self._goto(self.total_pages)
    def _pg_prev(self):
        if self.cur_page>1: self._goto(self.cur_page-1)
    def _pg_next(self):
        if self.cur_page<self.total_pages: self._goto(self.cur_page+1)

    def _refresh_kpi(self):

        today = datetime.now().strftime("%Y-%m-%d")

        ts,occ,total_min = self.db.today_stats(
            today
        )

        self.kpi_dt.configure(
            text=ts
        )

        self.kpi_occ.configure(
            text=str(occ)
        )

        mttr = total_min // occ if occ else 0

        self.kpi_mttr.configure(
            text=str(mttr)
        )

        h,m = (
            int(x)
            for x in ts.split(":")
        )

        self.total_lbl.configure(
            text=f"Total : {h}h {m}m"
        )

    def _export_csv(self):
        path=f"downtime_{self.fdate}.csv"
        n = self.db.export_csv(
            self.filter_start_date,
            self.filter_end_date,
            self.filter_from_time,
            self.filter_to_time,
            path
        )
        if n: messagebox.showinfo("Export",f"{n} record → {os.path.abspath(path)}",parent=self)
        else: messagebox.showwarning("Export","Tidak ada data.",parent=self)

    def _refresh_all(self):
        self._refresh_kpi()
        self._load_table()
        self.after(200, self._draw_chart)

    def destroy(self):
        for j in [self._dur_job,self._clk_job]:
            if j:
                try: self.after_cancel(j)
                except: pass
        super().destroy()

