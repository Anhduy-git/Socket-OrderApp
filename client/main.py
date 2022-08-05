import tkinter as tk
from Constants import *
from ClientPages import HomePage



#Home page
if __name__ == "__main__":
    root = tk.Tk()

    canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT)
    canvas.pack()

    root.title("Home Page")
    HomePage(root).onCreate()

    root.mainloop()