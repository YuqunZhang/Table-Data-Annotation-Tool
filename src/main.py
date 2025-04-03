import tkinter as tk
from .gui import DataAnnotationApp
from .config import config

def main():
    root = tk.Tk()
    app = DataAnnotationApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()