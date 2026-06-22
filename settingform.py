import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, ttk
import json
import os

# ── Palette ───────────────────────────────────────────────────────────────────
CARD_BG  = "#0F172A"
CARD_BG2 = "#18202D"
TEXT     = "#F8FAFC"
TEXT2    = "#94A3B8"
BORDER   = "#22364A"
SUCCESS  = "#10B981"
DANGER   = "#EF4444"
BLUE     = "#3B82F6"


# =============================================================================
# SETTING FORM
# =============================================================================
class SettingForm:

    def __init__(self):
        pass

    # =========================================================================
    # PATH & JSON
    # =========================================================================
    def get_setting_path(self):
        return os.path.join(
            os.path.dirname(__file__),
            "setting.json"
        )

    def load_setting(self):

        default = {
            "Message": {
                "OK Color": "Green",
                "OK Font":  "Arial 24 Bold",
                "NOK Color": "Red",
                "NOK Font":  "Arial 24 Bold"
            },
            "Communication Devices": {
                "_table": [
                    {
                        "Device Name": "PSN",
                        "Type": "TCP",
                        "IP Address": "192.168.108.1",
                        "Port": "9004"
                    },
                    {
                        "Device Name": "PSN Part",
                        "Type": "TCP",
                        "IP Address": "192.168.108.2",
                        "Port": "9004"
                    }
                ]
            },
            "Product Rules": {
                "_table": [
                    {"Product": "1", "Part Voltage": "127V"},
                    {"Product": "2", "Part Voltage": "240V"}
                ]
            },
            "Product Matrix Mapping": {
                "Part Matrix":   "47",
                "PN":            "1-7",
                "Vendor":        "",
                "Voltage":       "",
                "HW Ver":        "",
                "FW Ver":        "",
                "ESP FW":        "",
                "Date":          "",
                "Serial Number": ""
            },

            "SN Chassis Mapping": {
                "Product Matrix": "1-2",
                "Date": "3-4",
                "Type": "3-4",
                "Line": "5-6",
                "Serial Number": "7-12",
                "Partner": "13-14",
                "Voltage": "15-18",
                "Plug": "19-20",
                "Color": "21-22"
            }
            
        }

        path = self.get_setting_path()

        try:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass

        return default

    def save_setting(self, data):

        path = self.get_setting_path()

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

            

    # =========================================================================
    # SHOW DIALOG
    # =========================================================================
    def show(self, parent):

        dlg = ctk.CTkToplevel(parent)
        dlg.title("System Configuration")
        width = 600
        height = 580

        parent.update_idletasks()

        x = parent.winfo_x() + (parent.winfo_width() // 2) - (width // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (height // 2)

        dlg.geometry(f"{width}x{height}+{x}+{y}")
        dlg.transient(parent)
        dlg.grab_set()
        dlg.configure(fg_color=CARD_BG)

        # ── Title bar ─────────────────────────────────────────────────────────
        title_bar = ctk.CTkFrame(dlg, fg_color=CARD_BG2, height=46, corner_radius=0)
        title_bar.pack(fill="x")
        title_bar.pack_propagate(False)

        ctk.CTkLabel(
            title_bar,
            text="System Configuration",
            font=("Segoe UI", 13, "bold"),
            text_color=TEXT
        ).pack(side="left", padx=16, pady=10)

        # ── Scrollable content ────────────────────────────────────────────────
        content_frame = ctk.CTkFrame(dlg, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=0, pady=0)

        canvas = tk.Canvas(content_frame, bg=CARD_BG, highlightthickness=0)
        vscroll = tk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vscroll.set)
        vscroll.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        inner = ctk.CTkFrame(canvas, fg_color="transparent")
        win_id = canvas.create_window((0, 0), window=inner, anchor="nw")

        def _on_configure(e):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def _on_canvas_resize(e):
            try:
                canvas.itemconfig(win_id, width=e.width)
            except Exception:
                pass

        def _on_mousewheel(e):
            canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")

        inner.bind("<Configure>", _on_configure)
        canvas.bind("<Configure>", _on_canvas_resize)
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        dlg.bind("<Destroy>", lambda e: canvas.unbind_all("<MouseWheel>"))

        # ── Footer ────────────────────────────────────────────────────────────
        footer = ctk.CTkFrame(dlg, fg_color=CARD_BG2, height=56, corner_radius=0)
        footer.pack(side="bottom", fill="x")
        footer.pack_propagate(False)

        # ── Load data ─────────────────────────────────────────────────────────
        sections   = self.load_setting()
        entries    = {}          # entries[section][field] = widget
        table_rows = []          # list of {"Product": ..., "Part Voltage": ...}
        device_rows = []
        LABEL_W = 180
        ENTRY_W = 300

        # ── Color options ─────────────────────────────────────────────────────
        COLOR_OPTIONS = ["Green", "Red", "Yellow", "White", "Blue", "Orange"]
        FONT_OPTIONS  = [
            "Arial 24 Bold", "Arial 20 Bold", "Arial 16 Bold",
            "Segoe UI 24 Bold", "Courier 20 Bold"
        ]
        TYPE_OPTIONS  = ["TCP", "COM"]

        # dropdown fields map
        DROPDOWN_MAP = {
            "OK Color":  COLOR_OPTIONS,
            "NOK Color": COLOR_OPTIONS,
            "OK Font":   FONT_OPTIONS,
            "NOK Font":  FONT_OPTIONS,
        }

        # ── Helper: divider ───────────────────────────────────────────────────
        def _divider(parent):
            ctk.CTkFrame(
                parent,
                height=1,
                fg_color=BORDER
            ).pack(fill="x", padx=12, pady=(0, 4))

        # ── Helper: section header ────────────────────────────────────────────
        def _section_header(parent, title):
            f = ctk.CTkFrame(parent, fg_color="transparent")
            f.pack(fill="x", padx=12, pady=(14, 2))
            ctk.CTkLabel(
                f, text=f"[ {title} ]",
                font=("Segoe UI", 11, "bold"),
                text_color=TEXT2
            ).pack(anchor="w")
            _divider(parent)

        # ── Helper: row ───────────────────────────────────────────────────────
        def _row(parent, label, value, dropdown_opts=None):
            row = ctk.CTkFrame(parent, fg_color="transparent")
            row.pack(fill="x", padx=20, pady=2)

            ctk.CTkLabel(
                row,
                text=label,
                width=LABEL_W,
                anchor="w",
                font=("Segoe UI", 10),
                text_color=TEXT
            ).pack(side="left")

            if dropdown_opts:
                widget = ctk.CTkOptionMenu(
                    row,
                    values=dropdown_opts,
                    width=ENTRY_W,
                    fg_color="#172132",
                    button_color="#1E3A5F",
                    button_hover_color="#2563EB",
                    text_color=TEXT,
                    font=("Segoe UI", 10)
                )
                widget.set(value)
            else:
                widget = ctk.CTkEntry(
                    row,
                    width=ENTRY_W,
                    height=28,
                    fg_color="#172132",
                    border_color=BORDER,
                    text_color=TEXT,
                    font=("Segoe UI", 10)
                )
                widget.insert(0, value)

            widget.pack(side="left", padx=(10, 0))
            return widget

        
        # ── Build sections ────────────────────────────────────────────────────
        for section_name, fields in sections.items():

            _section_header(inner, section_name)
            entries[section_name] = {}

            if section_name == "Communication Devices":

                device_rows = fields.get("_table", [])

                tbl_frame = ctk.CTkFrame(
                    inner,
                    fg_color="#172132",
                    border_width=1,
                    border_color=BORDER
                )

                tbl_frame.pack(
                    fill="x",
                    padx=20,
                    pady=(4,2)
                )

                cols = (
                    "device",
                    "type",
                    "config"
                )

                device_tree = ttk.Treeview(
                    tbl_frame,
                    columns=cols,
                    show="headings",
                    style="SR.Treeview",
                    height=5
                )

                device_tree.heading(
                    "device",
                    text="Device Name"
                )

                device_tree.heading(
                    "type",
                    text="Type"
                )

                device_tree.heading(
                    "config",
                    text="Configuration"
                )

                device_tree.column(
                    "device",
                    width=180,
                    anchor="center"
                )

                device_tree.column(
                    "type",
                    width=100,
                    anchor="center"
                )

                device_tree.column(
                    "config",
                    width=240,
                    anchor="center"
                )

                device_tree.pack(
                    fill="x",
                    padx=6,
                    pady=6
                )

                def refresh_device_tree():

                    for item in device_tree.get_children():
                        device_tree.delete(item)

                    for row in device_rows:

                        if row["Type"] == "TCP":

                            cfg = (
                                f'{row["IP Address"]}:'
                                f'{row["Port"]}'
                            )

                        else:

                            cfg = (
                                f'{row["COM Port"]} '
                                f'@{row["Baudrate"]}'
                            )

                        device_tree.insert(
                            "",
                            "end",
                            values=(
                                row["Device Name"],
                                row["Type"],
                                cfg
                            )
                        )

                refresh_device_tree()
                btn_row = ctk.CTkFrame(
                    inner,
                    fg_color="transparent"
                )

                btn_row.pack(
                    anchor="w",
                    padx=20,
                    pady=(2,4)
                )

                def add_device():

                    popup = ctk.CTkToplevel(dlg)

                    popup.title("Add Device")

                    popup.geometry("450x380")

                    popup.transient(dlg)

                    popup.grab_set()

                    popup.configure(
                        fg_color=CARD_BG
                    )

                    ctk.CTkLabel(
                        popup,
                        text="Device Name",
                        text_color=TEXT
                    ).pack(
                        pady=(15,5)
                    )

                    e_name = ctk.CTkEntry(
                        popup,
                        width=250
                    )

                    e_name.pack()

                    type_var = ctk.StringVar(
                        value="TCP"
                    )

                    type_menu = ctk.CTkOptionMenu(
                        popup,
                        values=["TCP","COM"],
                        variable=type_var
                    )

                    type_menu.pack(
                        pady=10
                    )

                    detail_frame = ctk.CTkFrame(
                        popup,
                        fg_color="transparent"
                    )

                    detail_frame.pack(
                        fill="x"
                    )

                    tcp_frame = ctk.CTkFrame(
                        detail_frame,
                        fg_color="transparent"
                    )

                    ctk.CTkLabel(
                        tcp_frame,
                        text="IP Address",
                        text_color=TEXT
                    ).pack()

                    e_ip = ctk.CTkEntry(
                        tcp_frame,
                        width=250
                    )

                    e_ip.insert(
                        0,
                        "192.168.108.1"
                    )

                    e_ip.pack()

                    ctk.CTkLabel(
                        tcp_frame,
                        text="Port",
                        text_color=TEXT
                    ).pack()

                    e_port = ctk.CTkEntry(
                        tcp_frame,
                        width=250
                    )

                    e_port.insert(
                        0,
                        "9004"
                    )

                    e_port.pack()

                    com_frame = ctk.CTkFrame(
                        detail_frame,
                        fg_color="transparent"
                    )

                    ctk.CTkLabel(
                        com_frame,
                        text="COM Port",
                        text_color=TEXT
                    ).pack()

                    e_com = ctk.CTkEntry(
                        com_frame,
                        width=250
                    )

                    e_com.insert(
                        0,
                        "COM3"
                    )

                    e_com.pack()

                    baud_menu = ctk.CTkOptionMenu(
                        com_frame,
                        values=[
                            "1200",
                            "2400",
                            "4800",
                            "9600",
                            "19200",
                            "38400",
                            "57600",
                            "115200"
                        ]
                    )

                    baud_menu.pack(
                        pady=4
                    )

                    parity_menu = ctk.CTkOptionMenu(
                        com_frame,
                        values=[
                            "None",
                            "Even",
                            "Odd"
                        ]
                    )

                    parity_menu.pack(
                        pady=4
                    )

                    bit_menu = ctk.CTkOptionMenu(
                        com_frame,
                        values=[
                            "5",
                            "6",
                            "7",
                            "8"
                        ]
                    )

                    bit_menu.pack(
                        pady=4
                    )

                    stop_menu = ctk.CTkOptionMenu(
                        com_frame,
                        values=[
                            "1",
                            "1.5",
                            "2"
                        ]
                    )

                    stop_menu.pack(
                        pady=4
                    )

                    def type_changed(choice):

                        tcp_frame.pack_forget()

                        com_frame.pack_forget()

                        if choice == "TCP":

                            tcp_frame.pack(
                                fill="x"
                            )

                        else:

                            com_frame.pack(
                                fill="x"
                            )

                    type_menu.configure(
                        command=type_changed
                    )

                    type_changed("TCP")

                    def save_device():
                        if not e_name.get().strip():

                            messagebox.showerror(
                                "Error",
                                "Device Name is required",
                                parent=popup
                            )

                            return
                        
                        for dev in device_rows:

                            if dev["Device Name"].lower() == e_name.get().lower():

                                messagebox.showerror(
                                    "Error",
                                    "Device already exists",
                                    parent=popup
                                )

                                return

                        if type_var.get() == "TCP":

                            device_rows.append(
                                {
                                    "Device Name": e_name.get(),
                                    "Type": "TCP",
                                    "IP Address": e_ip.get(),
                                    "Port": e_port.get()
                                }
                            )

                        else:

                            device_rows.append(
                                {
                                    "Device Name": e_name.get(),
                                    "Type": "COM",
                                    "COM Port": e_com.get(),
                                    "Baudrate": baud_menu.get(),
                                    "Parity": parity_menu.get(),
                                    "Data Bits": bit_menu.get(),
                                    "Stop Bits": stop_menu.get()
                                }
                            )

                        refresh_device_tree()
                        popup.destroy()

                    ctk.CTkButton(
                        popup,
                        text="Save",
                        fg_color=SUCCESS,
                        command=save_device
                    ).pack(
                        pady=10
                    )
                
                ctk.CTkButton(
                    btn_row,
                    text="Add",
                    command=add_device,
                    fg_color=SUCCESS
                ).pack(
                    side="left",
                    padx=5
                )

                def edit_device():

                    sel = device_tree.selection()

                    if not sel:

                        messagebox.showwarning(
                            "Warning",
                            "Please select device first",
                            parent=dlg
                        )

                        return

                    idx = device_tree.index(sel[0])

                    device = device_rows[idx]

                    popup = ctk.CTkToplevel(dlg)

                    popup.title("Edit Device")

                    popup.geometry("450x420")

                    popup.transient(dlg)

                    popup.grab_set()

                    popup.configure(
                        fg_color=CARD_BG
                    )

                    # =====================================================
                    # DEVICE NAME
                    # =====================================================

                    ctk.CTkLabel(
                        popup,
                        text="Device Name",
                        text_color=TEXT
                    ).pack(
                        pady=(15,5)
                    )

                    e_name = ctk.CTkEntry(
                        popup,
                        width=250
                    )

                    e_name.pack()

                    e_name.insert(
                        0,
                        device["Device Name"]
                    )

                    # =====================================================
                    # TYPE
                    # =====================================================

                    type_var = ctk.StringVar(
                        value=device["Type"]
                    )

                    type_menu = ctk.CTkOptionMenu(
                        popup,
                        values=["TCP","COM"],
                        variable=type_var
                    )

                    type_menu.pack(
                        pady=10
                    )

                    detail_frame = ctk.CTkFrame(
                        popup,
                        fg_color="transparent"
                    )

                    detail_frame.pack(
                        fill="x"
                    )

                    # =====================================================
                    # TCP FRAME
                    # =====================================================

                    tcp_frame = ctk.CTkFrame(
                        detail_frame,
                        fg_color="transparent"
                    )

                    ctk.CTkLabel(
                        tcp_frame,
                        text="IP Address",
                        text_color=TEXT
                    ).pack()

                    e_ip = ctk.CTkEntry(
                        tcp_frame,
                        width=250
                    )

                    e_ip.pack()

                    ctk.CTkLabel(
                        tcp_frame,
                        text="Port",
                        text_color=TEXT
                    ).pack()

                    e_port = ctk.CTkEntry(
                        tcp_frame,
                        width=250
                    )

                    e_port.pack()

                    # =====================================================
                    # COM FRAME
                    # =====================================================

                    com_frame = ctk.CTkFrame(
                        detail_frame,
                        fg_color="transparent"
                    )

                    ctk.CTkLabel(
                        com_frame,
                        text="COM Port",
                        text_color=TEXT
                    ).pack()

                    e_com = ctk.CTkEntry(
                        com_frame,
                        width=250
                    )

                    e_com.pack()

                    baud_menu = ctk.CTkOptionMenu(
                        com_frame,
                        values=[
                            "1200",
                            "2400",
                            "4800",
                            "9600",
                            "19200",
                            "38400",
                            "57600",
                            "115200"
                        ]
                    )

                    baud_menu.pack(
                        pady=4
                    )

                    parity_menu = ctk.CTkOptionMenu(
                        com_frame,
                        values=[
                            "None",
                            "Even",
                            "Odd"
                        ]
                    )

                    parity_menu.pack(
                        pady=4
                    )

                    bit_menu = ctk.CTkOptionMenu(
                        com_frame,
                        values=[
                            "5",
                            "6",
                            "7",
                            "8"
                        ]
                    )

                    bit_menu.pack(
                        pady=4
                    )

                    stop_menu = ctk.CTkOptionMenu(
                        com_frame,
                        values=[
                            "1",
                            "1.5",
                            "2"
                        ]
                    )

                    stop_menu.pack(
                        pady=4
                    )

                    # =====================================================
                    # LOAD CURRENT DATA
                    # =====================================================

                    if device["Type"] == "TCP":

                        e_ip.insert(
                            0,
                            device.get(
                                "IP Address",
                                ""
                            )
                        )

                        e_port.insert(
                            0,
                            device.get(
                                "Port",
                                ""
                            )
                        )

                    else:

                        e_com.insert(
                            0,
                            device.get(
                                "COM Port",
                                ""
                            )
                        )

                        baud_menu.set(
                            device.get(
                                "Baudrate",
                                "115200"
                            )
                        )

                        parity_menu.set(
                            device.get(
                                "Parity",
                                "None"
                            )
                        )

                        bit_menu.set(
                            device.get(
                                "Data Bits",
                                "8"
                            )
                        )

                        stop_menu.set(
                            device.get(
                                "Stop Bits",
                                "1"
                            )
                        )

                    # =====================================================
                    # TYPE CHANGE
                    # =====================================================

                    def type_changed(choice):

                        tcp_frame.pack_forget()

                        com_frame.pack_forget()

                        if choice == "TCP":

                            tcp_frame.pack(
                                fill="x"
                            )

                        else:

                            com_frame.pack(
                                fill="x"
                            )

                    type_menu.configure(
                        command=type_changed
                    )

                    type_changed(
                        device["Type"]
                    )

                    # =====================================================
                    # SAVE
                    # =====================================================

                    def save_edit():

                        if not e_name.get().strip():

                            messagebox.showerror(
                                "Error",
                                "Device Name is required",
                                parent=popup
                            )

                            return

                        if type_var.get() == "TCP":

                            device_rows[idx] = {

                                "Device Name": e_name.get().strip(),

                                "Type": "TCP",

                                "IP Address": e_ip.get().strip(),

                                "Port": e_port.get().strip()
                            }

                        else:

                            device_rows[idx] = {

                                "Device Name": e_name.get().strip(),

                                "Type": "COM",

                                "COM Port": e_com.get().strip(),

                                "Baudrate": baud_menu.get(),

                                "Parity": parity_menu.get(),

                                "Data Bits": bit_menu.get(),

                                "Stop Bits": stop_menu.get()
                            }

                        refresh_device_tree()

                        popup.destroy()

                    ctk.CTkButton(
                        popup,
                        text="Save",
                        fg_color=BLUE,
                        command=save_edit
                    ).pack(
                        pady=15
                    )
                
                ctk.CTkButton(
                    btn_row,
                    text="Edit",
                    command=edit_device,
                    fg_color=BLUE
                ).pack(
                    side="left",
                    padx=5
                )

                def delete_device():

                    sel = device_tree.selection()

                    if not sel:
                        return

                    idx = device_tree.index(sel[0])

                    device_rows.pop(idx)

                    refresh_device_tree()


                ctk.CTkButton(
                    btn_row,
                    text="Delete",
                    command=delete_device,
                    fg_color=DANGER
                ).pack(
                    side="left",
                    padx=5
                )

                
                continue
            # ── Product Rules → table with Add/Edit/Delete ─────────────────
            if section_name == "Product Rules":

                tbl_frame = ctk.CTkFrame(
                    inner,
                    fg_color="#172132",
                    border_width=1,
                    border_color=BORDER,
                    corner_radius=6
                )
                tbl_frame.pack(fill="x", padx=20, pady=(4, 2))

                # style treeview
                style = ttk.Style()
                style.theme_use("clam")
                style.configure(
                    "SR.Treeview",
                    background="#172132",
                    fieldbackground="#172132",
                    foreground=TEXT,
                    rowheight=26,
                    font=("Segoe UI", 10)
                )
                style.configure(
                    "SR.Treeview.Heading",
                    background="#1E3A5F",
                    foreground=TEXT,
                    font=("Segoe UI", 10, "bold"),
                    relief="flat"
                )
                style.map(
                    "SR.Treeview",
                    background=[("selected", "#2563EB")]
                )

                cols = ("product", "part_voltage")
                tree = ttk.Treeview(
                    tbl_frame,
                    columns=cols,
                    show="headings",
                    style="SR.Treeview",
                    height=5
                )
                tree.heading("product",     text="Product")
                tree.heading("part_voltage", text="Part Voltage")
                tree.column("product",     width=160, anchor="center")
                tree.column("part_voltage", width=200, anchor="center")
                tree.pack(fill="x", padx=6, pady=6)

                # load initial rows
                initial_rows = fields.get("_table", [])
                for r in initial_rows:
                    table_rows.append(r.copy())
                    tree.insert("", "end", values=(r["Product"], r["Part Voltage"]))

                # ── Add / Edit / Delete buttons ────────────────────────────
                btn_row = ctk.CTkFrame(inner, fg_color="transparent")
                btn_row.pack(anchor="w", padx=20, pady=(2, 4))

                def _refresh_tree():
                    for item in tree.get_children():
                        tree.delete(item)
                    for r in table_rows:
                        tree.insert("", "end", values=(r["Product"], r["Part Voltage"]))

                def _add_row():
                    popup = ctk.CTkToplevel(dlg)
                    popup.title("Add Row")
                    popup.geometry("320x160")
                    popup.transient(dlg)
                    popup.grab_set()
                    popup.configure(fg_color=CARD_BG)

                    ctk.CTkLabel(popup, text="Product",     text_color=TEXT).grid(row=0, column=0, padx=16, pady=10, sticky="w")
                    ctk.CTkLabel(popup, text="Part Voltage", text_color=TEXT).grid(row=1, column=0, padx=16, pady=4,  sticky="w")

                    e_prod = ctk.CTkEntry(popup, fg_color="#172132", border_color=BORDER, text_color=TEXT, width=160)
                    e_volt = ctk.CTkEntry(popup, fg_color="#172132", border_color=BORDER, text_color=TEXT, width=160)
                    e_prod.grid(row=0, column=1, padx=8, pady=10)
                    e_volt.grid(row=1, column=1, padx=8, pady=4)

                    def _confirm():
                        p = e_prod.get().strip()
                        v = e_volt.get().strip()
                        if p and v:
                            table_rows.append({"Product": p, "Part Voltage": v})
                            _refresh_tree()
                        popup.destroy()

                    ctk.CTkButton(
                        popup, text="Add", fg_color=SUCCESS,
                        command=_confirm, width=100
                    ).grid(row=2, column=1, pady=12, sticky="e", padx=8)

                def _edit_row():
                    sel = tree.selection()
                    if not sel:
                        return
                    idx   = tree.index(sel[0])
                    row_d = table_rows[idx]

                    popup = ctk.CTkToplevel(dlg)
                    popup.title("Edit Row")
                    popup.geometry("320x160")
                    popup.transient(dlg)
                    popup.grab_set()
                    popup.configure(fg_color=CARD_BG)

                    ctk.CTkLabel(popup, text="Product",     text_color=TEXT).grid(row=0, column=0, padx=16, pady=10, sticky="w")
                    ctk.CTkLabel(popup, text="Part Voltage", text_color=TEXT).grid(row=1, column=0, padx=16, pady=4,  sticky="w")

                    e_prod = ctk.CTkEntry(popup, fg_color="#172132", border_color=BORDER, text_color=TEXT, width=160)
                    e_volt = ctk.CTkEntry(popup, fg_color="#172132", border_color=BORDER, text_color=TEXT, width=160)
                    e_prod.insert(0, row_d["Product"])
                    e_volt.insert(0, row_d["Part Voltage"])
                    e_prod.grid(row=0, column=1, padx=8, pady=10)
                    e_volt.grid(row=1, column=1, padx=8, pady=4)

                    def _confirm():
                        p = e_prod.get().strip()
                        v = e_volt.get().strip()
                        if p and v:
                            table_rows[idx] = {"Product": p, "Part Voltage": v}
                            _refresh_tree()
                        popup.destroy()

                    ctk.CTkButton(
                        popup, text="Save", fg_color=BLUE,
                        command=_confirm, width=100
                    ).grid(row=2, column=1, pady=12, sticky="e", padx=8)

                def _delete_row():
                    sel = tree.selection()
                    if not sel:
                        return
                    idx = tree.index(sel[0])
                    table_rows.pop(idx)
                    _refresh_tree()

                for label, cmd, color in [
                    ("Add",    _add_row,    SUCCESS),
                    ("Edit",   _edit_row,   BLUE),
                    ("Delete", _delete_row, DANGER),
                ]:
                    ctk.CTkButton(
                        btn_row, text=label, width=80, height=28,
                        fg_color=color, hover_color="#0F2040",
                        text_color=TEXT, font=("Segoe UI", 10, "bold"),
                        command=cmd, corner_radius=4
                    ).pack(side="left", padx=(0, 6))

                continue  # skip normal field rendering for this section

            # ── Normal sections ────────────────────────────────────────────
            for field_name, value in fields.items():

                opts   = DROPDOWN_MAP.get(field_name)
                widget = _row(inner, field_name, str(value), dropdown_opts=opts)
                entries[section_name][field_name] = widget

        # ── Footer buttons ────────────────────────────────────────────────────
        def _save():

            data = {}

            for sec, fields in entries.items():

                data[sec] = {}

                for fname, widget in fields.items():

                    try:
                        data[sec][fname] = widget.get()

                    except Exception:

                        data[sec][fname] = ""

            data["Product Rules"] = {
                "_table": [r.copy() for r in table_rows]
            }

            data["Communication Devices"] = {
                "_table": [r.copy() for r in device_rows]
            }

            if "Product Matrix Mapping" in entries:

                data["Product Matrix Mapping"] = {}

                for fname, widget in entries["Product Matrix Mapping"].items():

                    try:
                        data["Product Matrix Mapping"][fname] = widget.get()

                    except:

                        data["Product Matrix Mapping"][fname] = ""

            if "SN Chassis Mapping" in entries:

                data["SN Chassis Mapping"] = {}

                for fname, widget in entries["SN Chassis Mapping"].items():

                    try:

                        data["SN Chassis Mapping"][fname] = widget.get()

                    except:

                        data["SN Chassis Mapping"][fname] = ""
                        
            self.save_setting(data)

            # ====================================
            # RELOAD MAIN FORM COMMUNICATION
            # ====================================

            try:

                parent.reload_comm_devices()
                parent.update_comm_status()

            except Exception as e:

                print(
                    "Reload Comm Error:",
                    e
                )

            messagebox.showinfo(
                "Success",
                "Setting saved successfully",
                parent=dlg
            )

        btn_frame = ctk.CTkFrame(footer, fg_color="transparent")
        btn_frame.pack(side="right", padx=15, pady=10)

        ctk.CTkButton(
            btn_frame, text="SAVE", width=110, height=34,
            fg_color=SUCCESS, hover_color="#059669",
            text_color="#052E16", font=("Segoe UI", 11, "bold"),
            command=_save
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame, text="CANCEL", width=110, height=34,
            fg_color="#374151", hover_color="#1F2937",
            text_color=TEXT, font=("Segoe UI", 11, "bold"),
            command=dlg.destroy
        ).pack(side="left", padx=5)

        dlg.update()


# =============================================================================
# STANDALONE TEST
# =============================================================================
if __name__ == "__main__":
    root = ctk.CTk()
    root.geometry("400x300")
    root.configure(fg_color="#0F172A")

    ctk.CTkButton(
        root,
        text="Open Setting",
        command=lambda: SettingForm().show(root),
        fg_color="#10B981"
    ).pack(expand=True)

    root.mainloop()