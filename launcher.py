#!/bin/python3
import tkinter as tk

def launcher() -> None:
    window = tk.Tk()
    window.title("Touhou Launcher")
    title = tk.Label(text="Launch Options", width=25, height=3, font=("Arial", 25))
    title.pack()

    close_on_launch = tk.BooleanVar()
    close_on_launch_button = tk.Checkbutton(text="Close launcher on launch", variable=close_on_launch, onvalue=True, offvalue=False)
    close_on_launch_button.pack()

    def launch_game() -> None:
        import subprocess
        if close_on_launch.get():
            window.destroy()
        subprocess.run(["./main.py", resolution.get()])

    launch_button = tk.Button(
        text="Launch Game",
        width=25,
        height=5,
        bg="white",
        fg="black",
        command=launch_game
    )
    launch_button.pack()
    
    resolution = tk.StringVar(value="windowed")
    command = lambda: print(resolution.get())
    resolution_option_fullscreen = tk.Radiobutton(
        text="Fullscreen", variable=resolution, value="fullscreen", command=command
    )

    resolution_option_windowed = tk.Radiobutton(
        text="Windowed (640x480)", variable=resolution, value="windowed", command=command
    )

    resolution_option_fullscreen.pack()
    resolution_option_windowed.pack()

    window.mainloop()


if __name__ == "__main__":
    launcher()