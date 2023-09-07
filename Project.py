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

# Define the function to execute the main analysis
def execute_analysis():
    # Get the value of k from the Tkinter slider
    k_value = k_slider.get()
    
    # Perform IDW interpolation on well nitrate data using the selected k value
    outIDW = Idw(well_nitrate, "nitr_ran", power=k_value)
    
    # Save the IDW output to a TIFF file
    outIDW.save(r"C:\Users\cwalinskid\Desktop\reps\GEOG777_Project1\Outputs\idw_nitrate.tif")
    
    #Raster
    messagebox.showinfo("Completion", "All set, analysis executed successfully.")

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
