import tkinter as tk
from AssemblyEditor import AssemblyEditor

if __name__ == "__main__":
    root = tk.Tk()
    editor = AssemblyEditor(root)
    root.mainloop()