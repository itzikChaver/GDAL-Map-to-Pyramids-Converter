import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os
import subprocess
import threading # To run the command in the background so the GUI doesn't freeze
import shutil # For copying files

class MapTilerApp:
    def __init__(self, master):
        self.master = master
        master.title("GDAL Map Converter")
        master.geometry("700x650") # Increased height slightly for new options
        master.resizable(False, False) # Prevents window resizing

        self.input_file_path = None
        self.output_dir_path = tk.StringVar(master) # Variable to store output directory path
        self.conversion_type_var = tk.StringVar(master, value="tiles") # Default to "tiles"

        # --- Top Frame - Input File Selection ---
        self.input_frame = tk.LabelFrame(master, text="Input Map File", bd=2, relief="groove")
        self.input_frame.pack(pady=10, padx=10, fill="x")

        tk.Label(self.input_frame, text="Please select a map file (GeoTIFF, JPG, PNG etc.):").pack(pady=5)
        
        self.input_path_entry = tk.Entry(self.input_frame, width=80)
        self.input_path_entry.pack(pady=5)
        self.input_path_entry.config(state="readonly")

        self.browse_input_button = tk.Button(self.input_frame, text="Select Map File...", command=self.browse_input_file)
        self.browse_input_button.pack(pady=5)

        # --- Conversion Type Selection ---
        self.conversion_type_frame = tk.LabelFrame(master, text="Conversion Type", bd=2, relief="groove")
        self.conversion_type_frame.pack(pady=10, padx=10, fill="x")

        self.tiles_radio = tk.Radiobutton(self.conversion_type_frame, text="Generate Web Map Tiles (Creates new folder with tiles)",
                                          variable=self.conversion_type_var, value="tiles", command=self.toggle_options_visibility)
        self.tiles_radio.pack(anchor="w", padx=5, pady=2)

        self.overviews_radio = tk.Radiobutton(self.conversion_type_frame, text="Add Internal Overviews (Creates a new GeoTIFF copy with overviews)",
                                             variable=self.conversion_type_var, value="overviews", command=self.toggle_options_visibility)
        self.overviews_radio.pack(anchor="w", padx=5, pady=2)
        
        # --- Output Directory Selection (visible for both types now) ---
        self.output_frame = tk.LabelFrame(master, text="Output Directory", bd=2, relief="groove") # Moved outside conversion_type_frame
        self.output_frame.pack(pady=10, padx=10, fill="x")

        tk.Label(self.output_frame, text="Select a directory to save the output:").pack(pady=5)
        
        self.output_path_entry = tk.Entry(self.output_frame, textvariable=self.output_dir_path, width=80)
        self.output_path_entry.pack(pady=5)
        self.output_path_entry.config(state="readonly")

        self.browse_output_button = tk.Button(self.output_frame, text="Select Output Directory...", command=self.browse_output_dir)
        self.browse_output_button.pack(pady=5)

        # --- Options Frame - Conversion Options ---
        self.options_frame = tk.LabelFrame(master, text="Conversion Options", bd=2, relief="groove")
        self.options_frame.pack(pady=10, padx=10, fill="x")

        # Zoom/Overview Levels
        self.levels_label = tk.Label(self.options_frame, text="Levels (e.g.: 2 4 8 16 for overviews; 0-16 for tiles):")
        self.levels_label.pack(side="left", padx=5)
        self.zoom_level_var = tk.StringVar(master, value="0-16")
        self.levels_entry = tk.Entry(self.options_frame, textvariable=self.zoom_level_var, width=20)
        self.levels_entry.pack(side="left", padx=5)

        # Resampling Method
        tk.Label(self.options_frame, text="Resampling Method:").pack(side="left", padx=5)
        self.resampling_method_var = tk.StringVar(master, value="average")
        self.resampling_options = ["average", "nearest", "bilinear", "lanczos"]
        self.resampling_menu = tk.OptionMenu(self.options_frame, self.resampling_method_var, *self.resampling_options)
        self.resampling_menu.pack(side="left", padx=5)

        # --- Conversion Button ---
        self.convert_button = tk.Button(master, text="Start Conversion", command=self.start_conversion)
        self.convert_button.pack(pady=10)

        # --- Output Area for Status ---
        self.status_label = tk.Label(master, text="Ready...", fg="blue")
        self.status_label.pack(pady=5)

        self.output_text = scrolledtext.ScrolledText(master, wrap=tk.WORD, height=8, width=70, state="disabled")
        self.output_text.pack(pady=5, padx=10, fill="both", expand=True)

        # Initial state setup
        self.toggle_options_visibility()


    def toggle_options_visibility(self):
        """Adjusts labels and entry states based on conversion type."""
        conversion_type = self.conversion_type_var.get()
        if conversion_type == "tiles":
            self.levels_label.config(text="Zoom Levels (e.g.: 0-16):")
            if not self.zoom_level_var.get(): # Set default if empty
                self.zoom_level_var.set("0-16")
            
            # Auto-populate output directory if an input file is already selected
            if self.input_file_path:
                base_name = os.path.splitext(os.path.basename(self.input_file_path))[0]
                default_output_path = os.path.join(os.path.dirname(self.input_file_path), f"{base_name}_tiles")
                self.output_dir_path.set(default_output_path)


        else: # "overviews" selected
            self.levels_label.config(text="Overview Levels (e.g.: 2 4 8 16):")
            if not self.zoom_level_var.get() or self.zoom_level_var.get() == "0-16": # Set default if empty or was tiles default
                self.zoom_level_var.set("2 4 8 16")

            # For overviews, the output file is named after input, placed in selected output folder
            if self.input_file_path and self.output_dir_path.get() == os.path.join(os.path.dirname(self.input_file_path), f"{os.path.splitext(os.path.basename(self.input_file_path))[0]}_tiles"):
                 # Clear default if it was tiles default and switch to overviews
                 self.output_dir_path.set("")


    def browse_input_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Map File",
            filetypes=(("Map files", "*.tif;*.tiff;*.jpg;*.jpeg;*.png;*.jp2"), ("All files", "*.*"))
        )
        if file_path:
            # For overviews, the input file MUST be a GeoTIFF
            if self.conversion_type_var.get() == "overviews" and not file_path.lower().endswith(('.tif', '.tiff')):
                messagebox.showerror("Error", "For 'Add Internal Overviews', the input file MUST be a GeoTIFF (.tif/.tiff).")
                self.set_input_file(None) # Clear selection
                return

            self.set_input_file(file_path)
            self.toggle_options_visibility() # Update output path based on new input and conversion type


    def browse_output_dir(self):
        dir_path = filedialog.askdirectory(
            title="Select Output Directory"
        )
        if dir_path:
            self.output_dir_path.set(dir_path)
            self.status_label.config(text=f"Output directory selected: {os.path.basename(dir_path)}")
            self.clear_output_text()


    def set_input_file(self, file_path):
        self.input_file_path = file_path
        self.input_path_entry.config(state="normal")
        self.input_path_entry.delete(0, tk.END)
        if file_path:
            self.input_path_entry.insert(0, self.input_file_path)
            self.status_label.config(text=f"Input file selected: {os.path.basename(file_path)}")
        else:
            self.input_path_entry.insert(0, "")
            self.status_label.config(text="No input file selected.")
        self.input_path_entry.config(state="readonly")
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
        
        conversion_type = self.conversion_type_var.get()
        chosen_output_dir = self.output_dir_path.get()

        if not chosen_output_dir: # Output directory is required for both now
            messagebox.showerror("Error", "Please select an output directory.")
            return
        
        # Ensure the chosen output directory exists
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
        self.conversion_thread = threading.Thread(target=self.run_gdal_command, args=(conversion_type, chosen_output_dir,))
        self.conversion_thread.start()

    def run_gdal_command(self, conversion_type, output_base_dir):
        input_file = self.input_file_path
        resampling_method = self.resampling_method_var.get()
        levels_input = self.zoom_level_var.get() # Renamed from zoom_levels for clarity

        command = []
        final_output_display_path = "" # What will be shown in the success message

        # --- Define Paths to GDAL Executables within the project's 'bin' folder ---
        # Get the directory where the current script (map_tiler_gui.py) is located
        script_dir = os.path.dirname(__file__)
        
        # Construct the full paths to the GDAL executables in the 'bin' folder
        gdal2tiles_exe_path = os.path.join(script_dir, "bin", "gdal2tiles.exe") 
        gdaladdo_exe_path = os.path.join(script_dir, "bin", "gdaladdo.exe") 
        gdal_translate_exe_path = os.path.join(script_dir, "bin", "gdal_translate.exe")

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

        if conversion_type == "tiles":
            # --- gdal2tiles.exe Logic ---
            command = [
                gdal2tiles_exe_path,
                '-p', 'raster',
                '-z', levels_input, # Use '0-16' format for gdal2tiles
                f'--resampling={resampling_method}',
                input_file,
                output_base_dir # gdal2tiles.exe will create a subfolder here
            ]
            base_name = os.path.splitext(os.path.basename(input_file))[0]
            final_output_display_path = os.path.join(output_base_dir, f"{base_name}_tiles")

        elif conversion_type == "overviews":
            # --- gdal_translate + gdaladdo Logic ---
            # 1. Validate input file type (already done in browse_input_file)
            if not input_file.lower().endswith(('.tif', '.tiff')):
                 self.update_output_text("Error: For overviews, the input file MUST be a GeoTIFF (.tif/.tiff).\n")
                 messagebox.showerror("Error", "For 'Add Internal Overviews', the input file MUST be a GeoTIFF (.tif/.tiff).")
                 self.status_label.config(text="Conversion failed.", fg="red")
                 self.convert_button.config(state="normal")
                 return

            # 2. Validate overview levels format
            levels_list = levels_input.split()
            if not all(part.isdigit() for part in levels_list):
                 self.update_output_text("Error: For overviews, 'Levels' must be space-separated integers (e.g., '2 4 8 16').\n")
                 messagebox.showerror("Error", "For 'Add Internal Overviews', 'Levels' must be space-separated integers (e.g., '2 4 8 16').")
                 self.status_label.config(text="Conversion failed.", fg="red")
                 self.convert_button.config(state="normal")
                 return

            # Define the new output GeoTIFF filename
            base_name = os.path.splitext(os.path.basename(input_file))[0]
            output_geotiff_name = f"{base_name}_with_overviews.tif"
            output_geotiff_path = os.path.join(output_base_dir, output_geotiff_name)
            final_output_display_path = output_geotiff_path

            # A. First, create a copy of the GeoTIFF using gdal_translate
            self.update_output_text(f"Copying GeoTIFF to: {output_geotiff_path}\n")
            translate_command = [
                gdal_translate_exe_path,
                input_file,
                output_geotiff_path
            ]
            
            try:
                process_translate = subprocess.Popen(translate_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, universal_newlines=True, shell=True, env=os.environ.copy())
                for line in process_translate.stdout:
                    self.update_output_text(line)
                process_translate.wait()

                if process_translate.returncode != 0:
                    self.status_label.config(text=f"Error copying GeoTIFF. Exit code: {process_translate.returncode}", fg="red")
                    messagebox.showerror("Error", f"Error copying GeoTIFF. Check output.\nExit code: {process_translate.returncode}")
                    self.convert_button.config(state="normal")
                    return

                self.update_output_text(f"GeoTIFF copied successfully.\n")

            except FileNotFoundError:
                self.status_label.config(text=f"Error: gdal_translate.exe not found at the specified path ({gdal_translate_exe_path}).", fg="red")
                messagebox.showerror("Error", f"gdal_translate.exe not found. Ensure the full path you entered in the code is correct.")
                self.convert_button.config(state="normal")
                return
            except Exception as e:
                self.status_label.config(text=f"An error occurred during copying: {e}", fg="red")
                messagebox.showerror("Error", f"An unexpected error occurred during copying: {e}")
                self.convert_button.config(state="normal")
                return
            
            # B. Second, add overviews to the copied GeoTIFF using gdaladdo
            self.update_output_text(f"Adding overviews to: {output_geotiff_path}\n")
            command = [
                gdaladdo_exe_path,
                '-r', resampling_method,
                output_geotiff_path, # Operate on the copy
                *levels_list # Unpack the list of level strings as separate arguments
            ]
            
        self.update_output_text(f"Running command:\n{' '.join(command)}\n\n")

        try:
            # Execute the GDAL command (gdal2tiles or gdaladdo on the copy)
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, universal_newlines=True, shell=True, env=os.environ.copy())
            
            for line in process.stdout:
                self.update_output_text(line)
            process.wait() # Wait for the process to finish

            if process.returncode == 0:
                success_message = ""
                if conversion_type == "tiles":
                    success_message = f"Conversion completed successfully! Tiles created in:\n{final_output_display_path}"
                else: # overviews
                    success_message = f"Internal overviews added successfully to new GeoTIFF:\n{final_output_display_path}"

                self.status_label.config(text=success_message, fg="green")
                messagebox.showinfo("Success", success_message)
            else:
                self.status_label.config(text=f"Error in conversion. Exit code: {process.returncode}", fg="red")
                messagebox.showerror("Error", f"Error in conversion. Check output.\nExit code: {process.returncode}")

        except FileNotFoundError:
            exe_name = "gdal2tiles.exe" if conversion_type == "tiles" else "gdaladdo.exe"
            error_msg = f"Error: {exe_name} not found at the specified path. Ensure full and valid path."
            self.status_label.config(text=error_msg, fg="red")
            messagebox.showerror("Error", error_msg)
        except Exception as e:
            self.status_label.config(text=f"An unexpected error occurred: {e}", fg="red")
            messagebox.showerror("General Error", f"An unexpected error occurred: {e}")
        finally:
            self.convert_button.config(state="normal") # Re-enable the button

if __name__ == "__main__":
    root = tk.Tk()
    
    app = MapTilerApp(root)
    root.mainloop()