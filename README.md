# GDAL Map to Pyramids Converter

This project provides a user-friendly Graphical User Interface (GUI) built with Tkinter for converting large geospatial image files (such as GeoTIFFs, JPGs, PNGs) into a web-optimized tile pyramid structure using `gdal2tiles.exe` from the GDAL/OGR library. This allows for efficient display of large maps in web applications (like OpenLayers, Leaflet, Google Maps API) by serving map tiles at various zoom levels.

## Table of Contents

1.  [About the Project](#1-about-the-project)
2.  [Supported Map Formats and the Conversion Process](#2-supported-map-formats-and-the-conversion-process)
      * [Supported Input Formats](#supported-input-formats)
      * [The Tiling Process (GDAL2Tiles)](#the-tiling-process-gdal2tiles)
      * [Output Structure](#output-structure)
3.  [Prerequisites](#3-prerequisites)
      * [Python 3](#python-3)
      * [OSGeo4W (GDAL)](#osgeo4w-gdal)
4.  [Installation Guide](#4-installation-guide)
      * [Step 1: Install Python 3](#step-1-install-python-3)
      * [Step 2: Install OSGeo4W (GDAL)](#step-2-install-osgeo4w-gdal)
          * [Important Note on 32-bit vs. 64-bit](#important-note-on-32-bit-vs-64-bit)
          * [Finding the gdal2tiles.exe Path](#finding-the-gdal2tilesexe-path)
      * [Step 3: Download the Project Script](#step-3-download-the-project-script)
      * [Step 4: Configure the Script (Crucial\!)](#step-4-configure-the-script-crucial)
5.  [How to Use](#5-how-to-use)
6.  [Troubleshooting](#6-troubleshooting)
7.  [License](#7-license)
8.  [Contact](#8-contact)

## 1\. About the Project

Working with high-resolution geospatial images on the web can be challenging due to their large file sizes. This project offers a simple, intuitive GUI to leverage `gdal2tiles.exe` – a powerful utility from the GDAL (Geospatial Data Abstraction Library) suite – to convert these large images into a "tile pyramid."

A tile pyramid is a collection of smaller image files (tiles) organized into different zoom levels. When a user zooms in or out on a map, only the necessary tiles for that specific view and zoom level are loaded, leading to a much smoother and faster user experience compared to loading one massive image.

## 2\. Supported Map Formats and the Conversion Process

### Supported Input Formats

The underlying `gdal2tiles.exe` utility, being part of GDAL, supports a vast array of raster formats. Common input formats include, but are not limited to:

  * **GeoTIFF (`.tif`, `.tiff`):** A standard format for geospatial raster data, often containing georeferencing information.
  * **JPEG (`.jpg`, `.jpeg`):** Common image format, good for photographic maps.
  * **PNG (`.png`):** Good for maps with transparent areas or sharp lines.
  * **JPEG2000 (`.jp2`):** A modern compression format, often used in geospatial contexts.

Generally, if GDAL can read it, this tool can process it. The GUI is configured to show common map file extensions but allows selecting "All files" (`*.*`).

### The Tiling Process (GDAL2Tiles)

The `gdal2tiles.exe` utility takes your input map and performs the following key operations:

  * **Pyramid Generation:** It creates multiple sets of tiles, each corresponding to a different zoom level. The highest zoom level (e.g., 16) contains the most detailed tiles, while the lowest (e.g., 0) represents the entire map in a single tile.
  * **Resampling:** As tiles are generated for different zoom levels, they need to be resampled (resized) from the original data. You can choose different resampling methods in the GUI:
      * `average`: Computes the average of all contributing pixels. Good for continuous data.
      * `nearest`: Uses the value of the nearest pixel. Fastest, but can produce blocky results.
      * `bilinear`: Uses a weighted average of the 4 nearest pixels. Smoother than nearest, but can blur sharp details.
      * `lanczos`: A more advanced interpolation method, often producing high-quality results.
  * **Georeferencing:** If your input file is georeferenced (e.g., a GeoTIFF), `gdal2tiles.exe` will automatically handle the spatial referencing, ensuring the tiles are positioned correctly on a web map.
  * **Output Folder Structure:** The output is a hierarchical folder structure where each folder represents a zoom level, and subfolders represent X and Y coordinates of the tiles.

### Output Structure

The output will be a new directory created next to your input map file, named `[original_filename]_tiles`. Inside this directory, you will find:

  * **`tiles/`**: This sub-directory contains the generated image tiles (`.png` or `.jpg` depending on `gdal2tiles` settings). The structure is typically `tiles/{z}/{x}/{y}.png`, where `{z}` is the zoom level, `{x}` is the column, and `{y}` is the row.
  * **`googlemaps.html`, `openlayers.html`, `leaflet.html`**: Sample HTML files that demonstrate how to load and display your generated tiles using popular web mapping libraries (Google Maps API, OpenLayers, Leaflet). These are excellent starting points for integrating your maps into a web application.
  * **`tilemapresource.xml`**: An XML file describing the tile set, including its bounding box, zoom levels, and tile dimensions.

## 3\. Prerequisites

Before running this script, you need to have Python and OSGeo4W (which includes GDAL) installed on your system.

### Python 3

  * **Version:** Python 3.6 or higher is recommended.
  * **Tkinter:** Tkinter is usually included with standard Python installations on Windows. If you installed Python via a custom method or on Linux/macOS, you might need to install it separately (e.g., `sudo apt-get install python3-tk` on Debian/Ubuntu).

### OSGeo4W (GDAL)

This script relies on the `gdal2tiles.exe` executable, which is part of the GDAL/OGR geospatial library. The easiest way to get GDAL on Windows is through the OSGeo4W installer.

## 4\. Installation Guide

Follow these steps carefully to set up your environment:

### Step 1: Install Python 3

1.  **Download Python:** Go to the official Python website: [python.org/downloads/](https://www.python.org/downloads/)
2.  **Run the Installer:**
      * When running the installer, **very important:** make sure to check the box that says **"Add Python to PATH"** (or similar, depending on the version). This will make it easier to run Python scripts from your command line.
      * Choose "Customize installation" to ensure Tkinter is selected (it usually is by default).
      * Install Python to a default location (e.g., `C:\Users\<YourUser>\AppData\Local\Programs\Python\Python3XX`).

### Step 2: Install OSGeo4W (GDAL)

OSGeo4W provides a convenient way to install GDAL and other open-source geospatial tools on Windows.

1.  **Download OSGeo4W Installer:** Go to the OSGeo4W website: [OSGeo4W Download Page](https://trac.osgeo.org/osgeo4w/)
      * Download the **`osgeo4w-setup-x86_64.exe`** for a 64-bit installation (recommended).
2.  **Run the OSGeo4W Installer:**
      * Select **"Advanced Install"**.
      * Choose **"Install from Internet"**.
      * Follow the prompts for download directory and local package directory (defaults are usually fine).
      * Select your internet connection type.
      * Choose a download site (any mirror is usually fine).
      * **Crucial Step: Select Packages.**
          * Under the **`Libs`** category, select **`gdal`**. Click on the "Skip" column next to `gdal` until you see the latest version number.
          * Under the **`Python`** category:
              * Select **`python3`** (or `python312` if available and you want that specific version). Click "Skip" until the version number appears.
              * **Crucially, select `python3-gdal`** (or `python312-gdal` if a specific version is listed). This package provides the Python bindings and utilities like `gdal2tiles.exe`. Click "Skip" until the version number appears.
              * Select **`python3-tk`** (or `python312-tk`) to ensure Tkinter support within the OSGeo4W Python environment, although our script uses your main Python's Tkinter.
          * (Optional but Recommended): Consider installing `qgis` from the `Desktop` or `GIS` category. This will pull in many common dependencies that are useful for geospatial work.
      * Click **"Next"**. The installer will show you a list of additional dependencies. **Accept all of them.**
      * Proceed with the installation. This may take some time depending on your internet speed and selected packages.

#### Important Note on 32-bit vs. 64-bit

Ensure consistency in your OSGeo4W installation. If you install the 64-bit version (`osgeo4w-setup-x86_64.exe`), all components (`gdal`, `python`, `python3-gdal`) should reside under a 64-bit path (e.g., `C:\OSGeo4W64`). Mixing 32-bit and 64-bit components can lead to "WinError 193" (entry point not found) or other compatibility issues.

#### Finding the `gdal2tiles.exe` Path

After installing OSGeo4W, you need to find the exact path to `gdal2tiles.exe`.

1.  **Open "OSGeo4W Shell"** from your Windows Start Menu. (This is a specific command line environment configured for OSGeo4W).
2.  In the OSGeo4W Shell, type the following command and press Enter:
    ```bash
    where gdal2tiles.exe
    ```
3.  **Note down the exact path** that is returned (e.g., `C:\OSGeo4W\apps\Python312\Scripts\gdal2tiles.exe`). This path is **CRUCIAL** for configuring the Python script.

### Step 3: Download the Project Script

1.  Create a folder on your computer for this project (e.g., `C:\Users\YourUser\Desktop\map_tiler_gui`).
2.  Save the provided Python script (the one with the GUI code) into this folder. You can name it `map_tiler_gui.py`.

### Step 4: Configure the Script (Crucial\!)

You need to update the `map_tiler_gui.py` script with the exact path to your `gdal2tiles.exe` executable.

1.  Open `map_tiler_gui.py` in a text editor (like Notepad++, VS Code, Sublime Text, or even Windows Notepad).

2.  Scroll down to the `run_gdal2tiles` function.

3.  Locate the line that defines `gdal2tiles_exe_path`:

    ```python
    gdal2tiles_exe_path = r"C:\OSGeo4W\apps\Python312\Scripts\gdal2tiles.exe" # ENSURE THIS PATH IS CORRECT FOR YOUR SYSTEM!
    ```

4.  **Replace** `C:\OSGeo4W\apps\Python312\Scripts\gdal2tiles.exe` with the exact path you found in **Step 2.4 (Finding the gdal2tiles.exe Path)**.

      * **Example:** If `where gdal2tiles.exe` returned `C:\OSGeo4W64\bin\gdal2tiles.exe`, then you would change the line to:
        ```python
        gdal2tiles_exe_path = r"C:\OSGeo4W64\bin\gdal2tiles.exe"
        ```
      * **Important:** Use raw strings (the `r` before the opening quote) for paths to avoid issues with backslashes.

5.  **Save** the `map_tiler_gui.py` file after making this change.

## 5\. How to Use

Once all prerequisites are installed and the script is configured, you can run the application:

1.  **Open a standard Windows Command Prompt (CMD) or PowerShell.** **Do NOT use the OSGeo4W Shell for this step.**

2.  **Navigate to your project directory** using the `cd` command:

    ```bash
    cd C:\Users\YourUser\Desktop\map_tiler_gui
    ```

    (Replace `C:\Users\YourUser\Desktop\map_tiler_gui` with the actual path where you saved `map_tiler_gui.py`).

3.  **Run the Python script:**

    ```bash
    "C:\Users\YourUser\AppData\Local\Programs\Python\Python312\python.exe" map_tiler_gui.py
    ```

    (Replace `C:\Users\YourUser\AppData\Local\Programs\Python\Python312\python.exe` with the actual path to your main Python executable, which typically resides in your AppData folder).

4.  **Using the GUI:**

      * **Select Map File:** Click the "Select Map File..." button and browse to your input image file (e.g., a `.tif`, `.jpg`, or `.png`).
      * **Zoom Levels:** Adjust the "Zoom Levels" range (e.g., `0-16`). `0` is the lowest zoom (entire map as one tile), and higher numbers mean more detail and more tiles.
      * **Resampling Method:** Choose a resampling method from the dropdown (e.g., `average`, `nearest`, `bilinear`, `lanczos`).
      * **Convert:** Click the "Convert Map to Pyramids" button.
          * If an output directory with the same name already exists, the script will ask for confirmation to delete its contents before proceeding.
          * The conversion process will start, and the output console will display progress messages from `gdal2tiles.exe`.
          * The GUI will remain responsive thanks to the threading.
      * **Completion:** Upon successful completion, a success message will appear, and the status label will turn green. The generated tiles will be in a new folder (e.g., `your_map_tiles`) in the same directory as your input file.

## 6\. Troubleshooting

  * **`FileNotFoundError: [WinError 2] The system cannot find the file specified`**:
      * This almost always means the path to `gdal2tiles.exe` configured in your script (`gdal2tiles_exe_path`) is incorrect.
      * Go back to **Step 2.4** and **Step 4** of the installation guide and re-verify the path. Ensure there are no typos, and it exactly matches the output from `where gdal2tiles.exe` in the OSGeo4W Shell.
  * **`WinError 193: %1 is not a valid Win32 application`**:
      * This typically indicates a mismatch between 32-bit and 64-bit components.
      * Ensure you downloaded and installed the 64-bit OSGeo4W installer (`osgeo4w-setup-x86_64.exe`).
      * Confirm that all paths within your OSGeo4W installation (e.g., to `gdal2tiles.exe`) consistently point to a `C:\OSGeo4W64\` directory (if you chose 64-bit) and not a mixed `C:\OSGeo4W\` and `C:\OSGeo4W64\` setup. If inconsistencies persist, a clean reinstallation of OSGeo4W (deleting the old folder first) is recommended.
  * **`ModuleNotFoundError: No module named 'osgeo'`**:
      * This error occurred when trying to run `gdal2tiles.py` via `python.exe` in the past. By switching to `gdal2tiles.exe` directly, this specific error should no longer appear with *this* script. If it appears while trying to run the `gdal2tiles.exe` command itself, it implies a deeper issue within your OSGeo4W GDAL installation that might require re-installing `python3-gdal` through the OSGeo4W installer.
  * **GUI is unresponsive/freezes:**
      * The script uses threading to prevent this, but if it still happens, it might be due to very large input files or extremely high zoom levels overwhelming your system resources. Monitor task manager.
  * **"Error deleting existing directory"**:
      * Ensure the output directory is not open in another application or explorer window, which might lock files and prevent deletion.

## 7\. License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 8\. Contact

For questions or support, please open an issue on the GitHub repository (if applicable) or contact haveritzik@gmail.com.