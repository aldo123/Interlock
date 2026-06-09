    
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import json
import os

CARD_BG = "#0F172A"
TEXT = "#F8FAFC"
BORDER = "#22364A"
SUCCESS = "#10B981"


    # =====================================================
    # INTERLOCK JSON
    # =====================================================
class InterlockForm:
    
    def __init__(self):
        pass

    def get_interlock_path(self):
        return os.path.join(
            os.path.dirname(__file__),
            "interlock.json"
        )

    def load_interlock(self):

        default = {

            "Control Point": {
                "Control Point Code": "BM01-VM01-CP20",
                "Control Point Family": "CP20 V-Mini",
                "Control Point Name": "CP20 - Pallet Label Printing",
                "Data Point": "CP20 V-Mini",
                "Interlock ByPass": "No",
                "Process": ""
            },

            "Documents": {
                "Max Document Size": "10485760"
            },

            "Tester": {
                "Max Retest Number": "1"
            },

            "Traceability Server": {
                "Database Server": "10.4.18.50",
                "TraceabilityCatalog": "traceability",
                "TraceabilityPassword": "************",
                "TraceabilitySslMode": "REQUIRED",
                "TraceabilityUserId": "cp2"
            }
        }

        path = self.get_interlock_path()

        try:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except:
            pass

        return default


    def save_interlock(self,data):

        path = self.get_interlock_path()

        with open(path, "w", encoding="utf-8") as f:
            json.dump(
                data,
                f,
                indent=4
            )
            
    def show(self, parent):
        

        dlg = ctk.CTkToplevel(parent)
        dlg.title("Interlock Setting")
        dlg.geometry("540x480")
        dlg.transient(parent)
        dlg.grab_set()

        container = ctk.CTkFrame(dlg, fg_color=CARD_BG, corner_radius=8, border_width=1, border_color=BORDER)
        container.pack(expand=True, fill="both", padx=12, pady=12)

        content_frame = ctk.CTkFrame(container, fg_color="transparent")
        content_frame.pack(fill="both", expand=True)
        footer = ctk.CTkFrame(
            container,
            height=60,
            fg_color=CARD_BG,
            border_width=1,
            border_color=BORDER
        )

        footer.pack(
            side="bottom",
            fill="x"
        )

        footer.pack_propagate(False)

        scroll_canvas = tk.Canvas(content_frame, bg=CARD_BG, highlightthickness=0)
        vscroll = tk.Scrollbar(content_frame, orient="vertical", command=scroll_canvas.yview)
        scroll_canvas.configure(yscrollcommand=vscroll.set)
        vscroll.pack(side="right", fill="y")
        scroll_canvas.pack(side="left", fill="both", expand=True)

        inner = ctk.CTkFrame(scroll_canvas, fg_color="transparent")
        window_id = scroll_canvas.create_window((0, 0), window=inner, anchor="nw")

        def _on_inner_config(event):
            scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all"))

        def _on_canvas_config(event):
            try:
                scroll_canvas.itemconfig(window_id, width=event.width)
            except Exception:
                pass

        inner.bind("<Configure>", _on_inner_config)
        scroll_canvas.bind("<Configure>", _on_canvas_config)

        def _on_mousewheel(event):
            scroll_canvas.yview_scroll(int(-1 * (event.delta / 120)), 'units')

        dlg.bind("<Destroy>",
            lambda e:
            scroll_canvas.unbind_all("<MouseWheel>")
        )

        header = ctk.CTkFrame(inner, fg_color="transparent")
        header.pack(fill="x", padx=8, pady=(8, 6))
        ctk.CTkLabel(header, text="Interlock Setting", font=("Segoe UI", 13, "bold"), text_color=TEXT).pack(anchor="w")

        sections = self.load_interlock()

        interlock_entries = {}

        for section_name, rows in sections.items():

            title_frame = ctk.CTkFrame(
                inner,
                fg_color="#18202D"
            )

            title_frame.pack(
                fill="x",
                padx=10,
                pady=(8,0)
            )

            ctk.CTkLabel(
                title_frame,
                text=section_name,
                font=("Segoe UI", 15, "bold"),
                text_color=TEXT
            ).pack(
                anchor="w",
                padx=10,
                pady=5
            )

            table = ctk.CTkFrame(
                inner,
                fg_color=CARD_BG,
                border_width=1,
                border_color=BORDER
            )

            table.pack(
                fill="x",
                padx=10,
                pady=(0,5)
            )

            table.grid_columnconfigure(0, weight=0)
            table.grid_columnconfigure(1, weight=0)

            for row_index, (label, value) in enumerate(rows.items()):

                lbl = ctk.CTkLabel(
                    table,
                    text=label,
                    anchor="w",
                    text_color=TEXT
                )

                lbl.grid(
                    row=row_index,
                    column=0,
                    sticky="ew",
                    padx=10,
                    pady=6
                )

                if label == "Interlock ByPass":

                    entry = ctk.CTkOptionMenu(
                        table,
                        values=["Yes", "No"],
                        width=280
                    )

                    entry.set(value)

                else:

                    entry = ctk.CTkEntry(
                        table,
                        width=280,
                        fg_color="#172132",
                        border_color="#334155",
                        text_color=TEXT
                    )

                    entry.insert(0, value)

                interlock_entries.setdefault(
                    section_name,
                    {}
                )

                interlock_entries[section_name][label] = entry

                entry.grid(
                    row=row_index,
                    column=1,
                    sticky="w",
                    padx=10,
                    pady=6
                )

                

        def save_interlock():
            data = {}

            for section_name, fields in interlock_entries.items():

                data[section_name] = {}

                for field_name, entry_widget in fields.items():

                    try:
                        data[section_name][field_name] = entry_widget.get()
                    except:
                        data[section_name][field_name] = ""

            self.save_interlock(data)

            try:

                if hasattr(parent, "db"):
                    parent.db.reload()

                if hasattr(parent, "update_database_status"):
                    parent.update_database_status()

            except Exception as e:

                print(
                    "Reload Database Error:",
                    e
                )

            messagebox.showinfo(
                "Success",
                "Interlock saved successfully"
            )

        btn_frame = ctk.CTkFrame(
            footer,
            fg_color="transparent"
        )

        btn_frame.pack(
            side="right",
            padx=15,
            pady=10
        )

        ctk.CTkButton(
            btn_frame,
            text="Save",
            width=120,
            command=save_interlock,
            fg_color=SUCCESS
        ).pack(
            side="left",
            padx=5
        )

        ctk.CTkButton(
            btn_frame,
            text="Close",
            width=120,
            command=dlg.destroy,
            fg_color="#374151"
        ).pack(
            side="left",
            padx=5
        )

        dlg.update()
