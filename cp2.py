import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import json
import os
from datetime import datetime
import time


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

class CP2Page:

    def __init__(self,parent,app):

        self.parent = parent
        self.app = app
        self.material_scanned = False
        self.build_ui()
        self.app.cp2_page = self
        

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
        self.txt_serial_number = ctk.CTkEntry(
            sn_entry_wrap,
            fg_color="#172132",
            border_width=0,
            text_color=TEXT,
            placeholder_text="Scan Product SN",
            width=300
        )

        self.txt_serial_number.pack(
            side="left",
            padx=(2,4)
        )

        self.txt_serial_number.configure(
            state="disabled"
        )
        ctk.CTkLabel(sn_row, text="Shift Completed Qty :",
                     font=("Segoe UI", 10), text_color=TEXT2).pack(side="left")
        ctk.CTkLabel(sn_row, text="  ✔ ", font=("Segoe UI", 12),
                     text_color=SUCCESS).pack(side="left")
        ctk.CTkEntry(sn_row, fg_color="#172132", border_color=BORDER,
                     text_color=TEXT, placeholder_text="", width=80,
                     state="disabled").pack(side="left", padx=8)
        # PASS1
        ctk.CTkLabel(
            sn_row,
            text="Pass1 :",
            font=("Segoe UI", 10),
            text_color=TEXT2
        ).pack(side="left")

        ctk.CTkEntry(
            sn_row,
            width=60,
            height=28,
            fg_color="#172132",
            border_color=BORDER,
            text_color=SUCCESS,
            state="disabled"
        ).pack(side="left", padx=(4,15))

        # FPY1
        ctk.CTkLabel(
            sn_row,
            text="FPY1 :",
            font=("Segoe UI", 10),
            text_color=TEXT2
        ).pack(side="left")

        ctk.CTkEntry(
            sn_row,
            width=60,
            height=28,
            fg_color="#172132",
            border_color=BORDER,
            text_color=SUCCESS,
            state="disabled"
        ).pack(side="left", padx=(4,15))

        # PASS2
        ctk.CTkLabel(
            sn_row,
            text="Pass2 :",
            font=("Segoe UI", 10),
            text_color=TEXT2
        ).pack(side="left")

        ctk.CTkEntry(
            sn_row,
            width=60,
            height=28,
            fg_color="#172132",
            border_color=BORDER,
            text_color=SUCCESS,
            state="disabled"
        ).pack(side="left", padx=(4,15))

        # FPY2
        ctk.CTkLabel(
            sn_row,
            text="FPY2 :",
            font=("Segoe UI", 10),
            text_color=TEXT2
        ).pack(side="left")

        ctk.CTkEntry(
            sn_row,
            width=60,
            height=28,
            fg_color="#172132",
            border_color=BORDER,
            text_color=SUCCESS,
            state="disabled"
        ).pack(side="left", padx=(4,0))

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
        self.txt_feeding_material = ctk.CTkEntry(
            fm_entry_wrap,
            fg_color="#172132",
            border_width=0,
            text_color=TEXT,
            placeholder_text="Scan Material Batch / Serial Number",
            width=500
        )

        self.txt_feeding_material.pack(
            side="left",
            padx=(2,4),
            fill="x",
            expand=True
        )

        self.txt_feeding_material.configure(
            state="disabled"
        )

        # ── 4. P/N Table ──────────────────────────────────────────
        tbl_frame = ctk.CTkFrame(main, fg_color=CARD_BG,
                                 border_width=1, border_color=BORDER, corner_radius=6)
        tbl_frame.pack(fill="x", padx=6, pady=(6, 0))

        style = ttk.Style()

        style.configure(
            "PN.Treeview",
            background="#172132",
            foreground="#E2E8F0",
            fieldbackground="#172132",
            borderwidth=0,
            rowheight=28,
            font=("Segoe UI", 10)
        )
        style.configure(
            "PN.Treeview.Heading",
            background="#1E293B",
            foreground="#E2E8F0",
            font=("Segoe UI", 10, "bold"),
            relief="flat"
        )

        style.map(
            "PN.Treeview",
            background=[("selected", "#2563EB"), ("!selected", "#172132")],
            foreground=[("selected", "#FFFFFF"), ("!selected", "#E2E8F0")]
        )
        style.map(
            "PN.Treeview.Heading",
            background=[("active", "#1E3A5F"), ("!active", "#1E293B")]
        )

        cols = ("pn", "description", "barcode", "bt_mac")
        self.tree = ttk.Treeview(tbl_frame, columns=cols, show="headings",
                             style="PN.Treeview", height=4)
        for col, label, w in [
            ("pn",          "P/N",                   160),
            ("description", "Description",            360),
            ("barcode",     "Barcode",                180),
            ("bt_mac",      "Bluetooth MAC Address",  200),
        ]:
            self.tree.heading(col, text=label)
            self.tree.column(col, width=w, anchor="w")
        self.tree.pack(fill="x", padx=6, pady=6)

        # ── 5. PCBA Barcode ───────────────────────────────────────
        pcba_box = self._card(main, "PCBA Barcode")
        pcba_row = ctk.CTkFrame(pcba_box, fg_color="transparent")
        pcba_row.pack(fill="x", pady=(2, 4))
        icons = ["📄", "👥", "🔌", "🖥", "⬛", "📦", "⊞", "▐▌▐"]
        self.pcba_entries = []
        for icon in icons:
            cell = ctk.CTkFrame(pcba_row, fg_color="#172132",
                                border_width=1, border_color=BORDER, corner_radius=4)
            cell.pack(side="left", padx=2, pady=2)
            inner_cell = ctk.CTkFrame(cell, fg_color="transparent")
            inner_cell.pack(padx=4, pady=4)
            ctk.CTkLabel(inner_cell, text=icon, font=("Segoe UI", 11),
                         text_color=TEXT2, width=20).pack(side="left")
            entry = ctk.CTkEntry(
                inner_cell,
                fg_color="#172132",
                border_width=0,
                text_color=TEXT,
                width=85,
                height=24,
                state="disabled"
            )
            entry.pack(side="left")
            self.pcba_entries.append(entry)

        # ── 6. Instruction ────────────────────────────────────────
        
        instr = ctk.CTkFrame(main, fg_color="#172132",
                             border_width=1, border_color=BORDER,
                             corner_radius=6, height=56)
        instr.pack(fill="x", padx=6, pady=(2, 0))
        instr.pack_propagate(False)
        inner_i = ctk.CTkFrame(instr, fg_color="transparent")
        inner_i.pack(fill="both", expand=True, padx=10)
        ctk.CTkLabel(inner_i, text="🧑‍💻", font=("Segoe UI", 22),
                     text_color=TEXT2).pack(side="left")
        self.lbl_instruction = ctk.CTkLabel(
            inner_i,
            text="Please Scan Product SN",
            font=("Segoe UI", 14, "bold"),
            text_color=SUCCESS
        )

        self.lbl_instruction.pack(
            side="left",
            padx=14
        )

        # ── 7. Message ────────────────────────────────────────────
        msg_outer = ctk.CTkFrame(main, fg_color=CARD_BG,
                                 border_width=1, border_color=BORDER, corner_radius=6)
        msg_outer.pack(fill="both", expand=True, padx=6, pady=(4, 6))
        ctk.CTkLabel(msg_outer, text=" Message ",
                     font=("Segoe UI", 10), text_color=TEXT2,
                     fg_color=CARD_BG).pack(anchor="w", padx=8, pady=(4, 0))
        self.msg_text = tk.Text(
            msg_outer,
            bg="#0A0F1A",
            fg="#00FF88",
            font=("Consolas", 10),
            relief="flat",
            bd=4,
            insertbackground=TEXT,
            selectbackground="#2563EB"
        )
        self.msg_text.pack(
            fill="both",
            expand=True,
            padx=6,
            pady=(2,6)
        )

        self.msg_text.config(
            state="disabled"
        )

    def handle_scan(
        self,
        device_name,
        data
    ):

        self.add_log(
            f"[{device_name}] {data}",
            "#00BFFF"
        )

        device = device_name.lower()

        if device == "product":

            self.scan_product(data)

        elif device == "part":

            # ==================================
            # MATERIAL BELUM DISCAN
            # ==================================
            if not self.material_scanned:

                self.scan_material(data)

            # ==================================
            # MATERIAL SUDAH DISCAN
            # BERARTI DATA BERIKUTNYA = MAC
            # ==================================
            else:

                self.update_mac_address(data)

                self.add_log(
                    f"MAC Address : {data}",
                    "#22C55E"
                )

                self.lbl_instruction.configure(
                    text="PASS"
                )

    def scan_product(
        self,
        serial_number
    ):

        current_sn = self.txt_serial_number.get().strip()

        if current_sn:

            self.add_log(
                f"Product SN already scanned : {current_sn}"
            )
            return

        self.txt_serial_number.configure(
            state="normal"
        )

        self.txt_serial_number.insert(
            0,
            serial_number
        )

        self.txt_serial_number.configure(
            state="disabled"
        )

        self.lbl_instruction.configure(
            text="Please Scan Main PCBA SN"
        )
    
    def scan_material(
        self,
        material_sn
    ):

        product_sn = self.txt_serial_number.get().strip()

        if not product_sn:

            self.add_log(
                "Scan Product SN first"
            )

            return

        required_voltage = self.get_required_voltage(
            product_sn
        )

        material_voltage = self.get_material_voltage(
            material_sn
        )

        self.add_log(
            f"Required Voltage : {required_voltage}"
        )

        self.add_log(
            f"Material Voltage : {material_voltage}"
        )

        if material_voltage != required_voltage:

            self.lbl_instruction.configure(
                text=f"PCBA difference voltage please re-scan PCBA ({required_voltage})"
            )

            return

        current_material = self.txt_feeding_material.get().strip()

        if current_material:

            self.add_log(
                f"Material already scanned : {current_material}"
            )

            return

        self.txt_feeding_material.configure(
            state="normal"
        )

        self.txt_feeding_material.insert(
            0,
            material_sn
        )

        self.txt_feeding_material.configure(
            state="disabled"
        )

        material_data = self.parse_material_data(
            material_sn
        )

        # =====================================
        # TABLE
        # =====================================

        for item in self.tree.get_children():

            self.tree.delete(item)

        self.tree.insert(
            "",
            "end",
            values=(
                material_data.get("PN",""),
                f"Main PCBA ({material_data.get('Voltage','')})",
                material_sn,
                ""
            )
        )

        # =====================================
        # PCBA BARCODE FIELD
        # =====================================

        pcba_values = [

            material_data.get("PN",""),
            material_data.get("Vendor",""),
            material_data.get("Voltage",""),
            material_data.get("HW Ver",""),
            material_data.get("FW Ver",""),
            material_data.get("ESP FW",""),
            material_data.get("Date",""),
            material_data.get("Serial Number","")

        ]

        for entry,value in zip(
            self.pcba_entries,
            pcba_values
        ):

            entry.configure(
                state="normal"
            )

            entry.delete(
                0,
                "end"
            )

            entry.insert(
                0,
                value
            )

            entry.configure(
                state="disabled"
            )

        self.lbl_instruction.configure(
            text="Scan Mac Address"
        )
        self.material_scanned = True
        

    def reset_interlock(self):

        self.txt_serial_number.configure(
            state="normal"
        )

        self.txt_serial_number.delete(
            0,
            "end"
        )

        self.txt_serial_number.configure(
            state="disabled"
        )

        self.txt_feeding_material.configure(
            state="normal"
        )

        self.txt_feeding_material.delete(
            0,
            "end"
        )

        self.txt_feeding_material.configure(
            state="disabled"
        )

        self.lbl_instruction.configure(
            text="Please Scan Product SN"
        )
        self.material_scanned = False

        for item in self.tree.get_children():

            self.tree.delete(item)

        # =====================================
        # CLEAR PCBA FIELD
        # =====================================

        for entry in self.pcba_entries:

            entry.configure(
                state="normal"
            )

            entry.delete(
                0,
                "end"
            )

            entry.configure(
                state="disabled"
            )

    def get_required_voltage(
        self,
        product_sn
    ):

        try:

            path = os.path.join(
                os.path.dirname(__file__),
                "setting.json"
            )

            with open(
                path,
                "r",
                encoding="utf-8"
            ) as f:

                setting = json.load(f)

            voltage_pos = int(
                setting["SN Chassis Mapping"]["Voltage"]
            )

            product_code = product_sn[
                voltage_pos - 1
            ]

            for row in setting["Product Rules"]["_table"]:

                if row["Product"] == product_code:

                    return row["Part Voltage"]

        except Exception as e:

            self.add_log(
                f"Voltage Rule Error: {e}"
            )

            return ""
    
    def get_material_voltage(
        self,
        material_sn
    ):

        try:

            path = os.path.join(
                os.path.dirname(__file__),
                "setting.json"
            )

            with open(
                path,
                "r",
                encoding="utf-8"
            ) as f:

                setting = json.load(f)

            voltage_range = setting[
                "Product Matrix Mapping"
            ]["Voltage"]

            start,end = map(
                int,
                voltage_range.split("-")
            )

            return material_sn[
                start - 1 : end
            ]

        except Exception as e:

            self.add_log(
                f"Material Voltage Error: {e}"
            )

        return ""
    

    def add_log(
        self,
        message,
        color="#00FF88"
    ):

        try:

            timestamp = datetime.now().strftime(
                "%H:%M:%S"
            )

            self.msg_text.configure(
                state="normal"
            )

            tag = f"log_{time.time()}"

            self.msg_text.tag_config(
                tag,
                foreground=color
            )

            self.msg_text.insert(
                "end",
                f"[{timestamp}] {message}\n",
                tag
            )

            self.msg_text.see("end")

            self.msg_text.configure(
                state="disabled"
            )

        except Exception:
            pass

    def parse_material_data(
        self,
        material_sn
    ):

        path = os.path.join(
            os.path.dirname(__file__),
            "setting.json"
        )

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as f:

            setting = json.load(f)

        mapping = setting[
            "Product Matrix Mapping"
        ]

        result = {}

        for field,rng in mapping.items():

            if "-" not in str(rng):
                continue

            start,end = map(
                int,
                rng.split("-")
            )

            result[field] = material_sn[
                start-1:end
            ]

        return result
    
    def update_mac_address(
        self,
        mac_address
    ):

        items = self.tree.get_children()

        if not items:
            return

        item = items[0]

        values = list(
            self.tree.item(item)["values"]
        )

        values[3] = mac_address

        self.tree.item(
            item,
            values=values
        )