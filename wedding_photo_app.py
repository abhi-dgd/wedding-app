from tkinter import filedialog
import face_recognition
import numpy as np
import os
import pandas as pd
import shutil
import tkinter as tk

def load_and_encode_faces(images):
    face_encodings = []
    for image in images:
        try:
            face_encoding = face_recognition.face_encodings(image)[0]
            face_encodings.append(face_encoding)
        except IndexError as e:
            print(f"Error: {e}. No face found in the image.")
    return face_encodings

def find_matching_guests(guest_face_encodings, wedding_face_encodings):
    matches = []
    for wedding_photo, wedding_encoding in wedding_face_encodings.items():
        match = face_recognition.compare_faces(guest_face_encodings, wedding_encoding)
        if any(match):
            matching_guest = list(guest_faces.keys())[np.argmin(face_recognition.face_distance(guest_face_encodings, wedding_encoding))]
            matches.append((matching_guest, wedding_photo))
    return matches

def save_photos(guest_data, guest_image_folder, wedding_image_folder, output_folder):
    guest_image_paths = [os.path.join(guest_image_folder, f) for f in os.listdir(guest_image_folder) if os.path.isfile(os.path.join(guest_image_folder, f))]
    
    # Group all guest images by name
    guest_image_groups = {}
    for _, row in guest_data.iterrows():
        name = row['name']
        guest_image_groups[name] = [img_path for img_path in guest_image_paths if name in img_path]

    # Load and encode all guest images
    guest_faces = {}
    for name, img_paths in guest_image_groups.items():
        guest_images = []
        for img_path in img_paths:
            try:
                img = face_recognition.load_image_file(img_path)
                if len(face_recognition.face_encodings(img)) > 0:
                    guest_images.append(img)
                else:
                    print(f"No face found in guest image: {img_path}. Skipping...")
            except Exception as e:
                print(f"Error loading guest image: {img_path}. Skipping. Details: {e}")
        guest_faces[name] = guest_images

    if not any(guest_faces.values()):
        print("Error: No valid guest images found.")
        return

    guest_face_encodings = []
    for guest_images in guest_faces.values():
        for img in guest_images:
            guest_face_encodings.append(face_recognition.face_encodings(img)[0])

    # Load and encode all wedding images
    wedding_image_paths = [os.path.join(wedding_image_folder, f) for f in os.listdir(wedding_image_folder) if os.path.isfile(os.path.join(wedding_image_folder, f))]
    wedding_faces = {}
    for wedding_image_path in wedding_image_paths:
        try:
            wedding_image = face_recognition.load_image_file(wedding_image_path)
            wedding_faces[wedding_image_path] = face_recognition.face_encodings(wedding_image)
        except Exception as e:
            print(f"Error loading wedding image: {wedding_image_path}. Skipping. Details: {e}")

    # Find matching guests in wedding photos
    matching_guests = find_matching_guests(guest_face_encodings, wedding_faces)

    # Save matched photos to output folder
    for match in matching_guests:
        guest_name, wedding_photo = match
        guest_output_folder = os.path.join(output_folder, guest_name)
        os.makedirs(guest_output_folder, exist_ok=True)
        shutil.copy(wedding_photo, guest_output_folder)

def browse_csv():
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if file_path:
        csv_entry.delete(0, tk.END)
        csv_entry.insert(0, file_path)

def browse_guest_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        guest_folder_entry.delete(0, tk.END)
        guest_folder_entry.insert(0, folder_path)

def browse_wedding_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        wedding_folder_entry.delete(0, tk.END)
        wedding_folder_entry.insert(0, folder_path)

def browse_output_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        output_folder_entry.delete(0, tk.END)
        output_folder_entry.insert(0, folder_path)

def start_processing():
    csv_file = csv_entry.get()
    guest_folder = guest_folder_entry.get()
    wedding_folder = wedding_folder_entry.get()
    output_folder = output_folder_entry.get()

    if not csv_file or not guest_folder or not wedding_folder or not output_folder:
        tk.messagebox.showerror("Error", "Please fill in all required fields.")
        return

    try:
        guest_data = pd.read_csv(csv_file)
    except Exception as e:
        tk.messagebox.showerror("Error", f"Error reading CSV file: {e}")
        return

    save_photos(guest_data, guest_folder, wedding_folder, output_folder)
    tk.messagebox.showinfo("Success", "Processing completed and photos saved.")

# Create the main window
root = tk.Tk()
root.title("Wedding Photo App")

# Create and place labels, entries, and buttons
csv_label = tk.Label(root, text="CSV File:")
csv_label.grid(row=0, column=0, sticky="w", padx=(10, 5), pady=(10, 5))
csv_entry = tk.Entry(root, width=60)
csv_entry.grid(row=0, column=1, padx=(0, 5), pady=(10, 5))
csv_button = tk.Button(root, text="Browse", command=browse_csv)
csv_button.grid(row=0, column=2, padx=(0, 10), pady=(10, 5))

guest_folder_label = tk.Label(root, text="Guest Images Folder:")
guest_folder_label.grid(row=1, column=0, sticky="w", padx=(10, 5), pady=(0, 5))
guest_folder_entry = tk.Entry(root, width=60)
guest_folder_entry.grid(row=1, column=1, padx=(0, 5), pady=(0, 5))
guest_folder_button = tk.Button(root, text="Browse", command=browse_guest_folder)
guest_folder_button.grid(row=1, column=2, padx=(0, 10), pady=(0, 5))

wedding_folder_label = tk.Label(root, text="Wedding Images Folder:")
wedding_folder_label.grid(row=2, column=0, sticky="w", padx=(10, 5), pady=(0, 5))
wedding_folder_entry = tk.Entry(root, width=60)
wedding_folder_entry.grid(row=2, column=1, padx=(0, 5), pady=(0, 5))
wedding_folder_button = tk.Button(root, text="Browse", command=browse_wedding_folder)
wedding_folder_button.grid(row=2, column=2, padx=(0, 10), pady=(0, 5))

output_folder_label = tk.Label(root, text="Output Folder:")
output_folder_label.grid(row=3, column=0, sticky="w", padx=(10, 5), pady=(0, 5))
output_folder_entry = tk.Entry(root, width=60)
output_folder_entry.grid(row=3, column=1, padx=(0, 5), pady=(0, 5))
output_folder_button = tk.Button(root, text="Browse", command=browse_output_folder)
output_folder_button.grid(row=3, column=2, padx=(0, 10), pady=(0, 5))

process_button = tk.Button(root, text="Start Processing", command=start_processing)
process_button.grid(row=4, column=1, pady=(10, 10))


# Run the main loop
root.mainloop()
