import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from tkinter import ttk 
import os
import subprocess
import threading
import shutil

class MapTilerApp:
    def __init__(self, master):
        self.master = master
        master.title("GDAL Map Converter")
        master.geometry("750x800") 
        master.resizable(False, False)

        s = ttk.Style()
        s.theme_use('clam') 

        s.configure('TLabel', font=('Helvetica', 10)) 
        s.configure('TButton', font=('Helvetica', 10, 'bold')) 
        s.configure('TRadiobutton', font=('Helvetica', 10)) 
        s.configure('TEntry', font=('Helvetica', 10)) 
        s.configure('TCombobox', font=('Helvetica', 10)) 

        s.configure('Accent.TButton', background='#4CAF50', foreground='white', font=('Helvetica', 10, 'bold'))
        s.map('Accent.TButton',
              background=[('active', '#66BB6A')], 
              foreground=[('active', 'white')]) 

        self.status_font_config = ('Helvetica', 10, 'italic')
        self.output_font_config = ('Consolas', 9) 

        self.script_dir = os.path.dirname(os.path.abspath(__file__))

        self.input_file_path = "" # Will store the actual selected file path
        
        # --- FIXED: Initialize output_base_dir_var to an empty string ---
        self.output_base_dir_var = tk.StringVar(master, value="") 
        self.conversion_type_var = tk.StringVar(master, value="tiles")

        self.status_label = ttk.Label(master, text="Initializing GUI...", foreground="blue", font=self.status_font_config)
        self.output_text = scrolledtext.ScrolledText(master, wrap=tk.WORD, height=15, width=70, state="disabled", font=self.output_font_config, background="#f0f0f0")


        # --- Top Frame - Input File Selection ---
        self.input_frame = ttk.LabelFrame(master, text="Input Map File", padding=(10, 10, 10, 10)) 
        self.input_frame.pack(pady=10, padx=15, fill="x") 

        tk.Label(self.input_frame, text="Please select a map file (GeoTIFF, JPG, PNG etc.):", font=('Helvetica', 10)).pack(pady=5)
        
        self.input_path_entry = ttk.Entry(self.input_frame, width=80) 
        self.input_path_entry.pack(pady=5, padx=5) 
        self.input_path_entry.config(state="readonly")
        
        # Set initial display for input path to hint about selecting a file
        self.set_input_file_display("No file selected", is_file=False) # Changed initial hint


        ttk.Button(self.input_frame, text="Select Map File...", command=self.browse_input_file, style='Accent.TButton').pack(pady=5) 

        # --- Conversion Type Selection ---
        self.conversion_type_frame = ttk.LabelFrame(master, text="Conversion Type", padding=(10, 10, 10, 10))
        self.conversion_type_frame.pack(pady=10, padx=15, fill="x")

        self.tiles_radio = ttk.Radiobutton(self.conversion_type_frame, text="Generate Web Map Tiles (Creates new folder with tiles)", variable=self.conversion_type_var, value="tiles", command=self.toggle_options_visibility)
        self.tiles_radio.pack(anchor="w", padx=10, pady=2)

        self.overviews_radio = ttk.Radiobutton(self.conversion_type_frame, text="Add Internal Overviews (Creates a new GeoTIFF copy with overviews)", variable=self.conversion_type_var, value="overviews", command=self.toggle_options_visibility)
        self.overviews_radio.pack(anchor="w", padx=10, pady=2)

        self.srtm_radio = ttk.Radiobutton(self.conversion_type_frame, text="Convert to SRTMHGT (DTM in .hgt format)", variable=self.conversion_type_var, value="srtmhgt", command=self.toggle_options_visibility)
        self.srtm_radio.pack(anchor="w", padx=10, pady=2)

        print("[INFO] Conversion options initialized: 'tiles', 'overviews', 'srtmhgt'")

        
        # --- Output Directory Selection ---
        self.output_frame = ttk.LabelFrame(master, text="Base Output Directory", padding=(10, 10, 10, 10)) 
        self.output_frame.pack(pady=10, padx=15, fill="x")

        tk.Label(self.output_frame, text="Select a base directory to save the output:", font=('Helvetica', 10)).pack(pady=5)
        
        self.output_path_entry = ttk.Entry(self.output_frame, textvariable=self.output_base_dir_var, width=80) 
        self.output_path_entry.pack(pady=5, padx=5)
        self.output_path_entry.config(state="readonly")
        
        # --- NEW: Set initial display for output path ---
        self.set_output_dir_display("No directory selected (will default to input path)")


        ttk.Button(self.output_frame, text="Select Base Output Directory...", command=self.browse_output_dir, style='Accent.TButton').pack(pady=5)

        # --- Options Frame - Conversion Options ---
        self.options_frame = ttk.LabelFrame(master, text="Conversion Options", padding=(10, 10, 10, 10))
        self.options_frame.pack(pady=10, padx=15, fill="x")

        levels_inner_frame = ttk.Frame(self.options_frame)
        levels_inner_frame.pack(fill="x", pady=5)
        self.levels_label = ttk.Label(levels_inner_frame, text="Levels (e.g.: 2 4 8 16 for overviews; 0-16 for tiles):")
        self.levels_label.pack(side="left", padx=5)
        self.zoom_level_var = tk.StringVar(master, value="0-16")
        self.levels_entry = ttk.Entry(levels_inner_frame, textvariable=self.zoom_level_var, width=20) 
        self.levels_entry.pack(side="left", padx=5, expand=True, fill="x")

        resampling_inner_frame = ttk.Frame(self.options_frame)
        resampling_inner_frame.pack(fill="x", pady=5)
        ttk.Label(resampling_inner_frame, text="Resampling Method:").pack(side="left", padx=5)
        self.resampling_method_var = tk.StringVar(master, value="average")
        self.resampling_options = ["average", "nearest", "bilinear", "lanczos", "cubic", "cubicspline"] 
        self.resampling_menu = ttk.OptionMenu(resampling_inner_frame, self.resampling_method_var, self.resampling_options[0], *self.resampling_options)
        self.resampling_menu.pack(side="left", padx=5, expand=True, fill="x")


        # --- Conversion Button ---
        self.convert_button = ttk.Button(master, text="Start Conversion", command=self.start_conversion, style='Accent.TButton', width=20)
        self.convert_button.pack(pady=15)

        # --- Output Area for Status (packed at the bottom) ---
        self.status_label.pack(pady=5) 
        self.output_text.pack(pady=5, padx=15, fill="both", expand=True) 

        self.toggle_options_visibility()
        self.status_label.config(text="Ready. Please select an input file.")


    def toggle_options_visibility(self):
        conversion_type = self.conversion_type_var.get()
        print(f"[DEBUG] toggle_options_visibility called for conversion_type = {conversion_type}")
        if conversion_type == "tiles":
            self.levels_label.config(text="Zoom Levels (e.g.: 0-16):")
            self.levels_entry.config(state="normal")
            self.resampling_menu.config(state="normal")
            if not self.zoom_level_var.get() or self.zoom_level_var.get() == "2 4 8 16":
                self.zoom_level_var.set("0-16")
        elif conversion_type == "overviews":
            self.levels_label.config(text="Overview Levels (e.g.: 2 4 8 16):")
            self.levels_entry.config(state="normal")
            self.resampling_menu.config(state="normal")
            if not self.zoom_level_var.get() or self.zoom_level_var.get() == "0-16":
                self.zoom_level_var.set("2 4 8 16")
        else:  # srtmhgt
            self.levels_label.config(text="(No zoom levels for SRTMHGT)")
            self.levels_entry.config(state="disabled")
            self.resampling_menu.config(state="disabled")

    def browse_input_file(self):
        initial_dir = None
        if self.input_file_path and os.path.exists(self.input_file_path):
            initial_dir = os.path.dirname(self.input_file_path)
        else:
            initial_dir = self.script_dir 

        file_path = filedialog.askopenfilename(
            title="Select Map File",
            initialdir=initial_dir, 
            filetypes=(("Map files", "*.tif;*.tiff;*.jpg;*.jpeg;*.png;*.jp2"), ("All files", "*.*"))
        )
        if file_path:
            if self.conversion_type_var.get() == "overviews" and not file_path.lower().endswith(('.tif', '.tiff')):
                messagebox.showerror("Error", "For 'Add Internal Overviews', the input file MUST be a GeoTIFF (.tif/.tiff).")
                return 
            
            self.set_input_file_display(file_path, is_file=True)
            
            # --- NEW: Set output directory to input file's directory ---
            input_file_directory = os.path.dirname(file_path)
            self.output_base_dir_var.set(input_file_directory)
            # --- UPDATED: Call the new display function for output path ---
            self.set_output_dir_display(input_file_directory) 

            self.status_label.config(text=f"Input file selected. Output directory set to: {os.path.basename(input_file_directory)}")
            self.clear_output_text() 


    def browse_output_dir(self):
        initial_dir = None
        # Prioritize the directory of the selected input file
        if self.input_file_path and os.path.exists(self.input_file_path):
            initial_dir = os.path.dirname(self.input_file_path)
        # Otherwise, use the currently set output directory (which might be empty or a previous choice)
        elif self.output_base_dir_var.get() and os.path.isdir(self.output_base_dir_var.get()):
            initial_dir = self.output_base_dir_var.get()
        else:
            initial_dir = self.script_dir # Fallback to script directory

        dir_path = filedialog.askdirectory(
            title="Select Base Output Directory",
            initialdir=initial_dir 
        )
        if dir_path:
            self.output_base_dir_var.set(dir_path) 
            self.set_output_dir_display(dir_path) # Update display
            self.status_label.config(text=f"Base output directory selected: {os.path.basename(dir_path)}")
            self.clear_output_text()
            

    def set_input_file_display(self, path, is_file=False):
        self.input_path_entry.config(state="normal")
        self.input_path_entry.delete(0, tk.END)

        if is_file:
            self.input_file_path = path
            self.input_path_entry.insert(0, self.input_file_path)
        else:
            self.input_file_path = "" 
            self.input_path_entry.insert(0, path) 

        self.input_path_entry.config(state="readonly")
        # self.clear_output_text() # Clearing output text is now handled in browse_input_file

    # --- NEW FUNCTION: To manage output directory display ---
    def set_output_dir_display(self, path):
        self.output_path_entry.config(state="normal")
        self.output_path_entry.delete(0, tk.END)
        self.output_path_entry.insert(0, path)
        self.output_path_entry.config(state="readonly")


    def clear_output_text(self):
        self.output_text.config(state="normal")
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state="disabled")

    def update_output_text(self, text):
        self.output_text.config(state="normal")
        self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END) 
        self.output_text.config(state="disabled")

    def start_conversion(self):
        if not self.input_file_path or not os.path.exists(self.input_file_path):
            messagebox.showerror("Error", "Please select a valid input map file first.")
            return
        
        chosen_base_output_dir = self.output_base_dir_var.get()

        # --- IMPORTANT: Validate output directory *before* proceeding ---
        if not chosen_base_output_dir or not os.path.isdir(chosen_base_output_dir):
            messagebox.showerror("Error", "Please select a valid base output directory.")
            return
        
        input_file_base_name = os.path.splitext(os.path.basename(self.input_file_path))[0]
        
        conversion_type = self.conversion_type_var.get()

        print(f"[DEBUG] start_conversion triggered. Selected conversion_type: {conversion_type}")
        
        if conversion_type == "tiles":
            actual_output_dir = os.path.join(chosen_base_output_dir, f"{input_file_base_name}_tiles")
            if not os.path.exists(actual_output_dir):
                try:
                    os.makedirs(actual_output_dir)
                    self.update_output_text(f"Created output directory: {actual_output_dir}\n")
                except Exception as e:
                    messagebox.showerror("Error", f"Could not create output directory for tiles: {actual_output_dir}\nError: {e}")
                    return
        elif conversion_type == "overviews":
            print("[INFO] Using existing output directory for internal overviews...")
            actual_output_dir = chosen_base_output_dir

        elif conversion_type == "srtmhgt":
            print("[INFO] Using existing output directory for SRTMHGT conversion...")
            actual_output_dir = chosen_base_output_dir

        else:
            messagebox.showerror("Error", f"Unsupported conversion type: {conversion_type}")
            return

        self.clear_output_text()
        self.status_label.config(text="Starting conversion...", foreground="orange")
        self.convert_button.config(state="disabled") 

        self.conversion_thread = threading.Thread(target=self.run_gdal_command, args=(conversion_type, actual_output_dir,))
        self.conversion_thread.start()

    def run_gdal_command(self, conversion_type, actual_output_dir): 
        print(f"[DEBUG] run_gdal_command executing. Type: {conversion_type}, Output: {actual_output_dir}")
        input_file = self.input_file_path
        resampling_method = self.resampling_method_var.get()
        levels_input = self.zoom_level_var.get()

        command = []
        final_output_display_path = "" 

        script_dir = os.path.dirname(__file__)
        
        gdal2tiles_exe_path = os.path.join(script_dir, "bin", "gdal2tiles.exe") 
        gdaladdo_exe_path = os.path.join(script_dir, "bin", "gdaladdo.exe") 
        gdal_translate_exe_path = os.path.join(script_dir, "bin", "gdal_translate.exe")

        gdal_data_path = os.path.join(script_dir, "bin", "gdal-data") 
        
        env = os.environ.copy()
        env['GDAL_DATA'] = gdal_data_path

        if conversion_type == "tiles":
            print("[INFO] Running gdal2tiles command...")
            command = [
                gdal2tiles_exe_path,
                '-p', 'raster',
                '-z', levels_input, 
                f'--resampling={resampling_method}',
                input_file,
                actual_output_dir 
            ]
            final_output_display_path = actual_output_dir 

        elif conversion_type == "overviews":
            print("[INFO] Running gdaladdo command for internal overviews...")
            if not input_file.lower().endswith(('.tif', '.tiff')):
                self.update_output_text("Error: For overviews, the input file MUST be a GeoTIFF (.tif/.tiff).\n")
                messagebox.showerror("Error", "For 'Add Internal Overviews', the input file MUST be a GeoTIFF (.tif/.tiff).")
                self.status_label.config(text="Conversion failed.", foreground="red")
                self.convert_button.config(state="normal")
                return

            levels_list = levels_input.split()
            if not all(part.isdigit() for part in levels_list):
                self.update_output_text("Error: For overviews, 'Levels' must be space-separated integers (e.g., '2 4 8 16').\n")
                messagebox.showerror("Error", "For 'Add Internal Overviews', 'Levels' must be space-separated integers (e.g., '2 4 8 16').")
                self.status_label.config(text="Conversion failed.", foreground="red")
                self.convert_button.config(state="normal")
                return

            base_name = os.path.splitext(os.path.basename(input_file))[0]
            output_geotiff_name = f"{base_name}_with_overviews.tif"
            output_geotiff_path = os.path.join(actual_output_dir, output_geotiff_name) 
            final_output_display_path = output_geotiff_path

            self.update_output_text(f"Copying GeoTIFF to: {output_geotiff_path}\n")
            translate_command = [
                gdal_translate_exe_path,
                input_file,
                output_geotiff_path
            ]
            
            try:
                process_translate = subprocess.Popen(translate_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, universal_newlines=True, shell=True, env=env)
                for line in process_translate.stdout:
                    self.update_output_text(line)
                process_translate.wait()

                if process_translate.returncode != 0:
                    self.status_label.config(text=f"Error copying GeoTIFF. Exit code: {process_translate.returncode}", foreground="red")
                    messagebox.showerror("Error", f"Error copying GeoTIFF. Check output.\nExit code: {process_translate.returncode}")
                    self.convert_button.config(state="normal")
                    return

                self.update_output_text(f"GeoTIFF copied successfully.\n")

            except FileNotFoundError:
                self.status_label.config(text=f"Error: gdal_translate.exe not found at ({gdal_translate_exe_path}).", foreground="red")
                messagebox.showerror("Error", f"gdal_translate.exe not found. Ensure the full path is correct.")
                self.convert_button.config(state="normal")
                return
            except Exception as e:
                self.status_label.config(text=f"An error occurred during copying: {e}", foreground="red")
                messagebox.showerror("Error", f"An unexpected error occurred during copying: {e}")
                self.convert_button.config(state="normal")
                return
            
            self.update_output_text(f"Adding overviews to: {output_geotiff_path}\n")
            command = [
                gdaladdo_exe_path,
                '-r', resampling_method,
                output_geotiff_path, 
                *levels_list 
            ]

        elif conversion_type == "srtmhgt":
            print("[INFO] Running gdal_translate command for SRTMHGT conversion...")
            base_name = os.path.splitext(os.path.basename(input_file))[0]
            output_file_name = base_name + ".hgt"
            output_file_path = os.path.join(actual_output_dir, output_file_name)
            final_output_display_path = output_file_path

            command = [
                gdal_translate_exe_path,
                "-of", "SRTMHGT",
                input_file,
                output_file_path
            ]
            
        self.update_output_text(f"Running command:\n{' '.join(command)}\n\n")

        try:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, universal_newlines=True, shell=True, env=env)
            
            for line in process.stdout:
                self.update_output_text(line)
            process.wait() 

            for line in process.stdout:
                cleaned_line = line.strip() # Remove leading/trailing whitespace, including newline
                if cleaned_line: # Only print if there's actual content
                    self.update_output_text(cleaned_line + "\n") # Add one newline explicitly

            process.wait()

            if process.returncode == 0:
                success_message = ""
                if conversion_type == "tiles":
                    success_message = f"Conversion completed successfully! Tiles created in:\n{final_output_display_path}"
                else: # overviews
                    success_message = f"Internal overviews added successfully to new GeoTIFF:\n{final_output_display_path}"
                
                # Now the success message should appear as intended
                self.status_label.config(text=success_message, foreground="green")
                messagebox.showinfo("Success", success_message)
            else:
                self.status_label.config(text=f"Error in conversion. Exit code: {process.returncode}", foreground="red")
                messagebox.showerror("Error", f"Error in conversion. Check output.\nExit code: {process.returncode}")

        except FileNotFoundError:
            exe_name = "gdal2tiles.exe" if conversion_type == "tiles" else "gdaladdo.exe"
            error_msg = f"Error: {exe_name} not found at the specified path. Ensure the executable exists and the path is correct."
            self.status_label.config(text=error_msg, foreground="red")
            messagebox.showerror("Error", error_msg)
        except Exception as e:
            self.status_label.config(text=f"An unexpected error occurred: {e}", foreground="red")
            messagebox.showerror("General Error", f"An unexpected error occurred: {e}")
        finally:
            self.master.after(0, lambda: self.convert_button.config(state="normal"))
            print("[INFO] Conversion thread completed.")


if __name__ == "__main__":
    root = tk.Tk()
    
    app = MapTilerApp(root)
    root.mainloop()