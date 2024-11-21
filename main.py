import os
from tkinter import Tk, Label, Button, Entry, filedialog, IntVar, messagebox, ttk, Canvas
from PIL import Image, ImageTk
from tkinterdnd2 import TkinterDnD, DND_FILES




def get_size_format(b, factor=1024, suffix="B"):
   for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
       if b < factor:
           return f"{b:.2f}{unit}{suffix}"
       b /= factor
   return f"{b:.2f}Y{suffix}"




def compress_img(image_path, output_file, target_size, width=None, height=None):
   try:
       img = Image.open(image_path)
       original_size = os.path.getsize(image_path)
       print("[*] Original size:", get_size_format(original_size))


       if width and height:
           img = img.resize((width, height), Image.LANCZOS)


       quality = 85
       img.save(output_file, quality=quality, optimize=True)
       compressed_size = os.path.getsize(output_file)


       while compressed_size > target_size and quality > 10:
           quality -= 5
           img.save(output_file, quality=quality, optimize=True)
           compressed_size = os.path.getsize(output_file)


       while compressed_size < target_size and quality < 95:
           quality += 1
           img.save(output_file, quality=quality, optimize=True)
           compressed_size = os.path.getsize(output_file)


       saving_diff = compressed_size - original_size
       return output_file, original_size, compressed_size, saving_diff
   except Exception as e:
       messagebox.showerror("Error", f"An error occurred: {e}")
       return None, None, None, None




def browse_file():
   file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")])
   if file_path:
       entry_path.delete(0, "end")
       entry_path.insert(0, file_path)
       preview_image(file_path)




def preview_image(image_path):
   try:
       img = Image.open(image_path)
       img.thumbnail((200, 200))
       img_tk = ImageTk.PhotoImage(img)
       canvas_preview.config(width=img_tk.width(), height=img_tk.height())
       canvas_preview.create_image(0, 0, anchor="nw", image=img_tk)
       canvas_preview.image = img_tk
       original_size = os.path.getsize(image_path)
       label_original_size.config(text=f"Original Size: {get_size_format(original_size)}")
   except Exception as e:
       messagebox.showerror("Error", f"Could not load image preview: {e}")




def browse_output_file():
   file_path = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png")])
   if file_path:
       entry_output_file.delete(0, "end")
       entry_output_file.insert(0, file_path)




def start_compression():
   image_path = entry_path.get()
   output_file = entry_output_file.get()
   target_size = target_size_var.get() * 1024


   if not image_path or not os.path.isfile(image_path):
       messagebox.showerror("Error", "Please select a valid image file.")
       return
   if not output_file:
       messagebox.showerror("Error", "Please select a valid output file path.")
       return


   width = int(entry_width.get()) if entry_width.get() else None
   height = int(entry_height.get()) if entry_height.get() else None


   progress_bar.start(10)
   root.after(100, lambda: compress_and_display_results(image_path, output_file, target_size, width, height))




def compress_and_display_results(image_path, output_file, target_size, width, height):
   new_filepath, original_size, new_size, saving_diff = compress_img(image_path, output_file, target_size, width,
                                                                     height)
   progress_bar.stop()
   if new_filepath:
       result = (
           f"Original size: {get_size_format(original_size)}\n"
           f"New size: {get_size_format(new_size)}\n"
           f"Size change: {saving_diff / original_size * 100:.2f}%"
       )
       label_result.config(text=result)
       preview_image(new_filepath)
       messagebox.showinfo("Success", f"Image saved at {new_filepath}")




def on_drop(event):
   file_path = event.data.strip()
   if os.path.isfile(file_path):
       entry_path.delete(0, "end")
       entry_path.insert(0, file_path)
       preview_image(file_path)




# Setting up the TkinterDnD window
root = TkinterDnD.Tk()
root.title("Image Compressor - The Pycodes")
root.geometry("800x500")


# Enable drag-and-drop functionality for the entry widget
entry_path = Entry(root, width=50)
entry_path.grid(row=0, column=1, padx=5, pady=5)
entry_path.drop_target_register(DND_FILES)
entry_path.dnd_bind('<<Drop>>', on_drop)


Label(root, text="Select Image:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
Button(root, text="Browse", command=browse_file).grid(row=0, column=2, padx=5, pady=5)


Label(root, text="Output File:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
entry_output_file = Entry(root, width=50)
entry_output_file.grid(row=1, column=1, padx=5, pady=5)
Button(root, text="Browse", command=browse_output_file).grid(row=1, column=2, padx=5, pady=5)


Label(root, text="Target Size (KB):").grid(row=2, column=0, padx=5, pady=5, sticky="e")
target_size_var = IntVar(value=500)
Entry(root, textvariable=target_size_var).grid(row=2, column=1, padx=5, pady=5)


Label(root, text="Width:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
entry_width = Entry(root)
entry_width.grid(row=3, column=1, padx=5, pady=5)


Label(root, text="Height:").grid(row=4, column=0, padx=5, pady=5, sticky="e")
entry_height = Entry(root)
entry_height.grid(row=4, column=1, padx=5, pady=5)


Button(root, text="Compress Image", command=start_compression).grid(row=5, column=1, padx=5, pady=20)


progress_bar = ttk.Progressbar(root, mode='indeterminate')
progress_bar.grid(row=6, column=1, padx=5, pady=5)


canvas_preview = Canvas(root, width=200, height=200)
canvas_preview.grid(row=0, column=3, rowspan=5, padx=10, pady=10)


label_original_size = Label(root, text="Original Size: ")
label_original_size.grid(row=7, column=0, columnspan=3, padx=5, pady=5)


label_result = Label(root, text="", justify="left")
label_result.grid(row=8, column=0, columnspan=3, padx=5, pady=5)


root.mainloop()
