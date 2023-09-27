# Import required modules
import arcpy
import tkinter as tk
from arcpy.sa import *
from tkinter import messagebox


# Check out the required ArcGIS extension for spatial analysis
arcpy.CheckOutExtension("Spatial")

# Enable overwriting of output files
arcpy.env.overwriteOutput = True

#Function to update ArcGIS Pro Layers
def export_layouts_to_pdf():
    project_path = r"C:\Users\Dominic\Desktop\GEOG777_Project1\Project1\Project1.aprx"
    project = arcpy.mp.ArcGISProject(project_path)

    # Loop through all the layouts and export each one to PDF
    for lyt in project.listLayouts():
        if lyt.name == "IDW":
            pdf_path = r"C:\Users\Dominic\Desktop\GEOG777_Project1\Outputs\idw_layout.pdf"
            lyt.exportToPDF(pdf_path)
        elif lyt.name == "OLS":
            pdf_path = r"C:\Users\Dominic\Desktop\GEOG777_Project1\Outputs\ols_layout.pdf"
            lyt.exportToPDF(pdf_path)

# Define paths to the shapefiles for cancer tracts and well nitrate levels
cancer_tracts_path = r"C:\Users\Dominic\Desktop\GEOG777_Project1\shapefiles\cancer_tracts.shp"
well_nitrate_path = r"C:\Users\Dominic\Desktop\GEOG777_Project1\shapefiles\well_nitrate.shp"

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
    outIDW.save(r"C:\Users\Dominic\Desktop\GEOG777_Project1\Outputs\idw_nitrate.tif")
    
    # Perform a zonal statistics analysis on the cancer tracts using the IDW output
    outZSaT = ZonalStatisticsAsTable(cancer_tracts, "GEOID10", outIDW, r"C:\Users\Dominic\Desktop\GEOG777_Project1\Outputs\zonal_stats.dbf", "DATA", "MEAN")

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
    arcpy.FeatureClassToFeatureClass_conversion(cancer_tracts, r"C:\Users\Dominic\Desktop\GEOG777_Project1\Outputs", "cancer_tracts_analysis.shp")

    # Print a message to console for debugging
    print("Export Complete")

 # Complete an OLS regression analysis on the cancer tracts shapefile
    arcpy.stats.OrdinaryLeastSquares(
        Input_Feature_Class=r"C:\Users\Dominic\Desktop\GEOG777_Project1\Outputs\cancer_tracts_analysis.shp",
        Unique_ID_Field="unique",
        Output_Feature_Class=r"C:\Users\Dominic\Desktop\GEOG777_Project1\Outputs\ols_analysis.shp",
        Dependent_Variable="canrate",
        Explanatory_Variables=["MEAN"],
        Output_Report_File=r"C:\Users\Dominic\Desktop\GEOG777_Project1\Outputs\ols_report.pdf")
    
    # Print a message to console for debugging
    print("OLS Complete")

    #Export layouts to PDF
    export_layouts_to_pdf()


# Initialize the Tkinter GUI window
root = tk.Tk()
root.title("Nitrate and Cancer Analysis")

# Create a Tkinter slider to select the k value for IDW interpolation
k_slider = tk.Scale(root, from_=1, to=10, orient='horizontal', label='Choose k value')
k_slider.pack()

# Create a Tkinter button that will execute the analysis when clicked
execute_button = tk.Button(root, text="Execute Analysis", command=execute_analysis)
execute_button.pack()

# Start the Tkinter event loop
root.mainloop()
 