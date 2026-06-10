import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os


# ── Palette ───────────────────────────────────────────────
BG      = "#0F172A"
CARD_BG = "#1E293B"
TEXT    = "#E2E8F0"
TEXT2   = "#94A3B8"
SUCCESS = "#22C55E"
BORDER  = "#334155"
BLUE    = "#3B82F6"
HDR_BG  = "#111827"
INPUT_BG = "#172132"

# ── Kolom tabel ───────────────────────────────────────────
COLUMNS = [
    ("Name",        160),
    ("Description", 120),
    ("Program",      90),
    ("ProductType",  90),
    ("Line",         60),
    ("Partner",      80),
    ("Voltage",      70),
    ("Plug",         60),
    ("Colour",       70),
    ("Customer",     80),
]
COL_KEYS = [c[0] for c in COLUMNS]


class ReferencePage:
    def __init__(self, parent, app=None):
        self.parent = parent
        self.app = app

        self.init_db()

        self._build_ui()

        self.load_data()

    # =========================================================
    # BUILD UI
    # =========================================================
    def _build_ui(self):
        root = ctk.CTkFrame(self.parent, fg_color=BG)
        root.pack(fill="both", expand=True)

        # ── Toolbar ──────────────────────────────────────────
        toolbar = ctk.CTkFrame(root, fg_color=HDR_BG, height=52, corner_radius=0)
        toolbar.pack(fill="x")
        toolbar.pack_propagate(False)

        ctk.CTkButton(
            toolbar,
            text="＋  ADD",
            width=100, height=34,
            fg_color=SUCCESS,
            hover_color="#16A34A",
            text_color="#052E16",
            font=("Segoe UI", 12, "bold"),
            corner_radius=6,
            command=self._open_add_popup
        ).pack(side="left", padx=14, pady=9)

        # search box
        self._search_var = tk.StringVar()
        self._search_var.trace_add("write", self._on_search)
        search_wrap = ctk.CTkFrame(toolbar, fg_color=INPUT_BG,
                                   border_width=1, border_color=BORDER,
                                   corner_radius=6)
        search_wrap.pack(side="left", padx=(0, 14), pady=9)
        ctk.CTkLabel(search_wrap, text="🔍", font=("Segoe UI", 12),
                     text_color=TEXT2).pack(side="left", padx=(8, 2))
        ctk.CTkEntry(search_wrap, textvariable=self._search_var,
                     fg_color="transparent", border_width=0,
                     text_color=TEXT, placeholder_text="Search...",
                     width=220, height=32,
                     font=("Segoe UI", 11)).pack(side="left", padx=(0, 6))

        # row count label
        self._count_lbl = ctk.CTkLabel(toolbar, text="0 records",
                                       font=("Segoe UI", 10), text_color=TEXT2)
        self._count_lbl.pack(side="right", padx=14)

        # ── Table frame ──────────────────────────────────────
        tbl_outer = ctk.CTkFrame(
            root,
            fg_color=BG
        )
        tbl_outer.pack(
            fill="both",
            expand=True,
            padx=8,
            pady=(4,8)
        )

        # ttk style
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure("Ref.Treeview",
            background=INPUT_BG,
            foreground=TEXT,
            fieldbackground=INPUT_BG,
            borderwidth=0,
            rowheight=26,
            font=("Segoe UI", 10)
        )
        style.configure("Ref.Treeview.Heading",
            background="#1E3A5F",
            foreground=TEXT,
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            anchor="center"
        )
        style.map("Ref.Treeview",
            background=[("selected", BLUE), ("!selected", INPUT_BG)],
            foreground=[("selected", "#FFFFFF"), ("!selected", TEXT)]
        )
        style.map("Ref.Treeview.Heading",
            background=[("active", "#1E3A5F"), ("!active", "#1E3A5F")]
        )

        style.layout(
            "Ref.Treeview",
            [
                ("Treeview.treearea", {"sticky": "nswe"})
            ]
        )

        # scrollbars
        vsb = ttk.Scrollbar(
            tbl_outer,
            orient="vertical",
            style="Dark.Vertical.TScrollbar"
        )

        hsb = ttk.Scrollbar(
            tbl_outer,
            orient="horizontal",
            style="Dark.Horizontal.TScrollbar"
        )

        self.tree = ttk.Treeview(
            tbl_outer,
            columns=COL_KEYS,
            show="headings",
            style="Ref.Treeview",
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set,
            selectmode="browse"
        )
        vsb.configure(command=self.tree.yview)
        hsb.configure(command=self.tree.xview)

        for key, w in COLUMNS:
            self.tree.heading(key, text=key,
                              command=lambda k=key: self._sort_by(k),
                              anchor="center")
            self.tree.column(key, width=w, minwidth=50, anchor="center")

        # alternating row tags
        self.tree.tag_configure("odd",  background=INPUT_BG)
        self.tree.tag_configure("even", background="#1A2740")

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tbl_outer.grid_rowconfigure(0, weight=1)
        tbl_outer.grid_columnconfigure(0, weight=1)

        # bindings
        self.tree.bind("<Double-1>",    self._on_double_click)
        self.tree.bind("<Button-3>",    self._on_right_click)

        # internal data store: list of dicts
        self._data: list[dict] = []
        self._sort_col = None
        self._sort_rev = False

        self._refresh_table()


    def init_db(self):

        db_path = os.path.join(
            os.path.dirname(__file__),
            "reference.db"
        )

        conn = sqlite3.connect(db_path)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS reference_master (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                description TEXT,
                program TEXT,
                producttype TEXT,
                line TEXT,
                partner TEXT,
                voltage TEXT,
                plug TEXT,
                colour TEXT,
                customer TEXT
            )
        """)

        conn.commit()
        conn.close()

    def load_data(self):

        db_path = os.path.join(
            os.path.dirname(__file__),
            "reference.db"
        )

        conn = sqlite3.connect(db_path)

        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                id,
                name,
                description,
                program,
                producttype,
                line,
                partner,
                voltage,
                plug,
                colour,
                customer
            FROM reference_master
            ORDER BY name
        """)

        rows = cursor.fetchall()

        conn.close()

        self._data = []

        for row in rows:

            self._data.append({
                "id": row[0],
                "Name": row[1],
                "Description": row[2],
                "Program": row[3],
                "ProductType": row[4],
                "Line": row[5],
                "Partner": row[6],
                "Voltage": row[7],
                "Plug": row[8],
                "Colour": row[9],
                "Customer": row[10]
            })

        self._refresh_table()
    # =========================================================
    # DATA HELPERS
    # =========================================================
    def _refresh_table(self, rows=None):
        """Render rows ke treeview. rows=None → tampilkan semua _data."""
        self.tree.delete(*self.tree.get_children())
        display = rows if rows is not None else self._data
        for i, row in enumerate(display):
            tag = "odd" if i % 2 == 0 else "even"
            self.tree.insert("", "end",
                             values=[row.get(k, "") for k in COL_KEYS],
                             iid=str(id(row)),
                             tags=(tag,))
        self._count_lbl.configure(text=f"{len(display)} records")

    def _row_from_iid(self, iid):
        for d in self._data:
            if str(id(d)) == iid:
                return d
        return None

    # ── Search ───────────────────────────────────────────────
    def _on_search(self, *_):
        q = self._search_var.get().strip().lower()
        if not q:
            self._refresh_table()
            return
        filtered = [r for r in self._data
                    if any(q in str(v).lower() for v in r.values())]
        self._refresh_table(filtered)

    # ── Sort ─────────────────────────────────────────────────
    def _sort_by(self, col):
        if self._sort_col == col:
            self._sort_rev = not self._sort_rev
        else:
            self._sort_col = col
            self._sort_rev = False
        self._data.sort(key=lambda r: r.get(col, ""), reverse=self._sort_rev)
        self._refresh_table()

    # =========================================================
    # ADD POPUP
    # =========================================================
    def _open_add_popup(self):
        self._open_form_popup("Add Reference", {}, self._do_add)

    def _do_add(self, values):

        db_path = os.path.join(
            os.path.dirname(__file__),
            "reference.db"
        )

        conn = sqlite3.connect(db_path)

        conn.execute("""
            INSERT INTO reference_master
            (
                name,
                description,
                program,
                producttype,
                line,
                partner,
                voltage,
                plug,
                colour,
                customer
            )
            VALUES (?,?,?,?,?,?,?,?,?,?)
        """, (
            values["Name"],
            values["Description"],
            values["Program"],
            values["ProductType"],
            values["Line"],
            values["Partner"],
            values["Voltage"],
            values["Plug"],
            values["Colour"],
            values["Customer"]
        ))

        conn.commit()
        conn.close()

        self.load_data()

    # =========================================================
    # EDIT POPUP  (double-click)
    # =========================================================
    def _on_double_click(self, event):
        iid = self.tree.focus()
        if not iid:
            return
        row = self._row_from_iid(iid)
        if row is None:
            return
        self._open_form_popup("Edit Reference", row.copy(),
                              lambda vals, r=row: self._do_edit(r, vals))

    def _do_edit(self, original: dict, new_vals: dict):

        db_path = os.path.join(
            os.path.dirname(__file__),
            "reference.db"
        )

        conn = sqlite3.connect(db_path)

        conn.execute("""
            UPDATE reference_master
            SET
                name=?,
                description=?,
                program=?,
                producttype=?,
                line=?,
                partner=?,
                voltage=?,
                plug=?,
                colour=?,
                customer=?
            WHERE id=?
        """, (
            new_vals["Name"],
            new_vals["Description"],
            new_vals["Program"],
            new_vals["ProductType"],
            new_vals["Line"],
            new_vals["Partner"],
            new_vals["Voltage"],
            new_vals["Plug"],
            new_vals["Colour"],
            new_vals["Customer"],
            original["id"]
        ))

        conn.commit()
        conn.close()

        self.load_data()

    # =========================================================
    # RIGHT-CLICK CONTEXT MENU
    # =========================================================
    def _on_right_click(self, event):
        iid = self.tree.identify_row(event.y)
        if not iid:
            return
        self.tree.selection_set(iid)
        self.tree.focus(iid)

        menu = tk.Menu(self.tree, tearoff=0,
                       bg=CARD_BG, fg=TEXT,
                       activebackground="#2563EB",
                       activeforeground="#FFFFFF",
                       font=("Segoe UI", 10),
                       bd=0, relief="flat")
        menu.add_command(label="✏  Edit",
                         command=lambda: self._on_double_click(None))
        menu.add_separator()
        menu.add_command(label="🗑  Remove",
                         command=lambda: self._do_remove(iid))
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _do_remove(self, iid):

        row = self._row_from_iid(iid)

        if row is None:
            return

        name = row.get("Name", "this record")

        if messagebox.askyesno(
            "Remove",
            f"Remove '{name}' ?",
            parent=self.parent
        ):

            db_path = os.path.join(
                os.path.dirname(__file__),
                "reference.db"
            )

            conn = sqlite3.connect(db_path)

            conn.execute(
                "DELETE FROM reference_master WHERE id=?",
                (row["id"],)
            )

            conn.commit()
            conn.close()

            self.load_data()

    # =========================================================
    # SHARED FORM POPUP  (add & edit)
    # =========================================================
    def _open_form_popup(self, title: str, prefill: dict, on_save):
        popup = ctk.CTkToplevel(self.parent)
        popup.title(title)
        popup.configure(fg_color=BG)
        popup.grab_set()
        popup.resizable(False, False)

        # centre on screen
        pw, ph = 480, 560
        popup.update_idletasks()
        sw = popup.winfo_screenwidth()
        sh = popup.winfo_screenheight()
        popup.geometry(f"{pw}x{ph}+{(sw-pw)//2}+{(sh-ph)//2}")

        # ── Header ───────────────────────────────────────────
        hdr = ctk.CTkFrame(popup, fg_color=HDR_BG, height=48, corner_radius=0)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        ctk.CTkLabel(hdr, text=title,
                     font=("Segoe UI", 14, "bold"),
                     text_color=SUCCESS).pack(side="left", padx=16, pady=12)

        # ── Scrollable fields ────────────────────────────────
        scroll_frame = ctk.CTkScrollableFrame(popup, fg_color=BG,
                                               scrollbar_button_color=BORDER)
        scroll_frame.pack(fill="both", expand=True, padx=0, pady=0)

        entries: dict[str, ctk.CTkEntry] = {}

        for key in COL_KEYS:
            row_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
            row_frame.pack(fill="x", padx=20, pady=(8, 0))

            ctk.CTkLabel(row_frame, text=key,
                         font=("Segoe UI", 11, "bold"),
                         text_color=TEXT2, width=110,
                         anchor="w").pack(side="left")

            entry = ctk.CTkEntry(
                row_frame,
                height=36,
                fg_color=INPUT_BG,
                border_color=BORDER,
                border_width=1,
                text_color=TEXT,
                font=("Segoe UI", 11),
                corner_radius=6
            )
            entry.pack(side="left", fill="x", expand=True)

            # pre-fill existing value
            val = prefill.get(key, "")
            if val:
                entry.insert(0, str(val))

            entries[key] = entry

        # ── Buttons ──────────────────────────────────────────
        btn_bar = ctk.CTkFrame(popup, fg_color=HDR_BG, height=56, corner_radius=0)
        btn_bar.pack(fill="x", side="bottom")
        btn_bar.pack_propagate(False)

        def _save():
            vals = {k: e.get().strip() for k, e in entries.items()}
            if not vals.get("Name"):
                messagebox.showwarning("Required", "Name is required.",
                                       parent=popup)
                return
            on_save(vals)
            popup.destroy()

        ctk.CTkButton(
            btn_bar, text="Save",
            width=110, height=36,
            fg_color=SUCCESS, hover_color="#16A34A",
            text_color="#052E16",
            font=("Segoe UI", 12, "bold"),
            corner_radius=6,
            command=_save
        ).pack(side="right", padx=14, pady=10)

        ctk.CTkButton(
            btn_bar, text="Cancel",
            width=90, height=36,
            fg_color="transparent",
            border_width=1, border_color=BORDER,
            text_color=TEXT2,
            font=("Segoe UI", 12),
            corner_radius=6,
            hover_color=CARD_BG,
            command=popup.destroy
        ).pack(side="right", padx=(0, 6), pady=10)

        # bind Enter to save
        popup.bind("<Return>", lambda e: _save())
        popup.bind("<Escape>", lambda e: popup.destroy())

        # focus first entry
        list(entries.values())[0].focus_set()


# ── Standalone test ───────────────────────────────────────
if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.title("Reference")
    root.geometry("1200x700")
    root.configure(fg_color=BG)

    ReferencePage(root)
    root.mainloop()