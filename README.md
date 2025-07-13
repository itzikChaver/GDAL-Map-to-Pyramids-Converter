# GDAL Map Converter GUI

## A User-Friendly Tool for Geospatial Image Processing

This project provides an intuitive **Graphical User Interface (GUI)** built with Python’s Tkinter library to simplify common geospatial raster processing tasks by leveraging the powerful **GDAL/OGR library**.
It makes several advanced operations accessible to non-technical users, combining flexibility, safety, and ease of use.

The tool currently supports three key conversion workflows:

1. **Generating Web Map Tiles (using `gdal2tiles.exe`):**
   Converts large geospatial image files (such as GeoTIFFs, JPEGs, PNGs, etc.) into a web‑optimized tile pyramid.
   This is essential for efficiently displaying large maps in web applications (e.g., OpenLayers, Leaflet, Google Maps) by serving small, pre‑rendered tiles at different zoom levels, greatly improving performance and responsiveness.

2. **Adding Internal Overviews to GeoTIFFs (using `gdal_translate.exe` and `gdaladdo.exe`):**
   Creates an optimized copy of an existing GeoTIFF and embeds internal overviews (also known as pyramids or Reduced Resolution Datasets – RRDs).
   These pre‑computed lower‑resolution layers enable much faster rendering when zooming out in desktop GIS applications (such as QGIS, ArcGIS, Global Mapper), as the software can read from the overviews instead of resampling the full‑resolution data on the fly.

3. **TIFF/GeoTIFF in DTM format to SRTMHGT format (using `gdal_translate.exe`):**
   Converts a digital terrain model (DTM) stored in TIFF or GeoTIFF format into the standardized **SRTMHGT** format (`.hgt` files).
   The SRTMHGT format is widely used for terrain visualization, GIS analysis, simulation tools, and 3D applications because it uses a fixed grid (typically 1201×1201 samples per 1°×1° tile) compatible with SRTM datasets.

> ⚙ Internally, the tool assembles and runs the relevant GDAL command‑line utilities, while keeping the process user‑friendly through its GUI.

---

## Table of Contents

1.  [Features & Benefits](#1-features--benefits)
2.  [Conversion Options & Process Explained](#2-conversion-options--process-explained)
    * [Supported Input Formats](#supported-input-formats)
    * [Option 1: Generate Web Map Tiles](#option-1-generate-web-map-tiles)
    * [Option 2: Add Internal Overviews](#option-2-add-internal-overviews)
    * [Option 3: DTM to SRTMHGT](#option-3-DTM-to-SRTMHGT)
    * [Common Option: Resampling Method](#common-option-resampling-method)
3.  [Prerequisites](#3-prerequisites)
    * [Python 3](#python-3)
    * [GDAL Binaries & Dependencies](#gdal-binaries--dependencies)
4.  [Installation Guide](#4-installation-guide)
    * [Step 1: Install Python 3](#step-1-install-python-3)
    * [Step 2: Obtain GDAL Binaries and Dependencies](#step-2-obtain-gdal-binaries-and-dependencies)
    * [Step 3: Download and Structure the Project](#step-3-download-and-structure-the-project)
5.  [How to Use the GUI](#5-how-to-use-the-gui)
6.  [Troubleshooting Common Issues](#6-troubleshooting-common-issues)
7.  [License](#7-license)
8.  [Contact](#8-contact)

---

## 1. Features & Benefits

* **User-Friendly GUI:** Simple and intuitive interface built with Tkinter, making complex GDAL operations accessible to users without command-line expertise.
* **Dual Functionality:** Supports both web map tile generation and GeoTIFF optimization (adding overviews) within a single application.
* **Safe Operation:** When adding overviews, the tool creates a *copy* of your original GeoTIFF, ensuring your source data remains untouched.
* **Background Processing:** Utilizes threading to run GDAL commands in the background, keeping the GUI responsive during long conversion processes.
* **Real-time Output:** Displays live command-line output from GDAL tools directly in the GUI, providing transparency and progress feedback.
* **Portable Design:** Designed to be self-contained by including GDAL binaries and dependencies within the project folder, reducing reliance on system-wide OSGeo4W installations (after initial setup).
* **Flexible Options:** Allows users to define zoom/overview levels and select resampling methods.

## 2. Conversion Options & Process Explained

The GUI offers two distinct conversion modes, each tailored for different use cases:

### Supported Input Formats

The underlying GDAL utilities (`gdal2tiles`, `gdaladdo`, `gdal_translate`) are highly versatile and support a vast array of raster formats. Common input formats include, but are not limited to:

* **GeoTIFF (`.tif`, `.tiff`):** The most common and robust format for georeferenced raster data, often containing embedded spatial information.
* **JPEG (`.jpg`, `.jpeg`):** A widely used compressed image format, suitable for photographic maps.
* **PNG (`.png`):** A lossless image format, excellent for maps with transparent areas, sharp lines, or specific color palettes.
* **JPEG2000 (`.jp2`):** A modern, highly compressed image format often used in professional geospatial contexts.
* **Many Others:** Generally, if GDAL can read a raster format, this tool can process it. The file dialog is pre-configured to show common map file extensions but also allows selecting "All files" (`*.*`).

### Option 1: Generate Web Map Tiles

This mode utilizes `gdal2tiles.exe` to create a hierarchical structure of image tiles suitable for web mapping applications.

* **Purpose:** To efficiently display large maps on websites by loading only the visible portions at appropriate resolutions, rather than the entire large image.
* **Conversion Process:**
    1.  The input map file is read by `gdal2tiles.exe`.
    2.  `gdal2tiles` generates multiple sets of smaller image files (tiles), each corresponding to a different **zoom level**.
    3.  The lowest zoom level (e.g., `0`) represents the entire map in a single or few tiles, while the highest zoom level contains the most detailed tiles, often matching the original map's resolution.
    4.  If the input file is georeferenced (e.g., a GeoTIFF), `gdal2tiles` automatically handles the spatial referencing and projection to a web-friendly Mercator projection (EPSG:3857).
* **Output Structure:**
    * The output is a new directory created within your chosen output folder. By default, it's named `[original_filename]_tiles`.
    * **`tiles/`**: This subdirectory contains the generated image tiles, organized into a standard web map tiling scheme: `tiles/{z}/{x}/{y}.png` (or `.jpg`), where `{z}` is the zoom level, `{x}` is the tile column, and `{y}` is the tile row.
    * **`googlemaps.html`, `openlayers.html`, `leaflet.html`**: Sample HTML files that demonstrate how to load and display your generated tiles using popular web mapping libraries. These serve as excellent starting points for integrating your maps into a web application.
    * **`tilemapresource.xml`**: An XML file describing the tile set, including its bounding box, supported zoom levels, and tile dimensions. This file can be useful for configuring web mapping clients.
* **"Levels" Option:** For tile generation, you specify the desired zoom levels as a **range** (e.g., `0-16`, meaning zoom levels 0 through 16 will be generated).

### Option 2: Add Internal Overviews

This mode leverages `gdal_translate.exe` to copy the input GeoTIFF and then `gdaladdo.exe` to embed internal overviews (also known as pyramids) directly into the new GeoTIFF copy.

* **Purpose:** To significantly enhance the display performance of large GeoTIFFs in desktop Geographic Information System (GIS) software. When a GIS application needs to display a large GeoTIFF at a zoomed-out (lower) resolution, it can quickly access these pre-computed overviews instead of having to resample the entire high-resolution image on the fly, leading to much faster rendering.
* **Requirement:** The input file for this operation **must be a GeoTIFF** (`.tif` or `.tiff`). The GUI will prevent selection of other file types for this mode.
* **Conversion Process:**
    1.  First, `gdal_translate.exe` creates a new, identical copy of your input GeoTIFF file in your chosen output directory. This ensures the original source file is never modified. The new file will be named `[original_filename]_with_overviews.tif`.
    2.  Second, `gdaladdo.exe` is executed on this newly created copy. It calculates and embeds lower-resolution versions of the image (overviews) directly within the GeoTIFF file's internal structure.
* **Output:**
    * A single new GeoTIFF file (e.g., `[original_filename]_with_overviews.tif`) will be created in your selected output directory.
    * This output file will be larger than the original, as it now contains the embedded overviews, but it will offer significantly improved performance in GIS applications.
* **"Levels" Option:** For overviews, you specify a **space-separated list of downsampling factors** (e.g., `2 4 8 16`). Each number represents a reduction factor (e.g., `2` means half the resolution, `4` means a quarter, `16` means 1/16th the resolution). A common practice is to use powers of 2.

### Option 3: DTM to SRTMHGT

This mode converts a **TIFF/GeoTIFF file containing DTM (Digital Terrain Model) data** into the **SRTMHGT format** (files with `.hgt` extension).
The SRTMHGT format is widely used in many GIS and 3D visualization applications because it matches the structure of original SRTM (Shuttle Radar Topography Mission) elevation data, using a fixed 1201 × 1201 grid per 1° × 1° geographic tile.

* **Purpose:**
  To make your locally created or acquired DTM elevation datasets compatible with software, tools, or libraries that directly consume SRTM-style `.hgt` files, such as terrain renderers, flight simulators, and some GPS mapping software.

* **Requirements:**

  * The input must be a raster file in TIFF or GeoTIFF format containing valid elevation data (e.g., in meters).
  * The input should ideally have a spatial reference in WGS 84 (EPSG:4326) or a UTM zone compatible with the target area.
  * Note: The tool does **not** currently clip or resample your TIFF to exactly match a 1°×1° tile. Make sure your input covers the correct extent (usually 1201×1201 samples) before conversion.

* **Conversion process:**

  1. The tool takes your selected TIFF file (e.g., `my_dtm.tif`).
  2. It runs `gdal_translate` with the option `-of SRTMHGT` to produce an output `.hgt` file in the SRTMHGT format.
  3. The output file keeps the base name of the original TIFF, e.g., `my_dtm.hgt`.

* **Output:**

  * A single `.hgt` file (e.g., `my_dtm.hgt`) located in the chosen output directory.
  * The output is a 16‑bit signed integer raster with a fixed size of 1201×1201 pixels, which is the standard for SRTM data tiles.

### Common Option: Resampling Method

When creating tiles or overviews, the original image data needs to be resampled (resized) to new resolutions. The GUI allows you to choose from different resampling (interpolation) methods:

* `average`: Computes the average pixel value from the contributing source pixels. Generally good for continuous data (e.g., elevation models) and can smooth out noise.
* `nearest`: Uses the value of the single nearest pixel. This is the fastest method but can produce blocky or "pixelated" results, especially when scaling up. Best for discrete data (e.g., land cover classifications).
* `bilinear`: Computes a weighted average of the 4 nearest pixels. Produces smoother results than `nearest` but can slightly blur sharp details.
* `lanczos`: A more advanced, high-quality interpolation method that often produces sharper results than `bilinear` without significant aliasing, but it is computationally more intensive.

## 3. Prerequisites

Before running this script, ensure you have Python installed and the necessary GDAL executables and their associated dependencies are correctly placed within your project's structure.

### Python 3

* **Version:** Python 3.6 or higher is recommended for compatibility and features.
* **Tkinter:** Tkinter, the standard Python GUI toolkit, is typically included with default Python installations on Windows. If you installed Python via a custom method or are on Linux/macOS, you might need to install `python3-tk` separately (e.g., `sudo apt-get install python3-tk` on Debian/Ubuntu systems).
* **GDAL Python bindings:**
  The GUI’s advanced features (such as detecting raster size and cutting into tiles for SRTMHGT) require the [GDAL Python bindings](https://pypi.org/project/GDAL/).
  Install them via:

  ```bash
  pip install GDAL
  ```

  ⚠ *Note:* On Windows, installation via `pip` might need a precompiled wheel (e.g., from [Christoph Gohlke’s repository](https://www.lfd.uci.edu/~gohlke/pythonlibs/#gdal)) that matches your Python version and architecture.

### GDAL Binaries & Dependencies

This project is designed for portability, meaning it expects the required GDAL command-line tools (`gdal2tiles.exe`, `gdaladdo.exe`, `gdal_translate.exe`) and their essential supporting files (DLLs, data files) to be co-located within a `bin` subfolder of your project directory. This approach minimizes reliance on a system-wide OSGeo4W installation's `PATH` variable and makes the application easier to distribute.

## 4. Installation Guide

Follow these steps carefully to set up your environment and prepare the project:

### Step 1: Install Python 3

1.  **Download Python:** Visit the official Python website: [python.org/downloads/](https://www.python.org/downloads/)
2.  **Run the Installer:**
    * During installation, **it is highly recommended** to check the box that says **"Add Python to PATH"** (or similar, depending on your Python version). This simplifies running Python scripts from any command line.
    * Choose "Customize installation" to ensure `Tkinter` is selected (it usually is by default).
    * Install Python to a standard or easily accessible location (e.g., `C:\Users\<YourUser>\AppData\Local\Programs\Python\Python3XX`).

### Step 2: Obtain GDAL Binaries and Dependencies

This is the most critical step for making the project self-contained. You will need to extract the necessary GDAL files from an existing OSGeo4W installation (or another reliable GDAL distribution).

1.  **Install OSGeo4W (Recommended Method to get GDAL files):**
    * If you don't already have OSGeo4W installed, download the appropriate installer: [OSGeo4W Download Page](https://trac.osgeo.org/osgeo4w/) (e.g., `osgeo4w-setup-x86_64.exe` for 64-bit systems, which is recommended).
    * Run the OSGeo4W Installer:
        * Select **"Advanced Install"**.
        * Choose **"Install from Internet"**.
        * Follow the prompts for download directory and local package directory (defaults are usually fine).
        * Select your internet connection type and a download site.
        * **Crucial Step: Select Packages.**
            * Under the `Libs` category, find and select the `gdal` package. Click on the "Skip" column next to `gdal` until you see the latest version number.
            * Under the `Python` category, select the `python3` package corresponding to your Python version (e.g., `python312`) and, **most importantly, the `python3-gdal` package** (e.g., `python312-gdal`). Click "Skip" until the version numbers appear.
            * (Optional but Recommended): Consider installing `qgis` from the `Desktop` or `GIS` category, as this often pulls in many common dependencies useful for geospatial work.
        * Click **"Next"**. The installer will present a list of additional dependencies. **Accept all of them.**
        * Proceed with the installation. Note the chosen installation path (e.g., `C:\OSGeo4W64`).

2.  **Gather GDAL Files for your Project's `bin` Folder:**
    * Create a new folder named `bin` directly inside your main project directory (e.g., `YourProjectFolder/bin`).
    * Now, copy the following files and folders from your OSGeo4W installation (using `C:\OSGeo4W64` as an example path) into your `YourProjectFolder\bin\` directory:
        * **Executables:**
            * `gdal2tiles.exe` (from `C:\OSGeo4W64\apps\Python312\Scripts\` or similar Python version path)
            * `gdaladdo.exe` (from `C:\OSGeo4W64\bin\`)
            * `gdal_translate.exe` (from `C:\OSGeo4W64\bin\`)
        * **Dynamic Link Libraries (DLLs):**
            * **CRITICAL:** Copy **ALL `*.dll` files** from `C:\OSGeo4W64\bin\` into `YourProjectFolder\bin\`. These are essential runtime dependencies for the GDAL executables to function correctly. This will be a large number of files.
        * **GDAL Data Files:**
            * Copy the entire `gdal` folder from `C:\OSGeo4W64\share\` into `YourProjectFolder\bin\gdal-data`. You should end up with `YourProjectFolder\bin\gdal-data\gdal_crs.json`, `gdal_datum.csv`, etc. This folder is crucial for GDAL's understanding of coordinate systems, transformations, and other internal data.
        * **PROJ Data Files (Highly Recommended):**
            * Copy the entire `proj` folder from `C:\OSGeo4W64\share\` into `YourProjectFolder\bin\proj`. PROJ is a core library used by GDAL for coordinate transformation, and its data files (`proj.db`, etc.) are often necessary for accurate georeferencing.

### Step 3: Download and Structure the Project

1.  Create a main folder on your computer for this project (e.g., `GDAL_Map_Converter`).
2.  Save the provided Python GUI script (`map_tiler_gui.py`) directly into this folder.
3.  Place the `bin` folder (which you populated in Step 2 with GDAL executables and all their dependencies) inside your `GDAL_Map_Converter` folder.

Your final project structure should look exactly like this:

```
GDAL_Map_Converter/
├── map_tiler_gui.py           (The main Python script)
└── bin/                       (Contains all GDAL dependencies)
    ├── gdal2tiles.exe
    ├── gdal2tiles-script.py
    ├── gdaladdo.exe
    ├── gdal_translate.exe
```

**Important Note:** The `map_tiler_gui.py` script has been specifically updated to automatically locate the GDAL executables and the `GDAL_DATA` environment variable within this `bin` subfolder. Therefore, **no manual path configuration within the Python script is required** if you follow this project structure precisely.

---

## 5. How to Use the GUI

Once all prerequisites are installed and the project is structured as described above, you can run the application:

1.  **Open a standard Windows Command Prompt (CMD) or PowerShell.**
    * **Do NOT** use the OSGeo4W Shell for this step, as it configures its own environment variables which might interfere with the self-contained setup.

2.  **Navigate to your project's root directory** using the `cd` command:

    ```bash
    cd C:\Users\YourUser\Desktop\GDAL_Map_Converter
    ```

    (Remember to replace `C:\Users\YourUser\Desktop\GDAL_Map_Converter` with the actual path where you saved your project folder).

3.  **Run the Python script:**

    ```bash
    "C:\Users\YourUser\AppData\Local\Programs\Python\Python312\python.exe" map_tiler_gui.py
    ```

    (You will need to replace `"C:\Users\YourUser\AppData\Local\Programs\Python\Python312\python.exe"` with the actual full path to your main Python executable installed in Step 1. This path typically resides in your AppData folder).

4.  **Using the GUI Interface:**

    * **"Input Map File" Section:**
        * Click the "Select Map File..." button.
        * Browse and select your input geospatial image file (e.g., a GeoTIFF, JPG, PNG, etc.).
    * **"Conversion Type" Section:**
        * Choose your desired conversion:
            * **"Generate Web Map Tiles":** For creating tiles for web mapping applications.
            * **"Add Internal Overviews":** For optimizing GeoTIFFs for desktop GIS applications. **Remember: For this option, the input file MUST be a GeoTIFF (.tif/.tiff). The GUI will prompt you if you select a non-GeoTIFF.**
    * **"Output Directory" Section:**
        * Click "Select Output Directory..."
        * Choose an empty or suitable directory where you want the output files or folders to be saved. The tool will create subfolders or files within this selected directory.
    * **"Conversion Options" Section:**
        * **"Levels":**
            * If "Generate Web Map Tiles" is selected, this field will dynamically change to "Zoom Levels (e.g.: 0-16):". Enter a range of zoom levels you want to generate.
            * If "Add Internal Overviews" is selected, this field will dynamically change to "Overview Levels (e.g.: 2 4 8 16):". Enter a space-separated list of downsampling factors.
        * **"Resampling Method":** Select your preferred resampling algorithm from the dropdown menu (`average`, `nearest`, `bilinear`, `lanczos`).
    * **"Start Conversion" Button:**
        * Click this button to initiate the conversion process.
        * The GUI's status label will update, and the "Output Console" text area will display the live command-line output from the GDAL tools.
        * The GUI remains responsive during the process thanks to background threading.
    * **Completion:**
        * Upon successful completion, a success message will appear in a pop-up window and the status label will turn green.
        * The generated tiles (for web maps) or the optimized GeoTIFF (for overviews) will be located in the output directory you selected.

---

## 6. Troubleshooting Common Issues

* **`FileNotFoundError: [WinError 2] The system cannot find the file specified`**:
    * **Cause:** This almost always means one of the GDAL executables (`gdal2tiles.exe`, `gdaladdo.exe`, `gdal_translate.exe`) or their required DLLs could not be found by the Python script or the operating system.
    * **Solution:**
        * **Re-verify Step 2 (`Obtain GDAL Binaries and Dependencies`) meticulously.** Ensure you have copied *all* the necessary `.exe` files, *all* the `.dll` files from your OSGeo4W `bin` directory, and the `gdal-data` (and `proj`) folders correctly into your `YourProjectFolder/bin` directory.
        * Double-check for any typos in the `bin` folder name or the internal structure. The script relies on this precise folder arrangement.
* **`WinError 193: %1 is not a valid Win32 application`**:
    * **Cause:** This typically indicates a mismatch between 32-bit and 64-bit components. For example, trying to run a 64-bit GDAL executable with a 32-bit Python environment or vice-versa, or having mixed 32-bit/64-bit DLLs.
    * **Solution:**
        * Ensure your Python installation is 64-bit.
        * Confirm that you downloaded and extracted the GDAL binaries from a 64-bit OSGeo4W installation. All `*.exe` and `*.dll` files within your `YourProjectFolder/bin` should be consistently 64-bit.
        * If inconsistencies persist, a clean reinstallation of OSGeo4W (deleting the old folder first) is sometimes the quickest solution.
* **Errors related to `GDAL_DATA` or `PROJ_LIB` (e.g., "Cannot find proj.db", "No such file or directory in `gdal_set_path`", or projection-related errors):**
    * **Cause:** This indicates that GDAL cannot find its essential data files required for coordinate system definitions, transformations, and other operations.
    * **Solution:**
        * Ensure you correctly copied the entire `gdal` folder from `C:\OSGeo4W64\share\` into `YourProjectFolder\bin\gdal-data` (resulting in `YourProjectFolder\bin\gdal-data\gdal_crs.json`, etc.).
        * If you encounter errors specifically related to projections, ensure you also copied the entire `proj` folder from `C:\OSGeo4W64\share\` into `YourProjectFolder\bin\proj`.
* **GUI is unresponsive/freezes:**
    * **Cause:** While the script uses threading to prevent this, very large input files or extremely high zoom/overview levels can still be highly resource-intensive and might temporarily strain your system.
    * **Solution:** Monitor your system's Task Manager (CPU, RAM usage). If the GUI freezes completely, the process might be stuck or consuming excessive resources. Consider trying a smaller input file or a smaller range of levels first.
* **"Error copying GeoTIFF" / "Error in conversion" (Generic GDAL errors):**
    * **Cause:** These are general errors from the underlying GDAL commands.
    * **Solution:**
        * **Crucially, check the detailed error messages displayed in the GUI's "Output Console" text area.** GDAL often provides specific reasons for failure there.
        * Ensure the input file is not corrupted, incomplete, or locked by another application.
        * For the "Add Internal Overviews" option, verify that the input file is indeed a valid GeoTIFF.
        * Check that the selected output directory has proper write permissions.

---

## 7. License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 8. Contact

For questions, bug reports, feature requests, or general support, please:
* Open an issue on the GitHub repository (if this project is hosted on GitHub).
* Or, contact the developer directly at: haveritzik@gmail.com

---