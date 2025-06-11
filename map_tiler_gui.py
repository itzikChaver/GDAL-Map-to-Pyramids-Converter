import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os
import subprocess
import threading # To run the command in the background so the GUI doesn't freeze

class MapTilerApp:
    def __init__(self, master):
        self.master = master
        master.title("GDAL Map to Pyramids Converter")
        master.geometry("600x450")
        master.resizable(False, False) # Prevents window resizing

        self.input_file_path = None

        # Top frame - file selection area
        self.top_frame = tk.Frame(master, bd=2, relief="groove")
        self.top_frame.pack(pady=10, padx=10, fill="x")

        # Label changed to not imply drag-and-drop
        self.instructions_label = tk.Label(self.top_frame, text="Please select a map file (GeoTIFF, JPG, PNG etc.)",
                                       height=2, relief="ridge", borderwidth=2, bg="lightgray")
        self.instructions_label.pack(pady=5, fill="x")

        self.path_entry = tk.Entry(self.top_frame, width=70)
        self.path_entry.pack(pady=5)
        self.path_entry.config(state="readonly") # Read-only

        self.browse_button = tk.Button(self.top_frame, text="Select Map File...", command=self.browse_file)
        self.browse_button.pack(pady=5)

        # Middle frame - gdal2tiles.exe options
        self.options_frame = tk.Frame(master, bd=2, relief="groove")
        self.options_frame.pack(pady=10, padx=10, fill="x")

        tk.Label(self.options_frame, text="gdal2tiles.exe Options:").pack(anchor="w")

        self.zoom_level_var = tk.StringVar(master, value="0-16") # Default: zoom 0 to 16
        tk.Label(self.options_frame, text="Zoom Levels (e.g.: 0-16):").pack(side="left", padx=5)
        self.zoom_level_entry = tk.Entry(self.options_frame, textvariable=self.zoom_level_var, width=10)
        self.zoom_level_entry.pack(side="left", padx=5)

        self.resampling_method_var = tk.StringVar(master, value="average") # Default
        tk.Label(self.options_frame, text="Resampling Method:").pack(side="left", padx=5)
        self.resampling_options = ["average", "nearest", "bilinear", "lanczos"]
        self.resampling_menu = tk.OptionMenu(self.options_frame, self.resampling_method_var, *self.resampling_options)
        self.resampling_menu.pack(side="left", padx=5)

        # Conversion button
        self.convert_button = tk.Button(master, text="Convert Map to Pyramids", command=self.start_conversion)
        self.convert_button.pack(pady=10)

        # Output area for status
        self.status_label = tk.Label(master, text="Ready...", fg="blue")
        self.status_label.pack(pady=5)

        self.output_text = scrolledtext.ScrolledText(master, wrap=tk.WORD, height=8, width=70, state="disabled")
        self.output_text.pack(pady=5, padx=10, fill="both", expand=True)

    def browse_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Map File",
            filetypes=(("Map files", "*.tif;*.tiff;*.jpg;*.jpeg;*.png;*.jp2"), ("All files", "*.*"))
        )
        if file_path:
            self.set_input_file(file_path)

    # The handle_drop function is no longer needed as there is no drag-and-drop

    def set_input_file(self, file_path):
        self.input_file_path = file_path
        self.path_entry.config(state="normal")
        self.path_entry.delete(0, tk.END)
        self.path_entry.insert(0, self.input_file_path)
        self.path_entry.config(state="readonly")
        self.status_label.config(text=f"File selected: {os.path.basename(file_path)}")
        self.clear_output_text()

    def clear_output_text(self):
        self.output_text.config(state="normal")
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state="disabled")

    def update_output_text(self, text):
        self.output_text.config(state="normal")
        self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END) # Auto-scroll to end
        self.output_text.config(state="disabled")

    def start_conversion(self):
        if not self.input_file_path or not os.path.exists(self.input_file_path):
            messagebox.showerror("Error", "Please select a valid map file first.")
            return

        self.clear_output_text()
        self.status_label.config(text="Starting conversion...", fg="orange")
        self.convert_button.config(state="disabled") # Prevents double clicks

        # Run the conversion in a separate thread so the GUI doesn't freeze
        self.conversion_thread = threading.Thread(target=self.run_gdal2tiles)
        self.conversion_thread.start()

    def run_gdal2tiles(self):
        input_file = self.input_file_path
        
        # Create output directory in the same location as the source file
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        output_dir = os.path.join(os.path.dirname(input_file), f"{base_name}_tiles")

        # Check if output directory exists and ask to delete if it does
        if os.path.exists(output_dir):
            if not messagebox.askyesno("Output directory exists",
                                       f"The directory '{output_dir}' already exists. Do you want to delete it and continue? (All existing tiles will be deleted!)"):
                self.status_label.config(text="Conversion canceled.", fg="red")
                self.convert_button.config(state="normal")
                return
            try:
                import shutil
                shutil.rmtree(output_dir)
                self.update_output_text(f"Existing directory deleted: {output_dir}\n")
            except Exception as e:
                self.update_output_text(f"Error deleting existing directory: {e}\n")
                self.status_label.config(text="Error deleting, conversion canceled.", fg="red")
                self.convert_button.config(state="normal")
                return

        zoom_levels = self.zoom_level_var.get()
        resampling_method = self.resampling_method_var.get()

        # **** CRITICAL CHANGE HERE: Use the gdal2tiles.exe executable directly ****
        # Use the full and precise path to the gdal2tiles.exe file as you verified in OSGeo4W Shell.
        # Based on your output: .\gdal2tiles.exe from C:\OSGeo4W\apps\Python312\Scripts directory
        # This means the full path is C:\OSGeo4W\apps\Python312\Scripts\gdal2tiles.exe

        gdal2tiles_exe_path = r"C:\OSGeo4W\apps\Python312\Scripts\gdal2tiles.exe" # ENSURE THIS PATH IS CORRECT FOR YOUR SYSTEM!

        command = [
            gdal2tiles_exe_path, # Execute gdal2tiles.exe directly
            '-p', 'raster',
            '-z', zoom_levels,
            f'--resampling={resampling_method}',
            input_file,
            output_dir
        ]
        # ************ END OF CRITICAL CHANGE ************

        self.update_output_text(f"Running command:\n{' '.join(command)}\n\n")

        try:
            # Execute the command and capture output in real-time
            # shell=True is sometimes required when directly running an EXE
            # It's important to add env=os.environ.copy() to ensure GDAL's
            # environment variables are loaded correctly (like GDAL_DATA).
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, universal_newlines=True, shell=True, env=os.environ.copy())
            
            for line in process.stdout:
                self.update_output_text(line)
            process.wait() # Wait for the process to finish

            if process.returncode == 0:
                self.status_label.config(text=f"Conversion completed successfully! Tiles in: {output_dir}", fg="green")
                messagebox.showinfo("Success", f"Conversion completed successfully!\nTiles created in directory:\n{output_dir}")
            else:
                self.status_label.config(text=f"Error in conversion. Exit code: {process.returncode}", fg="red")
                messagebox.showerror("Error", f"Error in conversion. Check output.\nExit code: {process.returncode}")

        except FileNotFoundError:
            self.status_label.config(text="Error: gdal2tiles.exe not found at the specified path. Ensure full and valid path.", fg="red")
            messagebox.showerror("Error", "gdal2tiles.exe not found. Ensure the full path you entered in the code is correct (e.g.: C:\\OSGeo4W\\apps\\Python312\\Scripts\\gdal2tiles.exe).")
        except Exception as e:
            self.status_label.config(text=f"An error occurred: {e}", fg="red")
            messagebox.showerror("General Error", f"An unexpected error occurred: {e}")
        finally:
            self.convert_button.config(state="normal") # Re-enable the button

if __name__ == "__main__":
    root = tk.Tk()
    
    app = MapTilerApp(root)
    root.mainloop()