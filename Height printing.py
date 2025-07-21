import os
import subprocess

folder = r"C:\Users\CVT\Desktop\projects\Convert_maps_from_Tiff_to_SRTMHGT\DTM-ISRAEL_08.06.25\SRTM-1"
gdalinfo_exe = r"C:\OSGeo4W\bin\gdalinfo.exe"

for filename in os.listdir(folder):
    if filename.lower().endswith('.hgt'):
        file_path = os.path.join(folder, filename)
        try:
            result = subprocess.run(
                [gdalinfo_exe, "-stats", file_path],
                capture_output=True,
                text=True,
                check=True
            )
            output = result.stdout

            min_val = max_val = None
            for line in output.splitlines():
                line = line.strip()
                if 'STATISTICS_MINIMUM=' in line:
                    min_val = line.split('=')[1]
                if 'STATISTICS_MAXIMUM=' in line:
                    max_val = line.split('=')[1]

            print(f"{filename}: min={min_val}, max={max_val}")

        except Exception as e:
            print(f"[ERROR] Failed to process {filename}: {e}")
