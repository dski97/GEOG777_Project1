# Import required modules
import arcpy
import tkinter as tk
from arcpy.sa import *
from tkinter import messagebox

# Check out the required ArcGIS extension for spatial analysis
arcpy.CheckOutExtension("Spatial")

# Enable overwriting of output files
arcpy.env.overwriteOutput = True

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
    
    #Raster
    messagebox.showinfo("Completion", "IDF Nitrate Raster Complete")

    # Perform a zonal statistics analysis on the cancer tracts using the IDW output
    outZSaT = ZonalStatisticsAsTable(cancer_tracts, "GEOID10", outIDW, r"C:\Users\cwalinskid\Desktop\reps\GEOG777_Project1\Outputs\zonal_stats.dbf", "DATA", "MEAN")

    # Print a message to console for debugging
    print("Zonal Statistics Complete")

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
        Input_Feature_Class_ID_Field="GEOID10", 
        Output_Feature_Class=r"C:\Users\cwalinskid\Desktop\reps\GEOG777_Project1\Outputs\ols_analysis.shp",
        Dependent_Variable="canrate",
        Explanatory_Variables=["MEAN"])
    
    # Print a message to console for debugging
    print("OLS Complete")


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
