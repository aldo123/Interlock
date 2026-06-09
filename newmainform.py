import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from interlockform import InterlockForm
from settingform import SettingForm

# ── Palette ──────────────────────────────────────────────────────────────────
BG       = "#0F172A"
CARD_BG  = "#1E293B"
TEXT     = "#E2E8F0"
TEXT2    = "#94A3B8"
SUCCESS  = "#22C55E"
BORDER   = "#334155"
BLUE     = "#3B82F6"
HDR_BG   = "#111827"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class NewMainForm(ctk.CTk):
    def __init__(self, user=None):
        super().__init__()
        self.user = user or {}
        self.title("WIK CP02-PCBAVM2")
        self.geometry("1440x880")
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        x = int((screen_width - 1440) / 2)
        y = int((screen_height - 880) / 2)

        self.geometry(f"1440x880+{x}+{y}")
        self.configure(fg_color=BG)
        self.minsize(1200, 700)
        self.resizable(True, True)
        self._build_header()
        self._build_body()

    # =========================================================================
    # HEADER
    # =========================================================================
    def _build_header(self):
        hdr = ctk.CTkFrame(self, fg_color=HDR_BG, height=72, corner_radius=0)
        hdr.pack(fill="x", side="top")
        hdr.pack_propagate(False)

        # ── WIK logo (left) ──────────────────────────────────────
        logo = ctk.CTkFrame(hdr, fg_color="transparent")
        logo.pack(side="left", padx=(18, 0))
        ctk.CTkLabel(logo, text="WIK", font=("Segoe UI", 32, "bold"),
                     text_color=SUCCESS).pack(side="left")
        sub = ctk.CTkFrame(logo, fg_color="transparent")
        sub.pack(side="left", padx=(8, 0), pady=4)
        ctk.CTkLabel(sub, text="Technology", font=("Segoe UI", 11),
                     text_color=TEXT2).pack(anchor="w")
        ctk.CTkLabel(sub, text="attuned to Nature", font=("Segoe UI", 11),
                     text_color=TEXT2).pack(anchor="w")

        # ── Center: title + datetime ──────────────────────────────
        center = ctk.CTkFrame(hdr, fg_color="transparent")
        center.pack(side="left", expand=True)
        ctk.CTkLabel(center, text="CP02-PCBAVM2",
                     font=("Segoe UI", 22, "bold"), text_color=SUCCESS).pack()
        ctk.CTkLabel(center, text="Monday, June 08, 2026  8:45:21 AM  WW24",
                     font=("Segoe UI", 10), text_color=TEXT2).pack()

        # ── Right: codes + user ───────────────────────────────────
        right = ctk.CTkFrame(hdr, fg_color="transparent")
        right.pack(side="right", padx=18)

        user = ctk.CTkFrame(right, fg_color="transparent")
        user.pack(side="right", padx=(20, 0))
        gear_btn = ctk.CTkButton(
            user,
            text="⚙",
            width=36,
            height=36,
            fg_color="transparent",
            hover_color="#2563EB",
            text_color=TEXT,
            font=("Segoe UI", 16),
            corner_radius=18,
            command=self.show_setting_menu
        )

        gear_btn.pack(
            side="left",
            padx=(0, 8)
        )
        ctk.CTkButton(user, text="👤", width=36, height=36,
                      fg_color="transparent", hover_color="#2563EB",
                      text_color=TEXT, font=("Segoe UI", 16),
                      corner_radius=18).pack(side="left", padx=(0, 4))
        username = self.user.get("username", "Guest")
        role = self.user.get("role", "")

        ctk.CTkLabel(
            user,
            text=f"{username}\n{role}",
            font=("Segoe UI", 10),
            text_color=TEXT2,
            justify="left"
        ).pack(side="left")

        codes = ctk.CTkFrame(right, fg_color="transparent")
        codes.pack(side="right")
        ctk.CTkLabel(codes, text="Line Code :   BW01-VM2",
                     font=("Segoe UI", 10), text_color=TEXT2, anchor="e").pack(anchor="e")
        ctk.CTkLabel(codes, text="Spec Code :   CP02-PCBAVM2",
                     font=("Segoe UI", 10), text_color=TEXT2, anchor="e").pack(anchor="e")

    # =========================================================================
    # BODY
    # =========================================================================
    def show_setting_menu(self):

        popup = ctk.CTkToplevel(self)

        popup.overrideredirect(True)

        popup.attributes("-topmost", True)

        x = self.winfo_pointerx()
        y = self.winfo_pointery()

        popup.geometry(f"220x130+{x-180}+{y+10}")

        popup.configure(
            fg_color="#0F172A"
        )

        frame = ctk.CTkFrame(
            popup,
            fg_color="#1E293B",
            corner_radius=8,
            border_width=1,
            border_color="#334155"
        )

        frame.pack(
            fill="both",
            expand=True,
            padx=2,
            pady=2
        )

        ctk.CTkLabel(
            frame,
            text="SETTINGS",
            font=("Segoe UI", 14, "bold"),
            text_color="#22C55E"
        ).pack(
            pady=(8,5)
        )

        ctk.CTkButton(
            frame,
            text="⚙  Interlock",
            anchor="w",
            height=36,
            fg_color="transparent",
            hover_color="#2563EB",
            command=lambda:[
                popup.destroy(),
                InterlockForm().show(self)
            ]
        ).pack(
            fill="x",
            padx=10,
            pady=2
        )

        ctk.CTkButton(
            frame,
            text="🔧  Setting",
            anchor="w",
            height=36,
            fg_color="transparent",
            hover_color="#2563EB",
            command=lambda:[
                popup.destroy(),
                SettingForm().show(self)
            ]
        ).pack(
            fill="x",
            padx=10,
            pady=2
        )

        popup.focus_force()

        popup.bind(
            "<FocusOut>",
            lambda e: popup.destroy()
        )

    def _build_body(self):
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True)

        self._build_sidebar(body)
        self._build_right_panel(body)   # pack right first so main gets rest
        self._build_main_content(body)

    # =========================================================================
    # SIDEBAR
    # =========================================================================
    def _build_sidebar(self, parent):
        sidebar = ctk.CTkFrame(parent, fg_color=HDR_BG, width=130, corner_radius=0)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        for label in ["Main", "MaterialStatus", "Maintenance", "SN List"]:
            ctk.CTkButton(
                sidebar, text=label, width=120, height=34,
                fg_color="transparent", hover_color=CARD_BG,
                text_color=TEXT2, anchor="w",
                font=("Segoe UI", 11), corner_radius=0
            ).pack(padx=4, pady=2, anchor="w")

    # =========================================================================
    # MAIN CONTENT
    # =========================================================================
    def _build_main_content(self, parent):
        main = ctk.CTkFrame(parent, fg_color=BG)
        main.pack(side="left", fill="both", expand=True)

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

        style = ttk.Style(self)

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

    # =========================================================================
    # RIGHT PANEL
    # =========================================================================
    def _build_right_panel(self, parent):
        right = ctk.CTkFrame(parent, fg_color=CARD_BG, width=290, corner_radius=0,
                             border_width=1, border_color=BORDER)
        right.pack(side="right", fill="y", padx=(0, 4), pady=4)
        right.pack_propagate(False)

        # Product image placeholder
        img_box = ctk.CTkFrame(right, fg_color="#172132", height=210,
                               border_width=1, border_color=BORDER, corner_radius=6)
        img_box.pack(fill="x", padx=8, pady=(8, 4))
        img_box.pack_propagate(False)
        ctk.CTkLabel(img_box, text="[ Product Image ]",
                     font=("Segoe UI", 11), text_color=TEXT2).pack(expand=True)

        # Move Status
        ms_outer = ctk.CTkFrame(right, fg_color=CARD_BG,
                                border_width=1, border_color=BORDER, corner_radius=6)
        ms_outer.pack(fill="x", padx=8, pady=(4, 4))
        ctk.CTkLabel(ms_outer, text="Move Status :",
                     font=("Segoe UI", 10), text_color=TEXT2).pack(
                         anchor="w", padx=8, pady=(4, 2))
        ctk.CTkFrame(ms_outer, fg_color="#172132",
                     height=36, corner_radius=4).pack(
                         fill="x", padx=8, pady=(0, 8))

        # Repair Action From Diagnosing
        rep_outer = ctk.CTkFrame(right, fg_color=CARD_BG,
                                 border_width=1, border_color=BORDER, corner_radius=6)
        rep_outer.pack(fill="both", expand=True, padx=8, pady=(4, 4))

        style = ttk.Style()
        style.configure("Rep.Treeview",
                        background="#172132", fieldbackground="#172132",
                        foreground=TEXT, rowheight=28,
                        font=("Segoe UI", 10))
        style.configure("Rep.Treeview.Heading",
                        background="#1E3A5F", foreground=TEXT,
                        font=("Segoe UI", 10, "bold"), relief="flat")
        rep_tree = ttk.Treeview(rep_outer, columns=("action",),
                                show="headings", style="Rep.Treeview", height=4)
        rep_tree.heading("action", text="Repair Action From Diagnosing")
        rep_tree.column("action", width=210, anchor="w")
        rep_tree.pack(fill="both", expand=True, padx=6, pady=6)


        # SN Reject
        ctk.CTkButton(
            right, text="SN Reject", height=56,
            fg_color=SUCCESS, hover_color="#16A34A",
            text_color="#052E16", font=("Segoe UI", 16, "bold"),
            corner_radius=8
        ).pack(fill="x", padx=8, pady=(4, 8))
        
        # Reset button
        ctk.CTkButton(
            right, text="Reset", height=56,
            fg_color=SUCCESS, hover_color="#16A34A",
            text_color="#052E16", font=("Segoe UI", 16, "bold"),
            corner_radius=8
        ).pack(fill="x", padx=8, pady=(4, 8))

    # =========================================================================
    # HELPER
    # =========================================================================
    def _card(self, parent, title):
        """Returns the inner frame of a labeled bordered card."""
        outer = ctk.CTkFrame(parent, fg_color=CARD_BG,
                             border_width=1, border_color=BORDER, corner_radius=6)
        outer.pack(fill="x", padx=6, pady=(6, 0))
        ctk.CTkLabel(outer, text=f" {title} ",
                     font=("Segoe UI", 10), text_color=TEXT2,
                     fg_color=CARD_BG).pack(anchor="w", padx=10, pady=(4, 0))
        inner = ctk.CTkFrame(outer, fg_color="transparent")
        inner.pack(fill="x", padx=8, pady=(0, 4))
        return inner


if __name__ == "__main__":
    app = NewMainForm()
    app.mainloop()
