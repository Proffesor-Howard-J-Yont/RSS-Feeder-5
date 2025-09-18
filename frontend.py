# FRONTEND.PY

# Before importing libraries, a loading screen is shown
from customtkinter import CTk, CTkLabel, CTkFrame, CTkProgressBar, set_appearance_mode, set_default_color_theme

# Set appearance mode and color theme
set_appearance_mode("Dark") # System, Dark, Light
set_default_color_theme("green") # green, dark-blue, blue

# Initialize the main application window
root = CTk()
root.title("RSS Feed Parser - 5th Generation")
root.geometry("1200x800")

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
from CTkSeparator import CTkSeparator
import backend
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

    '''# --------- Suggested Podcast Bar -------------
    suggested_frame = CTkFrame(mainframe, corner_radius=20, height=150)
    suggested_frame.pack(fill='x', pady=10)

    suggestedL = CTkLabel(suggested_frame, text='For You', font=('Calibri', 30, 'bold'), justify='left')
    suggestedL.grid(row=0, column=0, padx=20, pady=10)

    # NEW FEED BUTTON
    newfeedimage = CTkImage(light_image=Image.open('assets/plus_light.png'), dark_image=Image.open('assets/plus_dark.png'), size=(120, 120))
    newfeed_button = CTkButton(suggested_frame, text='New Feed', width=150, height=150, text_color=('black', 'white'), fg_color='transparent', hover_color='gray25', font=('Calibri', 15, 'bold'), image=newfeedimage, compound='top')
    newfeed_button.grid(row=1, column=0, padx=20, pady=10)
'''

    headerL = CTkLabel(mainframe, text='Browse', font=('Calibri', 50, 'bold'), justify='left')
    headerL.pack(pady=40, padx=(70,0), anchor='w')

    # --------- Top 2 -------------
    top2_frame = CTkFrame(mainframe, corner_radius=20)
    top2_frame.pack(fill='x', pady=10, padx=10)


global side_menu, new_feed_button, search_barE, disable_auto_resize, side_menu_label, ctk_separator

root_color = root.cget("fg_color")
mainframe = CTkScrollableFrame(root, fg_color=root_color)
mainframe.pack(fill='both', expand=True, side='right')

# Side menu
side_menu = CTkScrollableFrame(root, corner_radius=0, fg_color=root_color, width=250)
side_menu.pack(side='left', fill='y')

side_menu_label = CTkLabel(side_menu, text="📰 Podcasts", font=("Calibri", 30, 'bold'))
side_menu_label.pack(pady=20, padx=10, anchor='w')

ctk_separator = CTkSeparator(side_menu, orientation="horizontal", line_weight=2, length=240)
ctk_separator.pack(fill='x', padx=10, pady=(0, 20))

new_feed_button = CTkButton(side_menu, text=" + New Feed", width=140, command=lambda: newfeed())
new_feed_button.pack(pady=10, padx=10, fill='x')

search_barE = CTkEntry(side_menu, placeholder_text="Search Feeds", width=140)
search_barE.pack(pady=10, padx=10, fill='x')



# logic to minimize and maximize side menu
def smallify():
    global side_menu, side_menu_label, new_feed_button, search_barE
    side_menu.configure(width=50)
    side_menu_label.configure(text="📰")
    new_feed_button.configure(text="+")
    search_barE.configure(placeholder_text="")

def biggify():
    global side_menu, side_menu_label, new_feed_button, search_barE
    side_menu.configure(width=250)
    side_menu_label.configure(text="📰 Podcasts")
    new_feed_button.configure(text=" + New Feed")
    search_barE.configure(placeholder_text="Search Feeds")

disable_auto_resize = False
def toggle_side_menu(event=None):
    width = root.winfo_width()
    global disable_auto_resize

    # Make sure the function runs on click as well
    if event is not None and hasattr(event, 'type') and event.type == 4:  # 4 corresponds to ButtonPress event
        if event.widget == side_menu_label:
            if side_menu.cget('width') == 250:
                smallify()
            else:
                biggify()
        elif event.widget == search_barE:
            if side_menu.cget('width') == 250:
                pass
            else:
                biggify()

        disable_auto_resize = True

    if disable_auto_resize == False:
        if width <= 800:
            smallify()
        else:
            biggify()
        #print('Ran')
    else:
        pass
    

    # make sure this function doesnt run multiple times on resize
    root.after(100, lambda: None)


def newfeed():
    clear_board()
    root.update_idletasks()

    floating_frame = CTkFrame(mainframe, corner_radius=20, fg_color='gray15', width=600, height=400)
    floating_frame.place(relx=0.5, rely=0.5, anchor='center')

    headerL = CTkLabel(floating_frame, text='Add New Feed', font=('Calibri', 50, 'bold'), justify='left')
    headerL.pack(pady=40, padx=(70,0), anchor='w')

    feed_entry = CTkEntry(floating_frame, placeholder_text="Enter RSS Feed URL", width=400, font=('Calibri', 20))
    feed_entry.pack(pady=20, padx=20, fill='x')

    add_button = CTkButton(floating_frame, text="Add Feed", width=150, command=lambda: backend.add_feed(feed_entry.get()))
    add_button.pack(pady=20, padx=20)





# ------------------------------------------
# Initialize the home screen
home()
root.update()
# Bind the toggle function to root window resize event
root.bind("<Configure>", toggle_side_menu)
side_menu_label.bind("<Button-1>", toggle_side_menu)
search_barE.bind("<Button-1>", toggle_side_menu)
# ------------------------------------------
root.mainloop()
