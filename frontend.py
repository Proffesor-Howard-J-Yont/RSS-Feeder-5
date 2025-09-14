# FRONTEND.PY

# Before importing libraries, a loading screen is shown
from customtkinter import CTk, CTkLabel, CTkFrame, CTkProgressBar, set_appearance_mode, set_default_color_theme

# Set appearance mode and color theme
set_appearance_mode("Light") # System, Dark, Light
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
loading_progress = CTkProgressBar(loading_frame, mode="determinate", width=200)
loading_progress.pack(pady=15, padx=15, fill="x")


loading_progress.start()
root.update()
# Import other modules after setting up the loading screen
from customtkinter import *
from PIL import Image

topbgimage = CTkImage(light_image=Image.open('assets/home_img.png'), dark_image=Image.open('assets/home_img.png'), size=(1500, 300))

# ------------- Setup Complete -----------------
loading_progress.stop()
loading_frame.destroy()  # Remove the loading screen

# ------------- Functions -----------------
def clear_board():
    for widget in mainframe.winfo_children():
        widget.destroy()
    
def home():
    clear_board()

    # --------- Top Bar -------------
    top_frame = CTkFrame(mainframe, corner_radius=0, height=200)
    top_frame.pack(fill='x')

    homeL = CTkLabel(top_frame, text='Home', image=topbgimage, font=('Calibri', 70, 'bold'), justify='left', text_color='white')
    homeL.pack(fill='x', expand=True)

    # --------- Suggested Podcast Bar -------------
    suggested_frame = CTkFrame(mainframe, corner_radius=20, height=150)
    suggested_frame.pack(fill='x', pady=10)

    suggestedL = CTkLabel(suggested_frame, text='For You', font=('Calibri', 30, 'bold'), justify='left')
    suggestedL.grid(row=0, column=0, padx=20, pady=10)

    # NEW FEED BUTTON
    newfeedimage = CTkImage(light_image=Image.open('assets/plus_light.png'), dark_image=Image.open('assets/plus_dark.png'), size=(120, 120))
    newfeed_button = CTkButton(suggested_frame, text='New Feed', width=150, height=150, fg_color='transparent', hover_color='gray25', font=('Calibri', 15, 'bold'), image=newfeedimage, compound='top')
    newfeed_button.grid(row=1, column=0, padx=20, pady=10)


root_color = root.cget("fg_color")
mainframe = CTkScrollableFrame(root, fg_color=root_color)
mainframe.pack(fill='both', expand=True)

home()
# ------------------------------------------
root.mainloop()
