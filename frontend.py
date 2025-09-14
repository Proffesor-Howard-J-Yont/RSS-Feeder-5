# FRONTEND.PY

# Before importing libraries, a loading screen is shown
from customtkinter import CTk, CTkLabel, CTkFrame, CTkProgressBar, set_appearance_mode, set_default_color_theme

# Set appearance mode and color theme
set_appearance_mode("Dark") # System, Dark, Light
set_default_color_theme("green") # green, dark-blue, blue

# Initialize the main application window
root = CTk()
root.title("RSS Feed Parser - 5th Generation")
root.geometry("800x600")

# Create a loading screen frame in the center of the window
loading_frame = CTkFrame(root)
loading_frame.place(relx=0.5, rely=0.5, anchor="center")

# Add a label to the loading screen
loading_label = CTkLabel(loading_frame, text="RSS Feed Parser", font=("Calibri", 45, 'bold'))
loading_label.pack(pady=15, padx=15)

# Subtitle label
subtitle_label = CTkLabel(loading_frame, text="5th Generation", font=("Calibri", 25))
subtitle_label.pack(pady=5, padx=15)

# Add a progress bar to the loading screen
loading_progress = CTkProgressBar(loading_frame, mode="indeterminate", width=200)
loading_progress.pack(pady=15, padx=15, fill="x")


loading_progress.start()
root.update()
# Import other modules after setting up the loading screen
from customtkinter import *
from PIL import Image


# ------------- Setup Complete -----------------
loading_progress.stop()
loading_frame.destroy()  # Remove the loading screen

# ------------- Set up GUI -----------------





# ------------------------------------------
root.mainloop()
