import tkinter as tk
from tkinter import filedialog
from gtts import gTTS
from PIL import Image, ImageTk
import os
from BackendMain import BackendMain

class MSRPSoftwareGUI:
    def __init__(self, master):
        self.master = master
        master.title("Welcome to MSRP Software!")

        self.title_label = tk.Label(master, text="Welcome to MSRP Software!", font=("Helvetica", 16))
        self.title_label.pack(pady=20)

        self.choose_button = tk.Button(master, text="Choose an Image", command=self.choose_image)
        self.choose_button.pack(pady=10)

        self.generate_button = tk.Button(master, text="Generate MP3", command=self.generate_mp3)
        self.generate_button.pack(pady=10)

        self.image_label = tk.Label(master)
        self.image_label.pack(pady=20)

        # Create a list of values from 40 to 160
        values = list(range(40, 161))

        # Create a StringVar to store the selected value
        self.number_var = tk.StringVar()
        self.number_var.set("75")  # Set default value

        # Create an OptionMenu and populate it with values
        self.number_dropdown = tk.OptionMenu(master, self.number_var, *values)
        self.number_dropdown.pack(pady=10)

        # Loading window
        self.loading_window = None

        # Canvas for drawing
        self.canvas = tk.Canvas(master, width=400, height=300, bg="white")
        self.canvas.pack(pady=20)

    def choose_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")])
        if file_path:
            print("Chosen Image:", file_path)
            self.display_image(file_path)
            self.loading_action()
            self.master.after(100, lambda: self.run_backend_main(file_path))

    def display_image(self, image_path):
        image = Image.open(image_path)
        image.thumbnail((800, 600))  # Resize image if needed
        imgtk = ImageTk.PhotoImage(image)
        self.image_label.config(image=imgtk)
        self.image_label.image = imgtk

    def generate_mp3(self):
        text_to_speech = "This is a sample text. You can replace it with your own content."
        tts = gTTS(text=text_to_speech, lang='en')
        mp3_file = "./sounds/output.mp3"
        tts.save(mp3_file)
        os.system(f"start {mp3_file}")

    def loading_action(self):
        self.loading_window = tk.Toplevel(self.master)
        self.loading_window.title("Loading")
        self.loading_window.geometry("200x100")
        self.loading_label = tk.Label(self.loading_window, text="Loading...")
        self.loading_label.pack(expand=True, fill='both')

    def loading_done(self):
        if self.loading_window:
            self.loading_window.destroy()

    def run_backend_main(self, file_path):
        BackendMain.main(file_path)
        self.loading_done()

if __name__ == "__main__":
    root = tk.Tk()
    msrp_software_gui = MSRPSoftwareGUI(root)
    root.mainloop()
