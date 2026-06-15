import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image
from datetime import datetime
from interlockform import InterlockForm
from settingform import SettingForm
import json
import os
from cp2 import CP2Page
from reference import ReferencePage
from snlist import SNListPage
import time
from manuallogin import ManualLoginDialog
from database import DatabaseManager
from maintenance import MaintenancePage
from maintenance import MaintenanceDB

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
        self.db = DatabaseManager()
        self.db.connect()
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
        self.active_menu = "Main"
        self.menu_buttons = {}
        self.content_frame = None

        self.load_cp_from_json()
        self.machine_status = "IDLE"
        self.last_move_success = None
        self.downtime_active = False
        self.downtime_start = None
        self.downtime_id = None

        self._build_header()
        self._build_body()
        self.refresh_permissions()
        self.after(1000, self.update_machine_status)
        

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
        self.lbl_cp_title = ctk.CTkLabel(
            center,
            text=self.cp_family,
            font=("Segoe UI", 22, "bold"),
            text_color=SUCCESS
        )

        self.lbl_cp_title.pack()
        ctk.CTkLabel(center, text="Monday, June 08, 2026  8:45:21 AM  WW24",
                     font=("Segoe UI", 10), text_color=TEXT2).pack()

        # ── Right: codes + user ───────────────────────────────────
        right = ctk.CTkFrame(hdr, fg_color="transparent")
        right.pack(side="right", padx=18)

        user = ctk.CTkFrame(right, fg_color="transparent")
        user.pack(side="right", padx=(20, 0))

        # ── Downtime Button ─────────────────────────────
        # Machine Status + Downtime
        status_frame = ctk.CTkFrame(
            right,
            fg_color="transparent"
        )

        status_frame.pack(
            side="right",
            padx=(60,20)
        )

        self.lbl_machine_status = ctk.CTkLabel(
            status_frame,
            text="⚪ IDLE",
            font=("Segoe UI", 11, "bold"),
            text_color="#CBD5E1"
        )

        self.lbl_machine_status.pack(
            pady=(0,4)
        )

        self.btn_downtime = ctk.CTkButton(
            status_frame,
            text="⏸ Downtime",
            width=140,
            height=32,
            fg_color="#DC2626",
            hover_color="#B91C1C",
            text_color="white",
            font=("Segoe UI", 11, "bold"),
            corner_radius=6,
            command=self.open_downtime
        )

        self.btn_downtime.pack()

        self.gear_btn = ctk.CTkButton(
            user,
            text="🔧",
            width=36,
            height=36,
            fg_color="transparent",
            hover_color="#2563EB",
            text_color=TEXT,
            font=("Segoe UI", 16),
            corner_radius=18,
            command=self.show_setting_menu
        )

        self.gear_btn.pack(
            side="left",
            padx=(0, 8)
        )
        user_btn = ctk.CTkButton(
            user,
            text="👤",
            width=36,
            height=36,
            fg_color="transparent",
            hover_color="#2563EB",
            text_color=TEXT,
            font=("Segoe UI", 16),
            corner_radius=18,
            command=self.show_user_menu
        )

        user_btn.pack(
            side="left",
            padx=(0, 8)
        )
        username = self.user.get("username", "Guest")
        role = self.user.get("role", "")

        self.lbl_user = ctk.CTkLabel(
            user,
            text=f"{username}\n{role}",
            font=("Segoe UI", 10),
            text_color=TEXT2,
            justify="left"
        )

        self.lbl_user.pack(side="left")

        codes = ctk.CTkFrame(right, fg_color="transparent")
        codes.pack(side="right")
        self.lbl_line_code = ctk.CTkLabel(
            codes,
            text=f"Line Code : {self.cp_code}",
            font=("Segoe UI",10),
            text_color=TEXT2
        )

        self.lbl_line_code.pack(anchor="e")
        self.lbl_spec_code = ctk.CTkLabel(
            codes,
            text=f"Spec Code : {self.cp_family}",
            font=("Segoe UI",10),
            text_color=TEXT2
        )

        self.lbl_spec_code.pack(anchor="e")

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
            text="🔧 Interlock",
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

        self.body = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        self.body.pack(
            fill="both",
            expand=True
        )

        self._build_sidebar(self.body)

        

        self.content_frame = ctk.CTkFrame(
            self.body,
            fg_color=BG
        )

        self.content_frame.pack(
            side="left",
            fill="both",
            expand=True
        )

        self._build_main_content(
            self.content_frame
        )

    # =========================================================================
    # SIDEBAR
    # =========================================================================
    def _build_sidebar(self, parent):
        sidebar = ctk.CTkFrame(parent, fg_color=HDR_BG, width=130, corner_radius=0)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        menu_items = [
            ("Main", self.show_main),
            ("Maintenance", self.show_maintenance),
            ("SN List", self.show_sn_list),
            ("Reference", self.show_reference)
        ]

        for text, cmd in menu_items:

            btn = ctk.CTkButton(
                sidebar,
                text=text,
                width=120,
                height=34,
                fg_color="transparent",
                hover_color=CARD_BG,
                text_color=TEXT2,
                anchor="w",
                font=("Segoe UI", 11),
                corner_radius=0,
                command=lambda t=text, c=cmd: self.change_menu(t, c)
            )

            btn.pack(
                padx=4,
                pady=2,
                anchor="w"
            )

            self.menu_buttons[text] = btn

        self.menu_buttons["Main"].configure(
            fg_color="#16A34A",
            text_color="white"
        )

    def change_menu(self, menu_name, callback):

        self.active_menu = menu_name

        for name, btn in self.menu_buttons.items():

            if name == menu_name:

                btn.configure(
                    fg_color="#16A34A",
                    text_color="white"
                )

            else:

                btn.configure(
                    fg_color="transparent",
                    text_color=TEXT2
                )

        callback()


    def clear_content(self):

        if self.content_frame is not None:
            self.content_frame.destroy()
            self.content_frame = None
            
    def show_main(self):

        self.clear_content()

        self.content_frame = ctk.CTkFrame(
            self.body,
            fg_color=BG
        )

        self.content_frame.pack(
            side="left",
            fill="both",
            expand=True
        )

        self._build_main_content(
            self.content_frame
        )
    

    def show_maintenance(self):

        self.clear_content()

        self.content_frame = ctk.CTkFrame(
            self.body,
            fg_color=BG
        )

        self.content_frame.pack(
            side="left",
            fill="both",
            expand=True
        )

        self.maintenance_page = MaintenancePage(
            self.content_frame,
            user=self.user,
            main_form=self
        )

        self.maintenance_page.pack(
            fill="both",
            expand=True
        )

    def show_sn_list(self):

        self.clear_content()

        self.content_frame = ctk.CTkFrame(
            self.body,
            fg_color=BG
        )

        self.content_frame.pack(
            side="left",
            fill="both",
            expand=True
        )

        SNListPage(
            self.content_frame,
            self
        )

    def show_reference(self):

        self.clear_content()

        self.content_frame = ctk.CTkFrame(
            self.body,
            fg_color=BG
        )

        self.content_frame.pack(
            side="left",
            fill="both",
            expand=True
        )

        ReferencePage(
            self.content_frame,
            self
        )
    
    def load_cp_from_json(self):

        self.cp_code = "BW01-VM2"
        self.cp_family = "CP02-PCBAVM2"
        self.cp_name = "CP02-PCBAVM2"

        try:

            path = os.path.join(
                os.path.dirname(__file__),
                "interlock.json"
            )

            if not os.path.exists(path):
                return

            with open(
                path,
                "r",
                encoding="utf-8"
            ) as f:

                data = json.load(f)

            cp = data.get("Control Point", {})

            self.cp_code = cp.get(
                "Control Point Code",
                self.cp_code
            )

            self.cp_family = cp.get(
                "Control Point Family",
                self.cp_family
            )

            self.cp_name = cp.get(
                "Control Point Name",
                self.cp_name
            )

            self.process_no = cp.get(
                "Process",
                "1"
            )

        except Exception as e:

            print(
                "CP LOAD ERROR:",
                e
            )

    def refresh_cp_header(self):

        self.load_cp_from_json()

        self.lbl_cp_title.configure(
            text=self.cp_family
        )

        self.lbl_line_code.configure(
            text=f"Line Code : {self.cp_code}"
        )

        self.lbl_spec_code.configure(
            text=f"Spec Code : {self.cp_family}"
        )

    def update_machine_status(self):

        # Downtime override
        if self.machine_status == "MACHINE DOWN":
            self.after(1000, self.update_machine_status)
            return

        if self.machine_status == "WAITING MATERIAL":
            self.after(1000, self.update_machine_status)
            return

        # Belum pernah move success
        if self.last_move_success is None:

            self.machine_status = "IDLE"

            self.lbl_machine_status.configure(
                text="⚪ IDLE",
                text_color="#CBD5E1"
            )

            self.after(1000, self.update_machine_status)
            return

        elapsed = time.time() - self.last_move_success

        if elapsed < 60:

            self.machine_status = "RUNNING"

            self.lbl_machine_status.configure(
                text="🟢 RUNNING",
                text_color="#22C55E"
            )

        else:

            self.machine_status = "IDLE"

            self.lbl_machine_status.configure(
                text="⚪ IDLE",
                text_color="#CBD5E1"
            )

        self.after(1000, self.update_machine_status)
    
    def open_downtime(self):

        popup = ctk.CTkToplevel(self)
        popup.title("Downtime Selection")
        popup_width = 520
        popup_height = 250

        self.update_idletasks()

        x = self.winfo_x() + (self.winfo_width() // 2) - (popup_width // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (popup_height // 2)

        popup.geometry(f"{popup_width}x{popup_height}+{x}+{y}")
        popup.resizable(False, False)
        popup.grab_set()

        popup.configure(fg_color="#0F172A")

        ctk.CTkLabel(
            popup,
            text="SELECT DOWNTIME TYPE",
            font=("Segoe UI", 20, "bold"),
            text_color="#22C55E"
        ).pack(pady=(25, 10))

        ctk.CTkLabel(
            popup,
            text="Please choose downtime category",
            font=("Segoe UI", 11),
            text_color="#94A3B8"
        ).pack(pady=(0, 20))

        button_frame = ctk.CTkFrame(
            popup,
            fg_color="transparent"
        )
        button_frame.pack(
            pady=25,
            padx=20,
            fill="x"
        )

        ctk.CTkButton(
            button_frame,
            text="🔧\nCALL MAINTENANCE",
            width=180,
            height=100,
            fg_color="#DC2626",
            hover_color="#B91C1C",
            font=("Segoe UI", 14, "bold"),
            command=lambda: self.call_maintenance(popup)
        ).pack(
            side="left",
            expand=True,
            padx=(0,10)
        )

        ctk.CTkButton(
            button_frame,
            text="📦\nWAITING MATERIAL",
            width=180,
            height=100,
            fg_color="#F59E0B",
            hover_color="#D97706",
            font=("Segoe UI", 14, "bold"),
            command=lambda: self.waiting_material(popup)
        ).pack(
            side="left",
            expand=True,
            padx=(10,0)
        )

    def call_maintenance(self, popup):

        self.machine_status = "MACHINE DOWN"

        self.downtime_active = True
        self.downtime_start = datetime.now()

        self.downtime_id = (
            f"DT-{self.downtime_start.strftime('%Y%m%d%H%M%S')}"
        )

        db = MaintenanceDB()

        db.insert_downtime({
            "downtime_id": self.downtime_id,
            "start_time": self.downtime_start.strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": None,
            "duration": None,
            "downtime_type": None,
            "root_cause": None,
            "corrective_action": None,
            "technician": self.user.get("username",""),
            "shift": "Shift A",
            "notes": None,
            "machine_code": self.cp_code
        })

        self.lbl_machine_status.configure(
            text="🔴 MACHINE DOWN",
            text_color="#EF4444"
        )

        popup.destroy()


    def waiting_material(self, popup):

        self.machine_status = "WAITING MATERIAL"

        self.lbl_machine_status.configure(
            text="🟡 WAITING MATERIAL",
            text_color="#F59E0B"
        )

        popup.destroy()
    
    def show_user_menu(self):

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
            text="User",
            font=("Segoe UI", 14, "bold"),
            text_color="#22C55E"
        ).pack(
            pady=(8,5)
        )

        ctk.CTkButton(
            frame,
            text="🔑 Change Password",
            anchor="w",
            height=36,
            fg_color="transparent",
            hover_color="#2563EB",
            command=lambda: [
                popup.destroy(),
                self.change_password()
            ]
        ).pack(
            fill="x",
            padx=10,
            pady=2
        )

        ctk.CTkButton(
            frame,
            text="🔄 Relogin",
            anchor="w",
            height=36,
            fg_color="transparent",
            hover_color="#2563EB",
            command=lambda: [
                popup.destroy(),
                self.relogin()
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
    
    def relogin(self):

        dlg = ManualLoginDialog(self)

        self.wait_window(dlg)

        username = getattr(dlg, "username", "").strip()
        password = getattr(dlg, "password", "").strip()
        card_id  = getattr(dlg, "card_id", "").strip()

        if not username and not password and not card_id:
            return

        user = None

        try:

            if card_id:

                sql = """
                    SELECT username, role, id_card
                    FROM users
                    WHERE id_card=%s
                    LIMIT 1
                """

                user = self.db.fetch_one(
                    sql,
                    (card_id,)
                )

            else:

                sql = """
                    SELECT username, role, id_card
                    FROM users
                    WHERE username=%s
                    AND password=%s
                    LIMIT 1
                """

                user = self.db.fetch_one(
                    sql,
                    (
                        username,
                        password
                    )
                )

            if not user:

                messagebox.showerror(
                    "Login Failed",
                    "Invalid Username / Password / Card ID"
                )

                return

            self.user = user

            self.refresh_user_info()
            self.refresh_permissions()

            messagebox.showinfo(
                "Success",
                f"Login as {user['username']}"
            )

        except Exception as e:

            messagebox.showerror(
                "Database Error",
                str(e)
            )

    def change_password(self):

        popup = ctk.CTkToplevel(self)

         # Hilangkan title bar Windows
        popup.overrideredirect(True)

        popup.grab_set()
        popup.lift()
        popup.focus_force()

        W = 420
        H = 240

        px = self.winfo_rootx() + (self.winfo_width() - W) // 2
        py = self.winfo_rooty() + (self.winfo_height() - H) // 2

        popup.geometry(f"{W}x{H}+{px}+{py}")

        popup.configure(
            fg_color="#0F172A"
        )

        card = ctk.CTkFrame(
            popup,
            fg_color="#111827",
            border_width=1,
            border_color="#22C55E",
            corner_radius=12
        )

        card.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        ctk.CTkLabel(
            card,
            text="Change Password",
            font=("Segoe UI",18,"bold"),
            text_color="#22C55E"
        ).pack(
            pady=(20,15)
        )

        new_pwd = ctk.CTkEntry(
            card,
            placeholder_text="New Password",
            height=40,
            show="*"
        )

        new_pwd.pack(
            fill="x",
            padx=25
        )

        def save_password():

            password = new_pwd.get().strip()

            if not password:

                messagebox.showwarning(
                    "Warning",
                    "Please enter new password"
                )

                return

            username = self.user.get("username")

            try:

                sql = """
                    UPDATE users
                    SET password=%s
                    WHERE username=%s
                """

                cursor = self.db.conn.cursor()

                cursor.execute(
                    sql,
                    (
                        password,
                        username
                    )
                )

                self.db.conn.commit()

                cursor.close()
                popup.destroy()
                messagebox.showinfo(
                    "Success",
                    "Password updated successfully"
                )

                

            except Exception as e:

                messagebox.showerror(
                    "Database Error",
                    str(e)
                )

        btn_frame = ctk.CTkFrame(
            card,
            fg_color="transparent"
        )

        btn_frame.pack(
            fill="x",
            padx=25,
            pady=20
        )

        ctk.CTkButton(
            btn_frame,
            text="Close",
            fg_color="#374151",
            command=popup.destroy
        ).pack(
            side="left",
            expand=True,
            fill="x",
            padx=(0,5)
        )

        ctk.CTkButton(
            btn_frame,
            text="Save",
            fg_color="#22C55E",
            text_color="black",
            command=save_password
        ).pack(
            side="left",
            expand=True,
            fill="x",
            padx=(5,0)
        )
    
    def refresh_user_info(self):

        username = self.user.get("username", "Guest")
        role = self.user.get("role", "")

        self.lbl_user.configure(
            text=f"{username}\n{role}"
        )
    
    def refresh_permissions(self):

        role = str(
            self.user.get("role", "")
        ).upper()

        is_engineer = role == "ENGINEER"

        # Maintenance
        if "Maintenance" in self.menu_buttons:

            self.menu_buttons["Maintenance"].configure(
                state="normal" if is_engineer else "disabled"
            )

        # Reference
        if "Reference" in self.menu_buttons:

            self.menu_buttons["Reference"].configure(
                state="normal" if is_engineer else "disabled"
            )

        # Setting Icon
        if hasattr(self, "gear_btn"):

            self.gear_btn.configure(
                state="normal" if is_engineer else "disabled"
            )
    
    # =========================================================================
    # MAIN CONTENT
    # =========================================================================
    def _build_main_content(self, parent):

        container = ctk.CTkFrame(
            parent,
            fg_color=BG
        )

        container.pack(
            fill="both",
            expand=True
        )

        # LEFT CONTENT
        left_content = ctk.CTkFrame(
            container,
            fg_color=BG
        )

        left_content.pack(
            side="left",
            fill="both",
            expand=True
        )

        # RIGHT PANEL
        self._build_right_panel(container)

        process = str(self.process_no)

        if process == "2":
            CP2Page(left_content, self)

        elif process == "3":
            from cp3 import CP3Page
            CP3Page(left_content, self)

        else:
            ctk.CTkLabel(
                left_content,
                text=f"PROCESS {process} NOT FOUND"
            ).pack(expand=True)
    
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
        style.theme_use("clam")   # ← satu-satunya tempat yang boleh panggil ini

        style.configure("Rep.Treeview",
                        background="#172132", fieldbackground="#172132",
                        foreground=TEXT, rowheight=28,
                        font=("Segoe UI", 10))
        style.configure("Rep.Treeview.Heading",
                        background="#1E3A5F", foreground=TEXT,
                        font=("Segoe UI", 10, "bold"), relief="flat")
        style.map("Rep.Treeview",
                background=[("selected", "#2563EB"), ("!selected", "#172132")],
                foreground=[("selected", "#FFFFFF"), ("!selected", TEXT)])
        style.map("Rep.Treeview.Heading",
                background=[("active", "#1E3A5F"), ("!active", "#1E293B")])
        
        
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
