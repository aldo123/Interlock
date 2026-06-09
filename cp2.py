import customtkinter as ctk
import tkinter as tk
from tkinter import ttk


# ── Palette ──────────────────────────────────────────────────────────────────
BG       = "#0F172A"
CARD_BG  = "#1E293B"
TEXT     = "#E2E8F0"
TEXT2    = "#94A3B8"
SUCCESS  = "#22C55E"
BORDER   = "#334155"
BLUE     = "#3B82F6"
HDR_BG   = "#111827"


class CP2Page:

    def __init__(self,parent,app):

        self.parent = parent
        self.app = app

        self.build_ui()

    def _card(self, parent, title):

        outer = ctk.CTkFrame(
            parent,
            fg_color=CARD_BG,
            border_width=1,
            border_color=BORDER,
            corner_radius=6
        )

        outer.pack(
            fill="x",
            padx=6,
            pady=(6,0)
        )

        ctk.CTkLabel(
            outer,
            text=title,
            text_color=TEXT2
        ).pack(
            anchor="w",
            padx=8,
            pady=(4,0)
        )

        inner = ctk.CTkFrame(
            outer,
            fg_color="transparent"
        )

        inner.pack(
            fill="x",
            padx=8,
            pady=4
        )

        return inner

    def build_ui(self):

        container = ctk.CTkFrame(
            self.parent,
            fg_color=BG
        )

        container.pack(
            fill="both",
            expand=True
        )

        main = ctk.CTkFrame(
            container,
            fg_color=BG
        )

        main.pack(
            fill="both",
            expand=True
        )

        # ── 1. Serial Number ─────────────────────────────────────
        sn_box = self._card(main, "Serial Number :")
        sn_row = ctk.CTkFrame(sn_box, fg_color="transparent")
        sn_row.pack(fill="x", pady=(6, 6))
        sn_entry_wrap = ctk.CTkFrame(sn_row, fg_color="#172132",
                                     border_width=2, border_color=BORDER, corner_radius=6)
        sn_entry_wrap.pack(side="left", padx=(0, 20))
        ctk.CTkLabel(sn_entry_wrap, text="▐▌▐▌▐▌", font=("Courier", 14),
                     text_color=TEXT2, width=28).pack(side="left", padx=(6, 0))
        ctk.CTkEntry(sn_entry_wrap, fg_color="#172132", border_width=0,
                     text_color=TEXT, placeholder_text="Scan Product SN", width=300,
                     state="disabled").pack(side="left", padx=(2, 4))
        ctk.CTkLabel(sn_row, text="Shift Completed Qty :",
                     font=("Segoe UI", 10), text_color=TEXT2).pack(side="left")
        ctk.CTkLabel(sn_row, text="  ✔ ", font=("Segoe UI", 12),
                     text_color=SUCCESS).pack(side="left")
        ctk.CTkEntry(sn_row, fg_color="#172132", border_color=BORDER,
                     text_color=TEXT, placeholder_text="", width=80,
                     state="disabled").pack(side="left", padx=8)

        # ── 2. Production Order ───────────────────────────────────
        po_outer = ctk.CTkFrame(main, fg_color=CARD_BG,
                                border_width=1, border_color=BORDER, corner_radius=6)
        po_outer.pack(fill="x", padx=6, pady=(8, 0))

        # title row (label only)
        po_hdr = ctk.CTkFrame(po_outer, fg_color="transparent")
        po_hdr.pack(fill="x", padx=10, pady=(6, 0))
        ctk.CTkLabel(po_hdr, text="Production Order :", font=("Segoe UI", 10),
                     text_color=TEXT2).pack(side="left")

        # scan entry row (icon inside entry wrap)
        po_scan = ctk.CTkFrame(po_outer, fg_color="transparent")
        po_scan.pack(fill="x", padx=10, pady=(4, 6))
        po_entry_wrap = ctk.CTkFrame(po_scan, fg_color="#172132",
                                     border_width=2, border_color=BORDER, corner_radius=6)
        po_entry_wrap.pack(side="left")
        ctk.CTkLabel(po_entry_wrap, text="📄", font=("Segoe UI", 13),
                     text_color=TEXT2).pack(side="left", padx=(6, 2))
        ctk.CTkEntry(po_entry_wrap, fg_color="#172132", border_width=0,
                     text_color=TEXT, placeholder_text="", width=280,
                     state="disabled").pack(side="left", padx=(0, 4))

        # fields: Product, Description, Order Qty, Completed Qty, Balance Qty
        po_single = ctk.CTkFrame(po_outer, fg_color="transparent")
        po_single.pack(fill="x", padx=10, pady=(0, 8))
        po_fields = [
            ("Product :",       140),
            ("Description :",   300),
            ("Order Qty :",      80),
            ("Completed Qty :",  80),
            ("Balance Qty :",    80),
        ]
        for lbl, w in po_fields:
            ctk.CTkLabel(po_single, text=lbl, font=("Segoe UI", 9, "bold"),
                         text_color=TEXT2, anchor="w").pack(side="left", padx=(4, 1))
            ctk.CTkEntry(po_single, fg_color="#172132", border_color=BORDER,
                         text_color=TEXT, placeholder_text="", width=w, height=26,
                         state="disabled").pack(side="left", padx=(0, 4))

        # ── 3. Feeding Material ───────────────────────────────────
        fm_box = self._card(main, "Feeding Material:")
        fm_row = ctk.CTkFrame(fm_box, fg_color="transparent")
        fm_row.pack(fill="x", pady=(6, 6))
        fm_entry_wrap = ctk.CTkFrame(fm_row, fg_color="#172132",
                                     border_width=2, border_color=BORDER, corner_radius=6)
        fm_entry_wrap.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(fm_entry_wrap, text="▐▌▐▌▐▌", font=("Courier", 14),
                     text_color=TEXT2, width=28).pack(side="left", padx=(6, 0))
        ctk.CTkEntry(fm_entry_wrap, fg_color="#172132", border_width=0,
                     text_color=TEXT,
                     placeholder_text="Scan Material Batch / Serial Number",
                     width=500, state="disabled").pack(side="left", padx=(2, 4), fill="x", expand=True)

        # ── 4. P/N Table ──────────────────────────────────────────
        tbl_frame = ctk.CTkFrame(main, fg_color=CARD_BG,
                                 border_width=1, border_color=BORDER, corner_radius=6)
        tbl_frame.pack(fill="x", padx=6, pady=(6, 0))

        style = ttk.Style()

        style.theme_use("default")

        style.configure(
            "PN.Treeview",
            background="#172132",
            foreground="#E2E8F0",
            fieldbackground="#172132",
            borderwidth=0,
            rowheight=28
        )

        style.configure(
            "PN.Treeview.Heading",
            background="#1E293B",
            foreground="#E2E8F0"
        )

        style.map(
            "PN.Treeview",
            background=[("selected", "#2563EB")],
            foreground=[("selected", "#FFFFFF")]
        )

        cols = ("pn", "description", "barcode", "bt_mac")
        tree = ttk.Treeview(tbl_frame, columns=cols, show="headings",
                             style="PN.Treeview", height=4)
        for col, label, w in [
            ("pn",          "P/N",                   160),
            ("description", "Description",            360),
            ("barcode",     "Barcode",                180),
            ("bt_mac",      "Bluetooth MAC Address",  200),
        ]:
            tree.heading(col, text=label)
            tree.column(col, width=w, anchor="w")
        tree.pack(fill="x", padx=6, pady=6)

        # ── 5. PCBA Barcode ───────────────────────────────────────
        pcba_box = self._card(main, "PCBA Barcode")
        pcba_row = ctk.CTkFrame(pcba_box, fg_color="transparent")
        pcba_row.pack(fill="x", pady=(2, 4))
        icons = ["📄", "👥", "🔌", "🖥", "⬛", "📦", "⊞", "▐▌▐"]
        for icon in icons:
            cell = ctk.CTkFrame(pcba_row, fg_color="#172132",
                                border_width=1, border_color=BORDER, corner_radius=4)
            cell.pack(side="left", padx=2, pady=2)
            inner_cell = ctk.CTkFrame(cell, fg_color="transparent")
            inner_cell.pack(padx=4, pady=4)
            ctk.CTkLabel(inner_cell, text=icon, font=("Segoe UI", 11),
                         text_color=TEXT2, width=20).pack(side="left")
            ctk.CTkEntry(inner_cell, fg_color="#172132", border_width=0,
                         text_color=TEXT, width=85, height=24,
                         state="disabled").pack(side="left")

        # ── 6. Instruction ────────────────────────────────────────
        ctk.CTkLabel(main, text="Instruction :",
                     font=("Segoe UI", 10, "bold"), text_color=TEXT).pack(
                         anchor="w", padx=10, pady=(8, 0))
        instr = ctk.CTkFrame(main, fg_color="#172132",
                             border_width=1, border_color=BORDER,
                             corner_radius=6, height=56)
        instr.pack(fill="x", padx=6, pady=(2, 0))
        instr.pack_propagate(False)
        inner_i = ctk.CTkFrame(instr, fg_color="transparent")
        inner_i.pack(fill="both", expand=True, padx=10)
        ctk.CTkLabel(inner_i, text="🧑‍💻", font=("Segoe UI", 22),
                     text_color=TEXT2).pack(side="left")
        ctk.CTkLabel(inner_i, text="Please Scan Material SN",
                     font=("Segoe UI", 14, "bold"),
                     text_color=SUCCESS).pack(side="left", padx=14)

        # ── 7. Message ────────────────────────────────────────────
        msg_outer = ctk.CTkFrame(main, fg_color=CARD_BG,
                                 border_width=1, border_color=BORDER, corner_radius=6)
        msg_outer.pack(fill="both", expand=True, padx=6, pady=(4, 6))
        ctk.CTkLabel(msg_outer, text=" Message ",
                     font=("Segoe UI", 10), text_color=TEXT2,
                     fg_color=CARD_BG).pack(anchor="w", padx=8, pady=(4, 0))
        msg_text = tk.Text(msg_outer, bg="#0A0F1A", fg=BLUE,
                           font=("Consolas", 9), relief="flat", bd=4,
                           insertbackground=TEXT, selectbackground="#2563EB")
        msg_text.pack(fill="both", expand=True, padx=6, pady=(2, 6))
        msg_text.config(state="disabled")