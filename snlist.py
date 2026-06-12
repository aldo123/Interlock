import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os
import json
import threading
from datetime import date
from tkcalendar import DateEntry

# ── Palette ───────────────────────────────────────────────
BG       = "#0F172A"
CARD_BG  = "#1E293B"
TEXT     = "#E2E8F0"
TEXT2    = "#94A3B8"
SUCCESS  = "#22C55E"
BORDER   = "#334155"
BLUE     = "#3B82F6"
HDR_BG   = "#111827"
INPUT_BG = "#172132"

# ── CP Column Definitions ─────────────────────────────────
CP_COLUMN_MAP = {
    "1": [
        ("date_time",       "Date Time",                          150),
        ("chassis_sn",      "Chassis SN (WU# Code 1)",           200),
        ("batch_number",    "Batch Number (Macro SMP Code 4)",   230),
        ("sku_info",        "SKU Information",                    160),
        ("drawing_vision",  "Drawing Vision",                     130),
        ("psn_vision",      "Psn Vision",                         110),
        ("app_version",     "App Version",                        120),
    ],
    "2": [
        ("date_time",    "Date Time",                  150),
        ("chassis_sn",   "Chassis SN (WU# Code 1)",   200),
        ("main_pcba",    "Main PCBA (SU# Code F)",     220),
        ("mac_address",  "MAC Address (SU# Code F)",   170),
        ("app_version",  "App Version",                120),
    ],
    # Tambah CP baru di sini:
    # "3": [...],
}

CP_TABLE_MAP = {
    "1": "snlist_cp1",
    "2": "snlist_cp2",
}

CP_DDL_MAP = {
    "1": """
        CREATE TABLE IF NOT EXISTS snlist_cp2 (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            date_time      TEXT,
            chassis_sn     TEXT,
            batch_number   TEXT,
            sku_info       TEXT,
            drawing_vision TEXT,
            psn_vision     TEXT,
            app_version    TEXT
        )
    """,
    "2": """
        CREATE TABLE IF NOT EXISTS snlist_cp1 (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            date_time   TEXT,
            chassis_sn  TEXT,
            main_pcba   TEXT,
            mac_address TEXT,
            app_version TEXT
        )
    """,
}


def _load_process_from_json():
    """Baca interlock.json — sinkron tapi ringan (hanya baca file kecil)."""
    try:
        path = os.path.join(os.path.dirname(__file__), "interlock.json")
        if not os.path.exists(path):
            return ["1"]
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        cp = data.get("Control Point", {})
        process = cp.get("Process", "1")
        if isinstance(process, list):
            return [str(p) for p in process]
        return [str(process)]
    except Exception as e:
        print("SNList: interlock.json load error:", e)
        return ["1"]


class SNListPage:
    def __init__(self, parent, app=None):
        self.parent = parent
        self.app    = app

        # ── 1. Baca proses dari JSON (cepat, hanya baca file) ──
        procs = _load_process_from_json()
        self.active_processes = [p for p in procs if p in CP_COLUMN_MAP] or ["1"]
        self.current_process  = self.active_processes[0]

        self._data: list[dict] = []
        self._sort_col = None
        self._sort_rev = False

        # ── 2. Bangun UI langsung (tidak ada IO di sini) ───────
        self._build_ui()

        # ── 3. DB init + load data di background thread ────────
        threading.Thread(target=self._bg_init_and_load, daemon=True).start()

    # =========================================================
    # BACKGROUND: init DB lalu load data, hasil dikirim ke mainthread
    # =========================================================
    def _bg_init_and_load(self):
        try:
            conn = self._get_conn()
            for p in self.active_processes:
                if p in CP_DDL_MAP:
                    conn.execute(CP_DDL_MAP[p])
            conn.commit()
            conn.close()
        except Exception as e:
            print("SNList DB init error:", e)

        # Ambil data lalu update UI di main thread
        rows = self._fetch_rows()
        self.parent.after(0, lambda: self._apply_rows(rows))

    def _fetch_rows(self, where="", params=()):
        """Query DB — dipanggil dari thread mana saja, return list of dict."""
        try:
            table   = CP_TABLE_MAP.get(self.current_process,
                                       f"snlist_cp{self.current_process}")
            col_defs = CP_COLUMN_MAP[self.current_process]
            db_cols  = [c[0] for c in col_defs]
            sel_cols = ", ".join(["id"] + db_cols)

            conn   = self._get_conn()
            cur    = conn.cursor()
            q      = f"SELECT {sel_cols} FROM {table}"
            if where:
                q += f" WHERE {where}"
            q += " ORDER BY date_time DESC"
            cur.execute(q, params)
            raw = cur.fetchall()
            conn.close()

            keys = ["id"] + db_cols
            return [dict(zip(keys, r)) for r in raw]
        except Exception as e:
            print("SNList fetch error:", e)
            return []

    def _apply_rows(self, rows):
        """Terima hasil dari thread, update UI di main thread."""
        self._data = rows
        self._refresh_table()

    # =========================================================
    # DB helper
    # =========================================================
    def _get_conn(self):
        db_path = os.path.join(os.path.dirname(__file__), "snlist.db")
        return sqlite3.connect(db_path)

    # =========================================================
    # PUBLIC load_data — dipanggil setelah operasi tulis
    # =========================================================
    def load_data(self, where="", params=()):
        """Non-blocking: fetch di thread, apply di main thread."""
        threading.Thread(
            target=lambda: self.parent.after(
                0, lambda: self._apply_rows(self._fetch_rows(where, params))
            ),
            daemon=True
        ).start()

    # =========================================================
    # BUILD UI  (tidak ada IO sama sekali)
    # =========================================================
    def _build_ui(self):
        self._root = ctk.CTkFrame(self.parent, fg_color=BG)
        self._root.pack(fill="both", expand=True)

        # ── Top bar ──────────────────────────────────────────
        top = ctk.CTkFrame(self._root, fg_color=HDR_BG, corner_radius=0)
        top.pack(fill="x")
        

        

        # ── Search by Date ────────────────────────────────────
        df = ctk.CTkFrame(top, fg_color="transparent")
        df.pack(side="left", padx=(16, 8), pady=8)

        ctk.CTkLabel(df, text="SEARCH BY PRINTED DATE",
                     font=("Segoe UI", 9, "bold"),
                     text_color=TEXT2).grid(row=0, column=0, columnspan=6,
                                            sticky="w", pady=(0, 3))

        # row 1: FROM <date> TO <date> SEARCH
        ctk.CTkLabel(df, text="FROM", font=("Segoe UI", 10),
                     text_color=TEXT2).grid(row=1, column=0, padx=(0, 4), sticky="w")
        self._date_from = DateEntry(df, width=11,
                                    background="#1E3A5F", foreground="white",
                                    borderwidth=1, date_pattern="yyyy-mm-dd",
                                    font=("Segoe UI", 10))
        self._date_from.grid(row=1, column=1, padx=(0, 8))

        ctk.CTkLabel(df, text="TO", font=("Segoe UI", 10),
                     text_color=TEXT2).grid(row=1, column=2, padx=(0, 4), sticky="w")
        self._date_to = DateEntry(df, width=11,
                                  background="#1E3A5F", foreground="white",
                                  borderwidth=1, date_pattern="yyyy-mm-dd",
                                  font=("Segoe UI", 10))
        self._date_to.grid(row=1, column=3, padx=(0, 8))

        ctk.CTkButton(df, text="SEARCH", width=80, height=28,
                      fg_color=BLUE, hover_color="#2563EB",
                      font=("Segoe UI", 10, "bold"), corner_radius=5,
                      command=self._search_by_date
                      ).grid(row=1, column=4, padx=(0, 4))

        # ── Search by Barcode ─────────────────────────────────
        bf = ctk.CTkFrame(top, fg_color="transparent")
        bf.pack(side="left", padx=(16, 8), pady=8)

        ctk.CTkLabel(bf, text="SEARCH BY BARCODE",
                     font=("Segoe UI", 9, "bold"),
                     text_color=TEXT2).pack(anchor="w", pady=(0, 3))

        # input + SEARCH button side by side
        bc_row = ctk.CTkFrame(bf, fg_color="transparent")
        bc_row.pack(anchor="w")

        bc_wrap = ctk.CTkFrame(bc_row, fg_color=INPUT_BG,
                               border_width=1, border_color=BORDER,
                               corner_radius=6)
        bc_wrap.pack(side="left")
        self._barcode_var = tk.StringVar()
        ctk.CTkEntry(bc_wrap, textvariable=self._barcode_var,
                     fg_color="transparent", border_width=0,
                     text_color=TEXT, width=220, height=28,
                     font=("Segoe UI", 11)).pack(padx=6, pady=1)

        ctk.CTkButton(bc_row, text="SEARCH", width=80, height=28,
                      fg_color=BLUE, hover_color="#2563EB",
                      font=("Segoe UI", 10, "bold"), corner_radius=5,
                      command=self._search_by_barcode
                      ).pack(side="left", padx=(6, 0))

        # Count + CSV
        self._count_lbl = ctk.CTkLabel(top, text="0 records",
                                       font=("Segoe UI", 10), text_color=TEXT2)
        self._count_lbl.pack(
            side="right",
            padx=8,
            pady=(32, 0)
        )

        ctk.CTkButton(
            top,
            text="SAVE TO CSV FILE",
            width=140,
            height=34,
            fg_color=SUCCESS,
            hover_color="#16A34A",
            text_color="#052E16",
            font=("Segoe UI", 11, "bold"),
            corner_radius=6,
            command=self._save_csv
        ).pack(
            side="right",
            padx=12,
            pady=(32, 0)
        )

        # ── Table area ───────────────────────────────────────
        self._tbl_outer = ctk.CTkFrame(self._root, fg_color=BG)
        self._tbl_outer.pack(fill="both", expand=True, padx=8, pady=(4, 8))
        self._build_table()

    # =========================================================
    # TABLE
    # =========================================================
    def _build_table(self):
        for w in self._tbl_outer.winfo_children():
            w.destroy()

        col_defs = CP_COLUMN_MAP[self.current_process]
        col_keys = [c[0] for c in col_defs]

        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure("SN.Treeview",
            background=INPUT_BG, foreground=TEXT,
            fieldbackground=INPUT_BG, borderwidth=0,
            rowheight=26, font=("Segoe UI", 10))
        style.configure("SN.Treeview.Heading",
            background="#1E3A5F", foreground=TEXT,
            font=("Segoe UI", 10, "bold"), relief="flat", anchor="center")
        style.map("SN.Treeview",
            background=[("selected", BLUE), ("!selected", INPUT_BG)],
            foreground=[("selected", "#FFFFFF"), ("!selected", TEXT)])
        style.map("SN.Treeview.Heading",
            background=[("active", "#1E3A5F"), ("!active", "#1E3A5F")])
        style.layout("SN.Treeview",
            [("Treeview.treearea", {"sticky": "nswe"})])

        vsb = ttk.Scrollbar(self._tbl_outer, orient="vertical")
        hsb = ttk.Scrollbar(self._tbl_outer, orient="horizontal")

        self.tree = ttk.Treeview(
            self._tbl_outer, columns=col_keys,
            show="headings", style="SN.Treeview",
            yscrollcommand=vsb.set, xscrollcommand=hsb.set,
            selectmode="browse"
        )
        vsb.configure(command=self.tree.yview)
        hsb.configure(command=self.tree.xview)

        for key, header, w in col_defs:
            self.tree.heading(key, text=header,
                              command=lambda k=key: self._sort_by(k),
                              anchor="center")
            self.tree.column(key, width=w, minwidth=60, anchor="center")

        self.tree.tag_configure("odd",  background=INPUT_BG)
        self.tree.tag_configure("even", background="#1A2740")

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        self._tbl_outer.grid_rowconfigure(0, weight=1)
        self._tbl_outer.grid_columnconfigure(0, weight=1)

        self.tree.bind("<Double-1>", self._on_double_click)
        self.tree.bind("<Button-3>",  self._on_right_click)

    # =========================================================
    # SWITCH CP
    # =========================================================
    def _switch_cp(self, process):
        if process == self.current_process:
            return
        self.current_process = process
        self._data = []
        self._sort_col = None
        self._sort_rev = False
        self._build_table()
        self.load_data()


    # =========================================================
    # REFRESH TABLE (main thread only)
    # =========================================================
    def _refresh_table(self, rows=None):
        self.tree.delete(*self.tree.get_children())
        col_keys = [c[0] for c in CP_COLUMN_MAP[self.current_process]]
        display  = rows if rows is not None else self._data
        for i, row in enumerate(display):
            tag = "odd" if i % 2 == 0 else "even"
            self.tree.insert("", "end",
                             values=[row.get(k, "") for k in col_keys],
                             iid=str(id(row)), tags=(tag,))
        self._count_lbl.configure(text=f"{len(display)} records")

    def _row_from_iid(self, iid):
        return next((d for d in self._data if str(id(d)) == iid), None)

    # =========================================================
    # SEARCH
    # =========================================================
    def _search_by_date(self):
        d_from = self._date_from.get_date().strftime("%Y-%m-%d")
        d_to   = self._date_to.get_date().strftime("%Y-%m-%d")
        threading.Thread(
            target=lambda: self.parent.after(0, lambda: self._apply_rows(
                self._fetch_rows("date(date_time) BETWEEN date(?) AND date(?)",
                                 (d_from, d_to))
            )), daemon=True
        ).start()

    def _search_by_barcode(self):
        q = self._barcode_var.get().strip()
        if not q:
            self.load_data()
            return
        db_cols = [c[0] for c in CP_COLUMN_MAP[self.current_process]]
        like    = " OR ".join([f"{c} LIKE ?" for c in db_cols])
        params  = tuple(f"%{q}%" for _ in db_cols)
        threading.Thread(
            target=lambda: self.parent.after(0, lambda: self._apply_rows(
                self._fetch_rows(like, params)
            )), daemon=True
        ).start()

    # =========================================================
    # SORT
    # =========================================================
    def _sort_by(self, col):
        if self._sort_col == col:
            self._sort_rev = not self._sort_rev
        else:
            self._sort_col, self._sort_rev = col, False
        self._data.sort(key=lambda r: r.get(col, ""), reverse=self._sort_rev)
        self._refresh_table()

    # =========================================================
    # SAVE CSV
    # =========================================================
    def _save_csv(self):
        import csv
        from tkinter import filedialog
        col_defs = CP_COLUMN_MAP[self.current_process]
        fp = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=f"CP{self.current_process}_snlist.csv"
        )
        if not fp:
            return
        with open(fp, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow([c[1] for c in col_defs])
            for row in self._data:
                w.writerow([row.get(c[0], "") for c in col_defs])
        messagebox.showinfo("Saved", f"CSV saved:\n{fp}", parent=self.parent)

    # =========================================================
    # DOUBLE CLICK EDIT
    # =========================================================
    def _on_double_click(self, event):
        iid = self.tree.focus()
        if not iid:
            return
        row = self._row_from_iid(iid)
        if row:
            self._open_form_popup("Edit Record", row.copy(),
                                  lambda v, r=row: self._do_edit(r, v))

    def _do_edit(self, original, new_vals):
        table   = CP_TABLE_MAP.get(self.current_process,
                                   f"snlist_cp{self.current_process}")
        db_cols = [c[0] for c in CP_COLUMN_MAP[self.current_process]]
        sets    = ", ".join([f"{c}=?" for c in db_cols])
        vals    = [new_vals.get(c, "") for c in db_cols] + [original["id"]]
        conn = self._get_conn()
        conn.execute(f"UPDATE {table} SET {sets} WHERE id=?", vals)
        conn.commit()
        conn.close()
        self.load_data()

    # =========================================================
    # RIGHT CLICK
    # =========================================================
    def _on_right_click(self, event):
        iid = self.tree.identify_row(event.y)
        if not iid:
            return
        self.tree.selection_set(iid)
        self.tree.focus(iid)
        menu = tk.Menu(self.tree, tearoff=0,
                       bg=CARD_BG, fg=TEXT,
                       activebackground="#2563EB", activeforeground="#FFFFFF",
                       font=("Segoe UI", 10), bd=0, relief="flat")
        menu.add_command(label="✏  Edit",
                         command=lambda: self._on_double_click(None))
        menu.add_separator()
        menu.add_command(label="🗑  Delete",
                         command=lambda: self._do_delete(iid))
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _do_delete(self, iid):
        row = self._row_from_iid(iid)
        if not row:
            return
        if messagebox.askyesno("Delete", "Delete this record?",
                               parent=self.parent):
            table = CP_TABLE_MAP.get(self.current_process,
                                     f"snlist_cp{self.current_process}")
            conn = self._get_conn()
            conn.execute(f"DELETE FROM {table} WHERE id=?", (row["id"],))
            conn.commit()
            conn.close()
            self.load_data()

    # =========================================================
    # FORM POPUP
    # =========================================================
    def _open_form_popup(self, title, prefill, on_save):
        col_defs = CP_COLUMN_MAP[self.current_process]
        popup = ctk.CTkToplevel(self.parent)
        popup.title(title)
        popup.configure(fg_color=BG)
        popup.grab_set()
        popup.resizable(False, False)
        ph = min(80 + len(col_defs) * 58 + 70, 640)
        popup.update_idletasks()
        sw, sh = popup.winfo_screenwidth(), popup.winfo_screenheight()
        popup.geometry(f"500x{ph}+{(sw-500)//2}+{(sh-ph)//2}")

        hdr = ctk.CTkFrame(popup, fg_color=HDR_BG, height=48, corner_radius=0)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        ctk.CTkLabel(hdr, text=title, font=("Segoe UI", 14, "bold"),
                     text_color=BLUE).pack(side="left", padx=16, pady=12)

        sf = ctk.CTkScrollableFrame(popup, fg_color=BG,
                                     scrollbar_button_color=BORDER)
        sf.pack(fill="both", expand=True)

        entries = {}
        for key, header, _ in col_defs:
            rf = ctk.CTkFrame(sf, fg_color="transparent")
            rf.pack(fill="x", padx=20, pady=(8, 0))
            ctk.CTkLabel(rf, text=header, font=("Segoe UI", 10, "bold"),
                         text_color=TEXT2, width=190, anchor="w",
                         wraplength=185).pack(side="left")
            e = ctk.CTkEntry(rf, height=34, fg_color=INPUT_BG,
                             border_color=BORDER, border_width=1,
                             text_color=TEXT, font=("Segoe UI", 11),
                             corner_radius=6)
            e.pack(side="left", fill="x", expand=True)
            val = prefill.get(key, "")
            if val:
                e.insert(0, str(val))
            entries[key] = e

        bb = ctk.CTkFrame(popup, fg_color=HDR_BG, height=56, corner_radius=0)
        bb.pack(fill="x", side="bottom")
        bb.pack_propagate(False)

        def _save():
            on_save({k: e.get().strip() for k, e in entries.items()})
            popup.destroy()

        ctk.CTkButton(bb, text="Save", width=110, height=36,
                      fg_color=SUCCESS, hover_color="#16A34A",
                      text_color="#052E16", font=("Segoe UI", 12, "bold"),
                      corner_radius=6, command=_save
                      ).pack(side="right", padx=14, pady=10)
        ctk.CTkButton(bb, text="Cancel", width=90, height=36,
                      fg_color="transparent", border_width=1,
                      border_color=BORDER, text_color=TEXT2,
                      font=("Segoe UI", 12), corner_radius=6,
                      hover_color=CARD_BG, command=popup.destroy
                      ).pack(side="right", padx=(0, 6), pady=10)

        popup.bind("<Return>", lambda e: _save())
        popup.bind("<Escape>", lambda e: popup.destroy())
        list(entries.values())[0].focus_set()


# ── Standalone test ───────────────────────────────────────
if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    root = ctk.CTk()
    root.title("SN List")
    root.geometry("1280x720")
    root.configure(fg_color=BG)
    SNListPage(root)
    root.mainloop()