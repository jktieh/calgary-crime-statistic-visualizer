"""
main.py

Authors: Jason Chiu and Jason Tieh
Since: Jun 20, 2025
version: 1.0

Entry point of the ENSF 692 Spring 2025 final project.

This script coordinates the overall program execution, including loading data,
getting user input, performing analysis, and exporting results.

"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

from dataLoader import create_dataframe, export_to_excel
from dataPrintAndSave import print_describe, location_year_summary, save_plot
from dataVisualizer import show_maps, plot_crime_category, plot_crime_count, plot_cc_vs_mdv, plot_cc_vs_bc
from userInputs import get_location, get_year

def main():     

    print("\nStarting up Calgary Crime Statistics Visualizer... \
          \nCreating dataframe...\n")
    # Load data from CSV files and perform initial cleaning    
    df = create_dataframe()       

    print(" --------- Start Calgary Crime Statistics Visualizer ---------")
    print("\nWelcome to Calgary Crime Statistic Visualizer!\n" \
    "\nIn this program, you will be able to view Calgary's basic crime statistics from the years 2018 to 2024" \
    "\nSelect a year and location/region within Calgary, and you will see data related to the input, including: " \
    "\ntype and quantity of crime, crime per month, crime per capita 1000 vs median assessed value of the region," \
    "\nand crime count vs the number of existing businesses of the region.")

    print("\nBased On current entire existing dataset, the following values have also been observed:\n")

    # Prints describe table summarizing entire dataset indexed by month
    print_describe(df)

    print("\n\nTo begin the visualizer, first select the region type.")

    # Loop for if user wishes to visualize different regions and/or years
    while True:
        # prompt to bring up Sector/Ward/Community reference maps
        map = input("\nIf you would like a map to see what sectors, wards, and communities you may see the map png files " \
        "\nfound in the /data folder or if you wish to see the images from here, enter (Y/N) (Note: this process is slow): ").strip().upper()
        if (map == 'Y'):
            show_maps()
        
        # get user desired location and year
        location_type, location = get_location(df)
        year = get_year(df)

        print("\nYou have chosen the following region and year | ", location_type, ": ", location, " for the year ", year)

        print("\nBased on these chosen fields, the following statistics can be seen:\n")
        
        # printing short summary table ot useful statistics for the chosen location and year
        location_year_summary(df, location, year, location_type)

        ## Beginning of displayed plotted results
        # plot for crime category and their total count for the chosen year and location
        print("\nHere is a plot showing the crime category and their total count for the chosen year and location: \
              \nBelow is a pivot table for the same data but separated by month")
        # also prints out a pivot table of the crime category count by month
        plot_crime_category(df, location, year, location_type)
        # prompt user if they wish to save plot as png or not (repeated for each of the 4 plots, this and 3 below)
        save0 = input("Would you like to save this plot as a png? (stored in /images) (Y/N): ").strip().upper()
        if (save0 == 'Y'):
            save_plot(location_type, year, "Crime_Category_Count", location)
        plt.close()
        
        # plot comparing the amount of crime per month for the chosen year and location
        print("\nHere is a plot comparing the amount of crime per month for the chosen year and location:\n")
        plot_crime_count(df, location, year, location_type)
        save1 = input("Would you like to save this plot as a png? (stored in /images) (Y/N): ").strip().upper()
        if (save1 == 'Y'):
            save_plot(location_type, year, "Crime_Count_by_Month", location)
        plt.close()

        # plot comparing Crime per capita 1000 vs a locations communities, median assessed value
        print("\nHere is a plot comparing Crime per capita 1000 vs a locations communities, median assessed value: \
              \nNote: If the point is not highlighted, there is no information on median assessed value for this location\n")
        plot_cc_vs_mdv(df, location, year, location_type)
        save2 = input("Would you like to save this plot as a png? (stored in /images) (Y/N): ").strip().upper()
        if (save2 == 'Y'):
            save_plot(location_type, year, "Crime_per_Capita_vs__med_Assessed_Value", location)
        plt.close()

        # plot comparing Crime Count vs a locations communities business count to date total
        print("\nHere is a plot comparing Crime Count vs a locations communities business count to date total: \
              \nNote: If the point is not highlighted, there is no information on business count to date for this location\n")
        plot_cc_vs_bc(df, location, year, location_type)
        save3 = input("Would you like to save this plot as a png? (stored in /images) (Y/N): ").strip().upper()
        if (save3 == 'Y'):
            save_plot(location_type, year, "Crime_Count_vs_Business_Count", location)
        plt.close()

        # prompt utilizing loop to ask for new location/region and year if desired
        final = input("\nWould you like to visualize data for another location and/or time? Hit 'ENTER' to continue" \
        ", otherwise enter 'Q' to quit: ").strip().upper()
        if(final == 'Q'):
            break
    
    # saves indexed csv merged datafram to an excel if desired
    final_save = input("\nWould you like to export the indexed crime dataframe to an excel?" \
    " (Y/N) (Note this may take over 10 minutes): ").strip().upper()
    if (final_save == 'Y'):
        export_to_excel(df, filename='calgary_crime_data.xlsx', sheet_name='Sheet1')
        
    print("\nThank you for Using the Calgary Crime Statistics Visualizer.")
    print("-----------------------------------------------------------------------------------------")

if __name__ == "__main__":
    main()