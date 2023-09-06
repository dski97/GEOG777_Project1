#import modules
import arcpy
import tkinter as tk

#set workspace
cancer_tracts_path = r"C:\Users\cwalinskid\Desktop\reps\GEOG777_Project1\shapefiles\cancer_tracts.shp"
well_nitrate_path = r"C:\Users\cwalinskid\Desktop\reps\GEOG777_Project1\shapefiles\well_nitrate.shp"

#load the shapefiles
cancer_tracts = arcpy.Describe(cancer_tracts_path).catalogPath
well_nitrate = arcpy.Describe(well_nitrate_path).catalogPath

print ("Working")

def execute_analysis():
    k_value = k_slider.get()
    # Trigger the analysis function with the provided k_value
    
root = tk.Tk()
root.title("Nitrate and Cancer Analysis")

k_slider = tk.Scale(root, from_=1, to=10, orient='horizontal', label='Choose k value')
k_slider.pack()

execute_button = tk.Button(root, text="Execute Analysis", command=execute_analysis)
execute_button.pack()

root.mainloop()