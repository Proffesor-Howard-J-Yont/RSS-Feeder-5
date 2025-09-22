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
import subprocess
import json
import os
import io
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

    # --------- Top 1 ------------- This will feature the top 1 podcasts based on clicks
    top1_frame = CTkFrame(mainframe, corner_radius=20)
    top1_frame.pack(fill='x', pady=10, padx=10)

    top1 = backend.grab_top_1_podcast()
    if len(top1) == 0:
        nofeedL = CTkLabel(top1_frame, text="No feeds available. Please add a new feed.", font=('Calibri', 20), text_color='gray40')
        nofeedL.place(relx=0.5, rely=0.5, anchor='center')
    else:
        feed_name, feed_description, feed_url, amt_clicked = top1[0]

        feed_image = None
        backend.c.execute("SELECT image FROM feeds WHERE feed_url = ?", (feed_url,))
        result = backend.c.fetchone()
        if result and result[0]:
            feed_image = CTkImage(light_image=Image.open(io.BytesIO(result[0])), dark_image=Image.open(io.BytesIO(result[0])), size=(200, 200))
        else:
            feed_image = CTkImage(light_image=Image.open('assets/podcast_placeholder.png'), dark_image=Image.open('assets/podcast_placeholder.png'), size=(150, 150), text='')

        feed_img_label = CTkLabel(top1_frame, image=feed_image, text='')
        feed_img_label.grid(row=0, column=0, rowspan=3, pady=(20, 10), padx=20)

        feed_label = CTkLabel(top1_frame, text=feed_name, font=('Calibri', 30, 'bold'))
        feed_label.grid(row=0, column=1, pady=(20, 10), padx=20, sticky='w')

        desc_text_box = CTkTextbox(top1_frame, height=150, font=('Calibri', 15), wrap='word', bg_color=top1_frame.cget("fg_color"), fg_color=top1_frame.cget("fg_color"), border_width=0)
        desc_text_box.grid(row=1, column=1, pady=(10, 0), padx=20, sticky='nsew')
        desc_text_box.insert('0.0', feed_description if feed_description else "No description available.")
        desc_text_box.configure(state='disabled')

        top1_frame.grid_columnconfigure(1, weight=1)  # Make column 1 (description column) expandable
        top1_frame.grid_rowconfigure(1, weight=1)     # Make row 1 (description row) expandable

        # Click event to view feed
        top1_frame.bind("<Button-1>", lambda e: view_feed(feed_url))
        feed_img_label.bind("<Button-1>", lambda e: view_feed(feed_url))
        feed_label.bind("<Button-1>", lambda e: view_feed(feed_url))
        desc_text_box.bind("<Button-1>", lambda e: view_feed(feed_url))

    # --------- Top podcasts slider -------------
    top_podcasts_frame = CTkFrame(mainframe, corner_radius=20, height=250)
    top_podcasts_frame.pack(fill='x', pady=10, padx=10)

    top_podcastsL = CTkLabel(top_podcasts_frame, text='Top Podcasts', font=('Calibri', 30, 'bold'), justify='left')
    top_podcastsL.grid(row=0, column=0, padx=20, pady=10, sticky='w', columnspan=2)

    # Create a canvas and side arrow buttons for horizontal scrolling
    canvas = CTkCanvas(top_podcasts_frame, height=250, highlightthickness=0, bg='grey17')
    canvas.grid(row=1, column=1, padx=(20,0), pady=10, sticky='nsew')

    scrollbar = CTkScrollbar(top_podcasts_frame, orientation="horizontal", command=canvas.xview)
    #scrollbar.grid(row=2, column=1, padx=(20,0), pady=(0,10), sticky='ew')
    canvas.configure(xscrollcommand=scrollbar.set)

    scrollable_frame = CTkFrame(canvas, fg_color=top_podcasts_frame.cget("fg_color"))
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
    top_podcasts_frame.grid_columnconfigure(1, weight=1)
    canvas.bind("<MouseWheel>", lambda event: canvas.xview_scroll(int(-1*(event.delta/120)), "units"))

    # Button to scroll left
    def scroll_left():
        canvas.xview_scroll(-1, "units")
    left_button = CTkButton(top_podcasts_frame, text="⬅️", width=30, height=50, command=scroll_left)
    left_button.grid(row=1, column=0, padx=(20,0), pady=10)

    # Button to scroll right
    def scroll_right():
        canvas.xview_scroll(1, "units")
    right_button = CTkButton(top_podcasts_frame, text="➡️", width=30, height=50, command=scroll_right)
    right_button.grid(row=1, column=2, padx=(0,20), pady=10)
    
    col = 0
    for feed in backend.grab_top_10_podcasts():
        feed_name, feed_description, feed_url, amt_clicked = feed

        feed_image = None
        backend.c.execute("SELECT image FROM feeds WHERE feed_url = ?", (feed_url,))
        result = backend.c.fetchone()
        if result and result[0]:
            feed_image = CTkImage(light_image=Image.open(io.BytesIO(result[0])), dark_image=Image.open(io.BytesIO(result[0])), size=(150, 150))
        else:
            feed_image = CTkImage(light_image=Image.open('assets/podcast_placeholder.png'), dark_image=Image.open('assets/podcast_placeholder.png'), size=(150, 150), text='')

        feed_img_button = CTkButton(scrollable_frame, width=150, height=200, text='', compound='top', fg_color='transparent', hover_color='gray25', font=('Calibri', 15, 'bold'), image=feed_image, command=lambda url=feed_url: view_feed(url))
        feed_img_button.grid(row=0, column=col, padx=10, pady=10)
        col += 1

    




def view_feed(feed_url):
    clear_board()
    root.update_idletasks()

    view_feed_frame = CTkFrame(mainframe, corner_radius=20)
    view_feed_frame.pack(fill='x', pady=10, padx=10)

    pod_details = backend.get_feed_details(feed_url)
    if not pod_details:
        errorL = CTkLabel(view_feed_frame, text="Error retrieving feed details.", font=('Calibri', 20), text_color='red')
        errorL.place(relx=0.5, rely=0.5, anchor='center')

        # back button to return home
        back_button = CTkButton(view_feed_frame, text="Back", width=100, command=lambda: home())
        back_button.pack(pady=10, padx=10, anchor='w')
        return

    if len(pod_details) == 0:
        nofeedL = CTkLabel(view_feed_frame, text="No feeds available. Please add a new feed.", font=('Calibri', 20), text_color='gray40')
        nofeedL.place(relx=0.5, rely=0.5, anchor='center')
        # back button to return home
        back_button = CTkButton(view_feed_frame, text="Back", width=100, command=lambda: home())
        back_button.pack(pady=10, padx=10, anchor='w')
        return
    else:
        feed_name, feed_description, feed_url, amt_clicked = pod_details[0]

        feed_image = None
        backend.c.execute("SELECT image FROM feeds WHERE feed_url = ?", (feed_url,))
        result = backend.c.fetchone()
        if result and result[0]:
            feed_image = CTkImage(light_image=Image.open(io.BytesIO(result[0])), dark_image=Image.open(io.BytesIO(result[0])), size=(200, 200))
        else:
            feed_image = CTkImage(light_image=Image.open('assets/podcast_placeholder.png'), dark_image=Image.open('assets/podcast_placeholder.png'), size=(150, 150), text='')

        feed_img_label = CTkLabel(view_feed_frame, image=feed_image, text='')
        feed_img_label.grid(row=0, column=0, rowspan=3, pady=(20, 10), padx=20)

        feed_label = CTkLabel(view_feed_frame, text=feed_name, font=('Calibri', 30, 'bold'))
        feed_label.grid(row=0, column=1, pady=(20, 10), padx=20, sticky='w')

        desc_text_box = CTkTextbox(view_feed_frame, height=150, font=('Calibri', 15), wrap='word', bg_color=view_feed_frame.cget("fg_color"), fg_color=view_feed_frame.cget("fg_color"), border_width=0)
        desc_text_box.grid(row=1, column=1, pady=(10, 0), padx=20, sticky='nsew')
        desc_text_box.insert('0.0', feed_description if feed_description else "No description available.")
        desc_text_box.configure(state='disabled')

        view_feed_frame.grid_columnconfigure(1, weight=1)  # Make column 1 (description column) expandable
        view_feed_frame.grid_rowconfigure(1, weight=1)     # Make row 1 (description row) expandable

        # view episodes here
        latest_episodes = CTkLabel(mainframe, text='Latest', font=('Calibri', 40, 'italic'), justify='left')
        latest_episodes.pack(pady=(70, 20), padx=(70,0), anchor='w')

        episodes_showed = 0

        for episode in backend.get_episodes_for_feed(feed_url):
            if episodes_showed >= 20:
                break

            episodes_showed += 1

            ep_sep = CTkSeparator(mainframe, orientation="horizontal", line_weight=2)
            ep_sep.pack(fill='x', padx=20, pady=20, expand=True)

            ep_frame = CTkFrame(mainframe, corner_radius=10)
            ep_frame.pack(fill='x', pady=5, padx=10)

            ep_title = CTkLabel(ep_frame, text=episode[0], font=('Calibri', 20, 'bold'))
            ep_title.grid(row=0, column=0, pady=(10, 0), padx=20, sticky='w')

            ep_desc = CTkTextbox(ep_frame, height=100, font=('Calibri', 12), wrap='word', bg_color=ep_frame.cget("fg_color"), fg_color=ep_frame.cget("fg_color"), border_width=0)
            ep_desc.grid(row=1, column=0, pady=(10, 0), padx=20, sticky='nsew')
            ep_desc.insert('0.0', episode[1] if episode[1] else "No description available.")

            ep_pub_date = CTkLabel(ep_frame, text=f"Published on: {episode[4] if episode[4] else 'Unknown'}", font=('Calibri', 12), text_color='gray40')
            ep_pub_date.grid(row=2, column=0, pady=(0, 10), padx=20, sticky='w')

            ep_frame.grid_columnconfigure(0, weight=1)  # Make column 0 expandable

            if episodes_showed % 2 == 0:
                ep_frame.configure(fg_color='gray20')
                ep_desc.configure(bg_color='gray20', fg_color='gray20')

            root.update()



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

    add_button = CTkButton(floating_frame, text="Add Feed", width=150, command=lambda: add_feed_click(feed_entry.get()))
    add_button.pack(pady=20, padx=20)

def add_feed_click(feed_url):
    # Create progress file
    with open('progress.json', 'w') as f:
        json.dump({"progress": 0, "step": "Starting..."}, f)

    # Start the backend process
    subprocess.Popen(["python", "backend.py", feed_url])

    clear_board()
    root.update_idletasks()

    floating_frame = CTkFrame(mainframe, corner_radius=20, fg_color='gray15', width=600, height=400)
    floating_frame.place(relx=0.5, rely=0.5, anchor='center')

    headerL = CTkLabel(floating_frame, text='Loading New Feed', font=('Calibri', 50, 'bold'))
    headerL.pack(pady=(40, 0), padx=70)

    subheaderL = CTkLabel(floating_frame, text="This may take a few minutes.", font=('Calibri', 20), text_color='gray40')
    subheaderL.pack(pady=(10, 10), padx=10)

    subheader2L = CTkLabel(floating_frame, text="...", font=('Calibri', 20, 'italic'))
    subheader2L.pack(pady=40, padx=10)

    loading_progress = CTkProgressBar(floating_frame, mode="determinate", width=400)
    loading_progress.pack(pady=(0, 40), padx=15, fill="x")
    loading_progress.set(0)

    def update_progress():
        if os.path.exists('progress.json'):
            try:
                with open('progress.json', 'r') as f:
                    data = json.load(f)
                    loading_progress.set(data['progress'] / 100)
                    subheader2L.configure(text=data['step'])
                    if data['progress'] < 100:
                        root.after(100, update_progress)
                    else:
                        os.remove('progress.json')
                        home()  # Return to home screen when complete
            except:
                root.after(100, update_progress)
        else:
            root.after(100, update_progress)

    update_progress()
# ------------------------------------------
# Initialize the home screen
home()
root.update()
# Bind the toggle function to root window resize event
root.bind("<Configure>", toggle_side_menu)
side_menu_label.bind("<Button-1>", lambda e: home())
search_barE.bind("<Button-1>", toggle_side_menu)
# ------------------------------------------
root.mainloop()
