# Import required modules
import arcpy
import tkinter as tk
from arcpy.sa import *
from tkinter import messagebox
import tkinter.ttk as ttk
from PIL import ImageTk, Image
import subprocess
import glob
import shutil
import os


# Check out the required ArcGIS extension for spatial analysis
arcpy.CheckOutExtension("Spatial")

# Enable overwriting of output files
arcpy.env.overwriteOutput = True

# Define the function to export layouts to PDF
def export_layouts_to_pdf():
    project_path = r"C:\Users\cwalinskid\Desktop\reps\GEOG777_Project1\Project1\Project1.aprx"
    project = arcpy.mp.ArcGISProject(project_path)

    # Loop through all the maps in the project
    for map in project.listMaps():
        # Loop through each layer in the map
        for lyr in map.listLayers():
            # Check and rename the IDW layer
            if lyr.name.lower() == "idw":
                lyr.name = "Nitrate Concentration Map"
            # Check and rename the OLS layer
            elif lyr.name.lower() == "ols_analysis":
                lyr.name = "Cancer Rate Regression Analysis"

    # Loop through all the layouts and export each one to PDF
    for lyt in project.listLayouts():
        if lyt.name == "IDW":
            pdf_path = r"C:\Users\cwalinskid\Desktop\reps\GEOG777_Project1\Outputs\idw_layout.pdf"
            lyt.exportToPDF(pdf_path)
        elif lyt.name == "OLS":
            pdf_path = r"C:\Users\cwalinskid\Desktop\reps\GEOG777_Project1\Outputs\ols_layout.pdf"
            lyt.exportToPDF(pdf_path)

    # Save the project after renaming layers
    project.save()
# Define paths to the shapefiles for cancer tracts and well nitrate levels
cancer_tracts_path = r"C:\Users\cwalinskid\Desktop\reps\GEOG777_Project1\shapefiles\cancer_tracts.shp"
well_nitrate_path = r"C:\Users\cwalinskid\Desktop\reps\GEOG777_Project1\shapefiles\well_nitrate.shp"

# Load the shapefiles using ArcPy's Describe function
cancer_tracts = arcpy.Describe(cancer_tracts_path).catalogPath
well_nitrate = arcpy.Describe(well_nitrate_path).catalogPath

# Print a message to console for debugging
print("Working")


# Define the function to calculate ICW
def execute_analysis():
    # Get the value of k from the Tkinter slider
    k_value = k_slider.get()
    
    # Perform IDW interpolation on well nitrate data using the selected k value
    outIDW = Idw(well_nitrate, "nitr_ran", cell_size= 0.00161631928, power=k_value)
    
    # Save the IDW output to a TIFF file
    outIDW.save(r"C:\Users\cwalinskid\Desktop\reps\GEOG777_Project1\Outputs\idw_nitrate.tif")
    
    # Perform a zonal statistics analysis on the cancer tracts using the IDW output
    outZSaT = ZonalStatisticsAsTable(cancer_tracts, "GEOID10", outIDW, r"C:\Users\cwalinskid\Desktop\reps\GEOG777_Project1\Outputs\zonal_stats.dbf", "DATA", "MEAN")

    # Print a message to console for debugging
    print("Zonal Statistics Complete")

    # Check if "MEAN" field exists and delete if it does
    field_names = [f.name for f in arcpy.ListFields(cancer_tracts)]
    if 'MEAN' in field_names:
        arcpy.DeleteField_management(cancer_tracts, "MEAN")
    
    # Check if "unique" field exists, create and populate it if it doesn't
    if 'unique' not in field_names:
        arcpy.AddField_management(cancer_tracts, "unique", "LONG")
        with arcpy.da.UpdateCursor(cancer_tracts, ["unique"]) as cursor:
            unique_id = 1
            for row in cursor:
                row[0] = unique_id
                cursor.updateRow(row)
                unique_id += 1

    # Join the zonal statistics table to the cancer tracts shapefile
    arcpy.JoinField_management(cancer_tracts, "GEOID10", outZSaT, "GEOID10", "MEAN")

    # Print a message to console for debugging
    print("Join Complete")

    #Export the cancer tracts shapefile to a new shapefile
    arcpy.FeatureClassToFeatureClass_conversion(cancer_tracts, r"C:\Users\cwalinskid\Desktop\reps\GEOG777_Project1\Outputs", "cancer_tracts_analysis.shp")

    # Print a message to console for debugging
    print("Export Complete")

 # Complete an OLS regression analysis on the cancer tracts shapefile
    arcpy.stats.OrdinaryLeastSquares(
        Input_Feature_Class=r"C:\Users\cwalinskid\Desktop\reps\GEOG777_Project1\Outputs\cancer_tracts_analysis.shp",
        Unique_ID_Field="unique",
        Output_Feature_Class=r"C:\Users\cwalinskid\Desktop\reps\GEOG777_Project1\Outputs\ols_analysis.shp",
        Dependent_Variable="canrate",
        Explanatory_Variables=["MEAN"],
        Output_Report_File=r"C:\Users\cwalinskid\Desktop\reps\GEOG777_Project1\Outputs\ols_report.pdf")
    
     # Print a message to console for debugging
    print("OLS Complete")

 # Complete a Spatial Autocorrelation analysis on the cancer tracts shapefile and export a html report
    arcpy.stats.SpatialAutocorrelation(
        Input_Feature_Class=r"C:\Users\cwalinskid\Desktop\reps\GEOG777_Project1\Outputs\ols_analysis.shp",
        Input_Field="Residual",
        Generate_Report="GENERATE_REPORT",
        Conceptualization_of_Spatial_Relationships="INVERSE_DISTANCE",
        Distance_Method="EUCLIDEAN_DISTANCE",
        Standardization="ROW",
        )


    # Print a message to console for debugging
    print("Morans I Complete")

    # Remove any existing Moran's I reports in the output folder
    existing_reports = glob.glob(r"C:\Users\cwalinskid\Desktop\reps\GEOG777_Project1\Outputs\MoransI_Result*.html")
    for report in existing_reports:
        os.remove(report)

     # Search for the most recently created Moran's I HTML report in the Temp directory
    search_path = r"C:\Users\cwalinskid\AppData\Local\Temp\MoransI_Result_*.html"
    list_of_files = glob.glob(search_path)
    latest_file = max(list_of_files, key=lambda x: os.path.getctime(x))

    # Define the destination path for the HTML report
    dest_path = r"C:\Users\cwalinskid\Desktop\reps\GEOG777_Project1\Outputs"

    # Move the HTML report to the desired output folder
    shutil.move(latest_file, dest_path)

    #Export layouts to PDF
    export_layouts_to_pdf()

      # Display a pop-up message indicating that the analysis is complete
    messagebox.showinfo("Analysis Complete", "The analysis has been successfully completed!")



# Initialize the Tkinter GUI window
root = tk.Tk()
root.title("Nitrate and Cancer Analysis")

# Create a Tkinter slider to select the k value for IDW interpolation
k_slider = tk.Scale(root, from_=1, to=10.0, resolution=0.1, orient='horizontal', 
                    label='Choose k value for IDW interpolation', bg='blue', 
                    fg='white', troughcolor='black', length=400)
k_slider.pack(pady=20)


# Map display
image_path = r"C:\Users\cwalinskid\Desktop\reps\GEOG777_Project1\Outputs\BaseMap.png"
original_img = Image.open(image_path)
# Resize the image
width, height = original_img.size
new_width = int(width * 0.18)
new_height = int(height * 0.18)
resized_img = original_img.resize((new_width, new_height), Image.ANTIALIAS)

# Convert to a format that Tkinter understands
img = ImageTk.PhotoImage(resized_img)

map_label = tk.Label(root, image=img)
map_label.pack()

# Create a Tkinter button that will execute the analysis when clicked
execute_button = tk.Button(root, text="Run Analysis", bg='green', fg= 'white', command=execute_analysis, padx=50, pady=20)
execute_button.pack(pady=20)

# Define the function to display information about the tool
def show_info():
    info_message = "Welcome to the Nitrate and Cancer Analysis Tool!\n\n" \
                   "How to use:\n" \
                   "- Adjust the k value for IDW interpolation using the slider.\n" \
                   "- Click 'Run Analysis' to perform the geospatial analysis.\n" \
                   "- View the results in the specified output directory.\n\n" \
                   "This tool helps in analyzing the relationship between nitrate levels in wells and cancer rates."
    messagebox.showinfo("How to Use", info_message)

# Create a Tkinter button that will display information about the tool when clicked
info_button = tk.Button(root, text="How to Use", bg='yellow', fg='black', command=show_info, padx=10, pady=5)
info_button.pack(pady=10)


# Start the Tkinter event loop
root.mainloop()
 