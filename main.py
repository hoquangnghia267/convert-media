import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
import os
import threading

# Basic configuration
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class ImageConverterApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Modern Image Converter")
        self.geometry("700x500")

        self.selected_files = []

        # UI Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # 1. Header and Select Files
        self.header_frame = ctk.CTkFrame(self, corner_radius=10)
        self.header_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        self.header_frame.grid_columnconfigure(0, weight=1)

        self.label_title = ctk.CTkLabel(self.header_frame, text="Image Converter", font=ctk.CTkFont(size=24, weight="bold"))
        self.label_title.grid(row=0, column=0, padx=20, pady=10)

        self.btn_select = ctk.CTkButton(self.header_frame, text="Select Images", command=self.select_files)
        self.btn_select.grid(row=1, column=0, padx=(20, 10), pady=10, sticky="e")

        self.btn_clear = ctk.CTkButton(self.header_frame, text="Clear List", fg_color="gray", hover_color="#555555", command=self.clear_list)
        self.btn_clear.grid(row=1, column=1, padx=(10, 20), pady=10, sticky="w")

        # 2. Options Frame
        self.options_frame = ctk.CTkFrame(self, corner_radius=10)
        self.options_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")
        
        self.label_format = ctk.CTkLabel(self.options_frame, text="Target Format:")
        self.label_format.grid(row=0, column=0, padx=10, pady=10)

        self.format_var = ctk.StringVar(value="JPG")
        self.format_menu = ctk.CTkComboBox(self.options_frame, values=["JPG", "PNG", "WEBP", "BMP"], variable=self.format_var)
        self.format_menu.grid(row=0, column=1, padx=10, pady=10)

        self.btn_convert = ctk.CTkButton(self.options_frame, text="Start Conversion", fg_color="green", hover_color="#006400", command=self.start_conversion_thread)
        self.btn_convert.grid(row=0, column=2, padx=10, pady=10)

        self.btn_open_folder = ctk.CTkButton(self.options_frame, text="Open Folder", command=self.open_output_folder)
        self.btn_open_folder.grid(row=0, column=3, padx=10, pady=10)

        # 3. Log Area
        self.log_area = ctk.CTkTextbox(self, corner_radius=10)
        self.log_area.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.log_area.insert("0.0", "Welcome! Select images to start.\n")
        self.log_area.configure(state="disabled")

        # 4. Progress Bar
        self.progress_bar = ctk.CTkProgressBar(self)
        self.progress_bar.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="ew")
        self.progress_bar.set(0)

    def log(self, message):
        self.log_area.configure(state="normal")
        self.log_area.insert("end", f"> {message}\n")
        self.log_area.see("end")
        self.log_area.configure(state="disabled")

    def select_files(self):
        files = filedialog.askopenfilenames(
            title="Select Images",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.webp *.bmp *.tiff")]
        )
        if files:
            self.selected_files = list(files)
            self.log(f"Selected {len(files)} files.")
            for f in files:
                self.log(f" - {os.path.basename(f)}")

    def clear_list(self):
        self.selected_files = []
        self.log_area.configure(state="normal")
        self.log_area.delete("1.0", "end")
        self.log_area.insert("0.0", "List cleared. Select images to start.\n")
        self.log_area.configure(state="disabled")
        self.progress_bar.set(0)

    def open_output_folder(self):
        if self.selected_files:
            folder = os.path.dirname(self.selected_files[0])
            os.startfile(folder)
        else:
            # Open current directory if no files selected
            os.startfile(os.getcwd())

    def start_conversion_thread(self):
        if not self.selected_files:
            messagebox.showwarning("Warning", "Please select images first!")
            return
        
        # Disable buttons during conversion
        self.btn_select.configure(state="disabled")
        self.btn_convert.configure(state="disabled")
        
        threading.Thread(target=self.convert_images, daemon=True).start()

    def convert_images(self):
        target_format = self.format_var.get().upper()
        # Pillow uses 'JPEG' as the format name, not 'JPG'
        save_format = "JPEG" if target_format == "JPG" else target_format
        target_ext = target_format.lower()
        
        total = len(self.selected_files)
        success_count = 0
        
        self.log(f"Starting conversion to {target_format}...")
        
        for i, file_path in enumerate(self.selected_files):
            try:
                # Update progress
                self.progress_bar.set((i + 1) / total)
                
                img = Image.open(file_path)
                
                # Prepare output filename
                base_name = os.path.splitext(file_path)[0]
                output_path = f"{base_name}.{target_ext}"
                
                # Check if output_path is same as input
                if output_path.lower() == file_path.lower():
                    output_path = f"{base_name}_converted.{target_ext}"

                # Handle transparency for JPG/JPEG
                if target_ext in ["jpg", "jpeg"]:
                    if img.mode in ("RGBA", "P"):
                        img = img.convert("RGB")
                
                img.save(output_path, format=save_format)
                self.log(f"Converted: {os.path.basename(file_path)} -> {os.path.basename(output_path)}")
                success_count += 1
                
            except Exception as e:
                self.log(f"Error converting {os.path.basename(file_path)}: {str(e)}")

        self.log(f"Finished! Successfully converted {success_count}/{total} files.")
        self.progress_bar.set(1)
        
        # Re-enable buttons
        self.btn_select.configure(state="normal")
        self.btn_convert.configure(state="normal")
        
        messagebox.showinfo("Done", f"Converted {success_count} files successfully!")

if __name__ == "__main__":
    app = ImageConverterApp()
    app.mainloop()
