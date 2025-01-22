import threading
from transformers import pipeline
import scipy.io.wavfile
from tkinter import messagebox, filedialog, Tk, Label, Button, Text, ttk, StringVar, Entry
from tkinter import Menu
from pydub import AudioSegment
from pydub.playback import play
import logging

logging.basicConfig(filename="musicgen.log", level=logging.INFO)
loaded_models = {}

def load_model(model_name: str):
    """Load the model if not already loaded."""
    if model_name not in loaded_models:
        try:
            logging.info(f"Loading model: {model_name}")
            loaded_models[model_name] = pipeline("text-to-audio", model=model_name)
        except Exception as e:
            logging.error(f"Error loading model {model_name}: {e}")
            messagebox.showerror("Error", f"Could not load model: {model_name}\n{e}")
    return loaded_models[model_name]

def generate_music(prompt: str, model_name: str, progress: ttk.Progressbar, save_location: str):
    """
    Generates music based on the prompt and selected model type.
    Updates the progress bar and saves the audio at the specified location.
    """
    logging.info(f"Generating music for the prompt: {prompt} using model {model_name}....")
    try:
        progress.start()
        model = load_model(model_name)
        
        music = model(prompt, forward_params={"do_sample": True})
        
        scipy.io.wavfile.write(save_location, rate=music["sampling_rate"], data=music["audio"])
        messagebox.showinfo("Success", f"Music generated successfully and saved at {save_location}!")
        logging.info(f"Music saved successfully at {save_location}")
        print(f"Succesfully generated music and saved at {save_location}")
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        messagebox.showerror("Error", f"An error occurred while generating music: {e}")
    finally:
        progress.stop()


def on_generate_button_click():
    prompt = text_prompt.get("1.0", "end-1c").strip() 
    model_name = selected_model.get() 
    if not prompt:
        messagebox.showwarning("Warning", "Please enter a prompt before generating music!")
        return

    save_location = filedialog.asksaveasfilename(
        defaultextension=".wav", filetypes=[("WAV files", "*.wav"), ("All files", "*.*")]
    )
    if not save_location:
        messagebox.showwarning("Warning", "Please select a location to save the music!")
        return
    
    threading.Thread(
        target=generate_music,
        args=(prompt, model_name, progress_bar, save_location),
        daemon=True
    ).start()

def use_example_prompt():
    """Populate the prompt text area with an example prompt."""
    text_prompt.delete("1.0", "end")
    text_prompt.insert("1.0", example_prompts[0]) 

def show_help():
    """Display help information."""
    help_message = (
        "To generate music, enter a prompt describing the music you want.\n"
        "Select a model (small, medium, or large).\n"
        "Click 'Generate Music' to create and save the music.\n"
        "You can also play the music after generation."
    )
    messagebox.showinfo("How to Use", help_message)

root = Tk()
root.title("Music Generation Application")
root.geometry("450x450")

menu = Menu(root)
help_menu = Menu(menu, tearoff=0)
help_menu.add_command(label="How to Use", command=show_help)
menu.add_cascade(label="Help", menu=help_menu)
root.config(menu=menu)

label = Label(root, text="Enter the prompt for music generation:")
label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

text_prompt = Text(root, height=2, width=40)
text_prompt.grid(row=1, column=0, padx=10, pady=5, columnspan=2)

example_prompts = ["A relaxing piano melody", "Energetic electronic beats", "A serene orchestral piece"]
example_button = Button(root, text="Use Example", command=use_example_prompt)
example_button.grid(row=2, column=0, padx=10, pady=5)

model_label = Label(root, text="Select the model type:")
model_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")

model_options = ["facebook/musicgen-small", "facebook/musicgen-medium", "facebook/musicgen-large"]
selected_model = StringVar(value=model_options[0])  

model_dropdown = ttk.Combobox(root, textvariable=selected_model, values=model_options, state="readonly")
model_dropdown.grid(row=4, column=0, padx=10, pady=5)

generate_button = Button(root, text="Generate Music", command=on_generate_button_click)
generate_button.grid(row=5, column=0, padx=10, pady=20)

progress_bar = ttk.Progressbar(root, mode="indeterminate")
progress_bar.grid(row=6, column=0, padx=10, pady=10)

root.mainloop()
 