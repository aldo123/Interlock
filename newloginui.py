import customtkinter as ctk
from PIL import Image
from datetime import datetime
import tkinter as tk

from interlockform import InterlockForm
from database import DatabaseManager


# ==========================================================
# CONFIG
# ==========================================================
WIDTH = 1400
HEIGHT = 720

GREEN = "#22C55E"
LIGHT_GREEN = "#3CB371"
BG = "#F4F4F4"
TEXT = "#333333"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")


class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        #self.overrideredirect(True)

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        x = int((screen_width - WIDTH) / 2)
        y = int((screen_height - HEIGHT) / 2)

        self.geometry(f"{WIDTH}x{HEIGHT}+{x}+{y}")

        self.configure(fg_color="#0F172A")
        self.login_mode = "card"
        self.db = DatabaseManager()
        self.db.connect()
        self.build_ui()
        self.update_clock()
        self.loading_percent = 0
        self.animate_loading()

    # ======================================================
    # UI
    # ======================================================
    def build_ui(self):

        # MAIN
        self.main = ctk.CTkFrame(
            self,
            fg_color="white",
            corner_radius=0
        )
        self.main.pack(fill="both", expand=True)

        # ==================================================
        # LEFT IMAGE PANEL
        # ==================================================
        self.left_panel = ctk.CTkFrame(
            self.main,
            fg_color="white",
            corner_radius=0
        )
        self.left_panel.pack(
            side="left",
            fill="both",
            expand=True
        )

        try:

            img = Image.open("factory.png")

            self.bg_image = ctk.CTkImage(
                light_image=img,
                dark_image=img,
                size=(980, 700)
            )

            self.image_label = ctk.CTkLabel(
                self.left_panel,
                image=self.bg_image,
                text=""
            )

            self.image_label.pack(
                fill="both",
                expand=True,
                padx=(8, 0),
                pady=(8, 0)
            )

        except Exception as e:

            self.image_label = ctk.CTkLabel(
                self.left_panel,
                text=f"Image not found\n{e}",
                font=("Segoe UI", 24, "bold")
            )

            self.image_label.pack(expand=True)

        # ==================================================
        # RIGHT LOGIN PANEL
        # ==================================================
        self.right_panel = ctk.CTkFrame(
            self.main,
            width=420,
            fg_color="#111827",
            corner_radius=0
        )
        self.right_panel.pack(
            side="right",
            fill="y"
        )
        self.right_panel.pack_propagate(False)

        # CLOSE BUTTON
        self.close_btn = ctk.CTkButton(
            self.right_panel,
            text="✖",
            width=30,
            height=30,
            fg_color="transparent",
            hover_color="#EEEEEE",
            text_color="red",
            command=self.destroy
        )
        self.close_btn.pack(
            anchor="ne",
            padx=10,
            pady=10
        )

        # ==================================================
        # LOGO
        # ==================================================
        logo_frame = ctk.CTkFrame(
            self.right_panel,
            fg_color="transparent"
        )
        logo_frame.pack(
            pady=(10, 0)
        )

        ctk.CTkLabel(
            logo_frame,
            text="WIK",
            font=("Segoe UI", 42, "bold"),
            text_color=GREEN
        ).pack()

        ctk.CTkLabel(
            logo_frame,
            text="Technology\nattuned to Nature",
            font=("Segoe UI", 18),
            justify="center",
            text_color="#FFFFFF"
        ).pack()

        ctk.CTkLabel(
            logo_frame,
            text="EE - Interlock & Traceability",
            font=("Segoe UI", 22, "bold"),
            text_color="#FFFFFF"
        ).pack(pady=(10, 30))

        # ==================================================
        # TABS
        # ==================================================
        tab_frame = ctk.CTkFrame(
            self.right_panel,
            fg_color="transparent"
        )
        tab_frame.pack(fill="x", padx=40)

        self.card_tab = ctk.CTkButton(
            tab_frame,
            text="Card Number",
            fg_color="transparent",
            hover=False,
            text_color=GREEN,
            width=80,
            command=lambda: self.switch_mode("card")
        )

        self.card_tab.pack(side="left")

        self.pass_tab = ctk.CTkButton(
            tab_frame,
            text="Password",
            fg_color="transparent",
            hover=False,
            text_color="gray",
            width=80,
            command=lambda: self.switch_mode("password")
        )

        self.pass_tab.pack(side="left", padx=20)

        line = ctk.CTkFrame(
            self.right_panel,
            height=2,
            fg_color=GREEN
        )
        line.pack(
            fill="x",
            padx=40,
            pady=(5, 20)
        )

        self.login_frame = ctk.CTkFrame(
            self.right_panel,
            fg_color="transparent"
        )

        self.login_frame.pack(
            fill="x",
            padx=40,
            pady=(10,10)
        )

        self.card_entry = ctk.CTkEntry(
            self.login_frame,
            height=40,
            placeholder_text="Scan Card Number",
            corner_radius=5,
            border_color="#7FA67F"
        )

        self.card_entry.bind(
            "<Return>",
            self.card_login
        )

        self.username_entry = ctk.CTkEntry(
            self.login_frame,
            height=40,
            placeholder_text="Username",
            corner_radius=5,
            border_color="#7FA67F"
        )

        self.password_entry = ctk.CTkEntry(
            self.login_frame,
            height=40,
            show="*",
            placeholder_text="Password",
            corner_radius=5,
            border_color="#7FA67F"
        )

        self.password_entry.bind(
            "<Return>",
            lambda e: self.login()
        )


        # ==================================================
        # LOGIN BUTTON
        # ==================================================
        self.login_btn = ctk.CTkButton(
            self.right_panel,
            text="LOGIN",
            height=45,
            fg_color=GREEN,
            hover_color="#09592F",
            font=("Segoe UI", 15, "bold"),
            state="disabled",
            command=self.login
        )

        self.login_btn.pack(
            fill="x",
            padx=40,
            pady=30
        )

        # CLOCK
        self.clock_label = ctk.CTkLabel(
            self.right_panel,
            text="",
            font=("Segoe UI", 12)
        )
        self.clock_label.pack(
            pady=10
        )

        # PUSH BOTTOM
        spacer = ctk.CTkFrame(
            self.right_panel,
            fg_color="transparent"
        )
        spacer.pack(
            fill="both",
            expand=True
        )


        # ==========================================
        # FOOTER INFO
        # ==========================================

        footer_frame = ctk.CTkFrame(
            self.right_panel,
            fg_color="transparent"
        )

        footer_frame.place(
            relx=0.05,
            rely=0.965,
            relwidth=0.90,
            anchor="sw"
        )

        # VERSION
        self.version_label = ctk.CTkLabel(
            footer_frame,
            text="Version : 1.0.0.1008",
            font=("Segoe UI", 11),
            text_color="#FFFFFF"
        )

        self.version_label.pack(
            side="left",
            padx=(0, 20)
        )


        # DATABASE STATUS
        self.db_label = ctk.CTkLabel(
            footer_frame,
            text="● Database",
            font=("Segoe UI", 11, "bold")
        )

        self.db_label.pack(
            side="left",
            padx=(0, 20)
        )

        self.update_database_status()

        # SETTINGS BUTTON
        self.setting_btn = ctk.CTkButton(
            footer_frame,
            text="⚙",
            width=30,
            height=30,
            fg_color="transparent",
            hover_color="#1E293B",
            text_color="#94A3B8",
            font=("Segoe UI Symbol", 18),
            command=self.open_interlock_setting
        )

        self.setting_btn.pack(
            side="right"
        )
        


        # ==================================================
        # STATUS BAR
        # ==================================================
        # STATUS BAR (LEFT PANEL ONLY)

        status_container = ctk.CTkFrame(
            self.left_panel,
            fg_color="white",
            height=25,
            corner_radius=0
        )
        status_container.pack(
            side="bottom",
            fill="x"
        )

        status_container.pack_propagate(False)

        self.progress = ctk.CTkProgressBar(
            status_container,
            height=12,
            progress_color="#00C000",
            fg_color="#DCDCDC"
        )

        self.progress.pack(
            fill="x",
            padx=5,
            pady=(2, 0)
        )

        self.progress.set(0)

        self.loading_label = ctk.CTkLabel(
            status_container,
            text="Loading... 0%",
            text_color=GREEN,
            font=("Segoe UI", 10, "bold")
        )

        self.loading_label.pack(
            anchor="w",
            padx=8
        )

        self.switch_mode("card")

 
    # ======================================================
    # CLOCK
    # ======================================================
    def update_clock(self):

        now = datetime.now().strftime(
            "%A, %d %B %Y  %H:%M:%S"
        )

        self.clock_label.configure(text=now)

        self.clock_job = self.after(
            1000,
            self.update_clock
        )
    
    def update_database_status(self):

        try:

            if self.db.is_connected():

                self.db_label.configure(
                    text="● Database Connected",
                    text_color="#22C55E"
                )

            else:

                self.db_label.configure(
                    text="● Database Disconnected",
                    text_color="#EF4444"
                )

        except:

            self.db_label.configure(
                text="● Database Disconnected",
                text_color="#EF4444"
            )

    def animate_loading(self):

        if self.loading_percent <= 100:

            self.progress.set(self.loading_percent / 100)

            self.loading_label.configure(
                text=f"System Loading... {self.loading_percent}%"
            )

            self.loading_percent += 1

            self.loading_job = self.after(
                25,
                self.animate_loading
            )

        else:

            self.progress.set(1)

            self.loading_label.configure(
                text="✓ System Ready"
            )

            self.login_btn.configure(state="normal")

    def open_interlock_setting(self):

        try:

            interlock = InterlockForm()

            interlock.show(self)

        except Exception as e:

            print("Interlock Error:", e)

    def card_login(self, event=None):

        card_id = self.card_entry.get().strip()

        if not card_id:
            return

        sql = """
        SELECT
            username,
            role,
            id_card
        FROM users
        WHERE id_card = %s
        LIMIT 1
        """

        user = self.db.fetch_one(
            sql,
            (card_id,)
        )

        if user:

            self.open_main_ui(user)

        else:

            tk.messagebox.showerror(
                "Login Failed",
                "Card Number Not Registered"
            )

            self.card_entry.delete(0, "end")
    
    def login(self):

        if self.login_mode == "card":

            self.card_login()

        else:

            username = self.username_entry.get().strip()
            password = self.password_entry.get().strip()

            if not username or not password:

                tk.messagebox.showwarning(
                    "Warning",
                    "Please enter username and password"
                )

                return

            sql = """
            SELECT
                username,
                role,
                id_card
            FROM users
            WHERE username=%s
            AND password=%s
            LIMIT 1
            """

            user = self.db.fetch_one(
                sql,
                (username, password)
            )

            if user:

                self.open_main_ui(user)

            else:

                tk.messagebox.showerror(
                    "Login Failed",
                    "Invalid Username or Password"
                )

    def open_main_ui(self, user):

        self.after_cancel(self.clock_job)
        self.after_cancel(self.loading_job)
        from newmainform import NewMainForm
        self.withdraw()
        app = NewMainForm(user)
        app.mainloop()
            
    def switch_mode(self, mode):

        self.login_mode = mode

        self.card_entry.pack_forget()
        self.username_entry.pack_forget()
        self.password_entry.pack_forget()

        if mode == "card":

            self.card_tab.configure(
                text_color=GREEN
            )

            self.pass_tab.configure(
                text_color="gray"
            )

            self.card_entry.pack(
                fill="x"
            )

        else:

            self.card_tab.configure(
                text_color="gray"
            )

            self.pass_tab.configure(
                text_color=GREEN
            )

            self.username_entry.pack(
                fill="x",
                pady=(0,10)
            )

            self.password_entry.pack(
                fill="x"
            )

if __name__ == "__main__":
    app = LoginWindow()
    app.mainloop()