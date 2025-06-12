import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os
import subprocess
import threading # To run the command in the background so the GUI doesn't freeze

class MapTilerApp:
    def __init__(self, master):
        self.master = master
        master.title("GDAL Map to Pyramids Converter")
        master.geometry("700x550") # Increased height to accommodate new input fields
        master.resizable(False, False) # Prevents window resizing

        self.input_file_path = None
        self.output_dir_path = tk.StringVar(master) # Variable to store output directory path

        # --- Top Frame - Input File Selection ---
        self.input_frame = tk.LabelFrame(master, text="Input Map File", bd=2, relief="groove")
        self.input_frame.pack(pady=10, padx=10, fill="x")

        tk.Label(self.input_frame, text="Please select a map file (GeoTIFF, JPG, PNG etc.):").pack(pady=5)
        
        self.input_path_entry = tk.Entry(self.input_frame, width=80)
        self.input_path_entry.pack(pady=5)
        self.input_path_entry.config(state="readonly")

        self.browse_input_button = tk.Button(self.input_frame, text="Select Map File...", command=self.browse_input_file)
        self.browse_input_button.pack(pady=5)

        # --- Middle Frame - Output Directory Selection ---
        self.output_frame = tk.LabelFrame(master, text="Output Directory", bd=2, relief="groove")
        self.output_frame.pack(pady=10, padx=10, fill="x")

        tk.Label(self.output_frame, text="Select a directory to save the output tiles:").pack(pady=5)
        
        self.output_path_entry = tk.Entry(self.output_frame, textvariable=self.output_dir_path, width=80)
        self.output_path_entry.pack(pady=5)
        self.output_path_entry.config(state="readonly") # Initially read-only

        self.browse_output_button = tk.Button(self.output_frame, text="Select Output Directory...", command=self.browse_output_dir)
        self.browse_output_button.pack(pady=5)

        # --- Options Frame - gdal2tiles.exe Options ---
        self.options_frame = tk.LabelFrame(master, text="gdal2tiles.exe Options", bd=2, relief="groove")
        self.options_frame.pack(pady=10, padx=10, fill="x")

        # Zoom Levels
        tk.Label(self.options_frame, text="Zoom Levels (e.g.: 0-16):").pack(side="left", padx=5)
        self.zoom_level_var = tk.StringVar(master, value="0-16")
        self.zoom_level_entry = tk.Entry(self.options_frame, textvariable=self.zoom_level_var, width=10)
        self.zoom_level_entry.pack(side="left", padx=5)

        # Resampling Method
        tk.Label(self.options_frame, text="Resampling Method:").pack(side="left", padx=5)
        self.resampling_method_var = tk.StringVar(master, value="average")
        self.resampling_options = ["average", "nearest", "bilinear", "lanczos"]
        self.resampling_menu = tk.OptionMenu(self.options_frame, self.resampling_method_var, *self.resampling_options)
        self.resampling_menu.pack(side="left", padx=5)

        # --- Conversion Button ---
        self.convert_button = tk.Button(master, text="Convert Map to Pyramids", command=self.start_conversion)
        self.convert_button.pack(pady=10)

        # --- Output Area for Status ---
        self.status_label = tk.Label(master, text="Ready...", fg="blue")
        self.status_label.pack(pady=5)

        self.output_text = scrolledtext.ScrolledText(master, wrap=tk.WORD, height=8, width=70, state="disabled")
        self.output_text.pack(pady=5, padx=10, fill="both", expand=True)

    def browse_input_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Map File",
            filetypes=(("Map files", "*.tif;*.tiff;*.jpg;*.jpeg;*.png;*.jp2"), ("All files", "*.*"))
        )
        if file_path:
            self.set_input_file(file_path)

            # Auto-populate output directory based on input file's directory
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            default_output_path = os.path.join(os.path.dirname(file_path), f"{base_name}_tiles")
            self.output_dir_path.set(default_output_path)


    def browse_output_dir(self):
        dir_path = filedialog.askdirectory(
            title="Select Output Directory"
        )
        if dir_path:
            # When a directory is selected, use it directly
            self.output_dir_path.set(dir_path)
            self.status_label.config(text=f"Output directory selected: {os.path.basename(dir_path)}")
            self.clear_output_text()


    def set_input_file(self, file_path):
        self.input_file_path = file_path
        self.input_path_entry.config(state="normal")
        self.input_path_entry.delete(0, tk.END)
        self.input_path_entry.insert(0, self.input_file_path)
        self.input_path_entry.config(state="readonly")
        self.status_label.config(text=f"Input file selected: {os.path.basename(file_path)}")
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
            messagebox.showerror("Error", "Please select a valid input map file first.")
            return
        
        chosen_output_dir = self.output_dir_path.get()
        if not chosen_output_dir:
            messagebox.showerror("Error", "Please select an output directory.")
            return
        
        # Ensure the chosen output directory exists before proceeding
        # The gdal2tiles.exe will create the final _tiles subfolder inside this.
        if not os.path.exists(chosen_output_dir):
            try:
                os.makedirs(chosen_output_dir)
                self.update_output_text(f"Created output base directory: {chosen_output_dir}\n")
            except Exception as e:
                messagebox.showerror("Error", f"Could not create output directory: {chosen_output_dir}\nError: {e}")
                return


        self.clear_output_text()
        self.status_label.config(text="Starting conversion...", fg="orange")
        self.convert_button.config(state="disabled") # Prevents double clicks

        # Run the conversion in a separate thread so the GUI doesn't freeze
        self.conversion_thread = threading.Thread(target=self.run_gdal2tiles, args=(chosen_output_dir,))
        self.conversion_thread.start()

    def run_gdal2tiles(self, output_base_dir):
        input_file = self.input_file_path
        
        # gdal2tiles.exe automatically creates a subfolder like 'filename_tiles'
        # inside the provided output directory. So, we provide the base directory.
        final_output_path_for_gdal = output_base_dir 

        # The check for existing directory and deletion logic is now handled by gdal2tiles.exe itself.
        # It prompts the user for overwrite by default if the exact output_dir already exists.
        # However, for consistency and clear user control within the GUI,
        # we can still offer a prompt *before* gdal2tiles.exe runs,
        # if the *exact* final output directory name is known and exists.
        # For simplicity, we'll let gdal2tiles.exe handle the overwrite prompt for its specific output folder.


        zoom_levels = self.zoom_level_var.get()
        resampling_method = self.resampling_method_var.get()

        # --- Define Paths to GDAL Executables within the project's 'bin' folder ---
        # Get the directory where the current script (map_tiler_gui.py) is located
        script_dir = os.path.dirname(__file__)
        
        # Construct the full paths to the GDAL executables in the 'bin' folder
        gdal2tiles_exe_path = os.path.join(script_dir, "bin", "gdal2tiles.exe") 

        # --- VERY IMPORTANT: Set the GDAL_DATA environment variable ---
        # gdal2tiles, gdaladdo, gdal_translate often need GDAL_DATA to find projection files, etc.
        # This variable points to the 'gdal-data' folder, typically inside OSGeo4W installation.
        # You'll need to copy this folder into your 'bin' directory, or find its path.
        # A common location for GDAL_DATA would be: C:\OSGeo4W\share\gdal (or similar)
        # For simplicity, let's assume you've copied 'gdal-data' into your 'bin' folder.
        # Or, if you know the fixed path, you can use it directly:
        # gdal_data_path = r"C:\OSGeo4W\share\gdal" 
        
        # If you copy the 'gdal-data' folder into your 'bin' directory:
        gdal_data_path = os.path.join(script_dir, "bin", "gdal-data") 

         # Create a copy of the current environment variables
        env = os.environ.copy()
        # Add or update GDAL_DATA
        env['GDAL_DATA'] = gdal_data_path
        # Optionally, you might also need to add the 'bin' directory to PATH if there are shared DLLs
        # env['PATH'] = os.path.join(script_dir, "bin") + os.pathsep + env['PATH']

        command = [
            gdal2tiles_exe_path, # Execute gdal2tiles.exe directly
            '-p', 'raster',
            '-z', zoom_levels,
            f'--resampling={resampling_method}',
            input_file,
            final_output_path_for_gdal # Pass the chosen base output directory
        ]

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
                # Construct the expected final output directory name created by gdal2tiles.exe
                base_name = os.path.splitext(os.path.basename(input_file))[0]
                actual_tiles_output = os.path.join(output_base_dir, f"{base_name}_tiles")

                self.status_label.config(text=f"Conversion completed successfully! Tiles in: {actual_tiles_output}", fg="green")
                messagebox.showinfo("Success", f"Conversion completed successfully!\nTiles created in directory:\n{actual_tiles_output}")
            else:
                self.status_label.config(text=f"Error in conversion. Exit code: {process.returncode}", fg="red")
                messagebox.showerror("Error", f"Error in conversion. Check output.\nExit code: {process.returncode}")

        except FileNotFoundError:
            self.status_label.config(text="Error: gdal2tiles.exe not found at the specified path. Ensure full and valid path.", fg="red")
            messagebox.showerror("Error", "gdal2tiles.exe not found. Ensure the full path you entered in the code is correct (e.g.: C:\\OSGeo4W\\apps\\Python312\\Scripts\\gdal2tiles.exe).")
        except Exception as e:
            self.status_label.config(text=f"An unexpected error occurred: {e}", fg="red")
            messagebox.showerror("General Error", f"An unexpected error occurred: {e}")
        finally:
            self.convert_button.config(state="normal") # Re-enable the button

if __name__ == "__main__":
    root = tk.Tk()
    
    app = MapTilerApp(root)
    root.mainloop()