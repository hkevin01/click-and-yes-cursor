"""
Simple GUI for configuration using Tkinter.
"""
import tkinter as tk
import json
import os


def save_config(x, y, message):
    config = {"coordinates": {"x": x, "y": y}, "message": message}
    with open(os.path.join(os.path.dirname(__file__), '../src/config.json'), 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4)


def launch_gui():
    root = tk.Tk()
    root.title("Click & Yes Cursor Config")

    tk.Label(root, text="X:").grid(row=0, column=0)
    x_entry = tk.Entry(root)
    x_entry.grid(row=0, column=1)

    tk.Label(root, text="Y:").grid(row=1, column=0)
    y_entry = tk.Entry(root)
    y_entry.grid(row=1, column=1)

    tk.Label(root, text="Message:").grid(row=2, column=0)
    msg_entry = tk.Entry(root)
    msg_entry.grid(row=2, column=1)

    def on_save():
        save_config(int(x_entry.get()), int(y_entry.get()), msg_entry.get())
        root.destroy()

    tk.Button(root, text="Save", command=on_save).grid(row=3, columnspan=2)
    root.mainloop()

if __name__ == "__main__":
    launch_gui()
