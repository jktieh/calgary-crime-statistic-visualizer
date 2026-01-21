import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.withdraw()

def show_regions_available(final_df, location_type):
    """
    Displays a popup table listing valid region values based on location_type.
    Only 'Community' table includes a No. column for row numbering.

    Parameters:
        final_df (pd.dataframe): DataFrame with merged dataset.
        location_type (str): 'Community', 'Ward Number', or 'Sector'

    Returns:
        Opens a tk window to display a list or table of the available regions that can be entered in.
    """
    # filter based on the conditions of no nan values and removing duplicates, dependent on location type
    if location_type == 'Community':
        region_df = final_df[['Community Code', 'Community']].dropna()
        region_df = region_df.drop_duplicates().sort_values('Community')
        columns = ('No.', 'Community Code', 'Community')
        headings = ['No.', 'Code', 'Community']
        values = region_df[['Community Code', 'Community']].values.tolist()

    elif location_type == 'Ward Number':
        region_df = final_df[['Ward Number']].dropna()
        region_df = region_df[region_df['Ward Number'].apply(lambda x: str(x).isdigit())]
        region_df['Ward Number'] = region_df['Ward Number'].astype(int)
        region_df = region_df.drop_duplicates().sort_values('Ward Number')
        columns = ('Ward Number',)
        headings = ['Ward Number']
        values = region_df.values.tolist()

    elif location_type == 'Sector':
        region_df = final_df[['Sector']].dropna()
        region_df = region_df.drop_duplicates().sort_values('Sector')
        columns = ('Sector',)
        headings = ['Sector']
        values = region_df.values.tolist()

    else:
        print(f"Invalid location type: {location_type}")
        return
    
    # Create Toplevel window
    window = tk.Toplevel()
    window.title(f"Valid {location_type}s")
    window.geometry("800x400")
    window.attributes("-topmost", True)

    # Frame to contain Treeview and Scrollbar
    frame = tk.Frame(window)
    frame.pack(fill='both', expand=True)

    # Grid configuration layout
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)

    # Create Treeview
    tree = ttk.Treeview(frame, columns=columns, show='headings')
    for col, heading in zip(columns, headings):
        tree.heading(col, text=heading)
        tree.column(col, anchor='w')

    for idx, row in enumerate(values, start=1):
        if location_type == 'Community':
            tree.insert('', 'end', values=(idx, *row))
        else:
            tree.insert('', 'end', values=(row[0],))

    # Scrollbar and placement
    scrollbar = ttk.Scrollbar(frame, orient='vertical', command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)

    tree.grid(row=0, column=0, sticky='nsew')
    scrollbar.grid(row=0, column=1, sticky='ns')

    # Keeps window open and program to continue
    window.after(100, lambda: None)


def show_maps():
    """Display two PNG images side by side using matplotlib.
    
    Returns:
        Opens a plt window showing the two pngs side by side
    """
    print("\nLoading images. This may take a few seconds...\n")
    file1 = "data/Calgary_Wards_and_Community_Codes_Map_2025.png"
    file2 = "data/Creb_Calgary_Community_and_Sector_Map_2025.png"
    img1 = mpimg.imread(file1)
    img2 = mpimg.imread(file2)

    # uses plt plot to show the two reference map images
    fig, axes = plt.subplots(1, 2, figsize=(12, 6))  # 1 row, 2 columns

    axes[0].imshow(img1)
    axes[0].set_title(f"Calgary Wards and Community Codes Map")
    axes[0].axis('off')

    axes[1].imshow(img2)
    axes[1].set_title(f"Calgary Community and Sectors Map")
    axes[1].axis('off')

    plt.tight_layout()
    plt.show(block = False)
    

def plot_crime_category(final_df, location, year, location_type):
    """
    Creates two subplots: total crime count per category for the specified location and year, 
    and a line plot of total crime count for all categories per year in Calgary. Also prints 
    out a pivot table in the console showing crime category counts by month

    Parameters:
        final_df (DataFrame): The DataFrame containing the cleaned and merged data.
        location (str): The specific location (community, ward, or sector) to filter the data.
        year (int): The year to filter the data.
        location_type (str): The type of location (e.g., 'Community', 'Ward', or 'Sector').
        
    Returns:
        Opens a plt window displaying the plots and prints a pivot table to the console
    """
    # Create 2 subplots for Figure 1
    fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(10, 9))

    # ----- PLOT 1.1: TOTAL CRIME COUNT PER CATEGORY FOR SPECIFIED COMMUNITY AND YEAR -----
    subset = final_df[(final_df[location_type] == location) & (final_df['Year'] == year)]
    crime_by_category = subset.groupby('Category')['Crime Count'].sum().reset_index()
    crime_by_category = crime_by_category.sort_values(by='Crime Count', ascending=False)

    axes[0].bar(crime_by_category['Category'], crime_by_category['Crime Count'])
    axes[0].set_title(f'Total Crime by Category in {location_type} {location} ({year})')
    axes[0].set_xlabel('Crime Category')
    axes[0].set_ylabel('Total Crime Count')
    axes[0].tick_params(axis='x', rotation=45)
    axes[0].grid(axis='y')

    # ----- PLOT 1.2: LINE PLOT TOTAL CRIME COUNT PER YEAR ALL CATEGORIES -----
    total_crime_category = final_df.groupby(['Category', 'Year'])['Crime Count'].sum().reset_index()
    pivot_table_year = total_crime_category.pivot(index='Year', columns='Category', values='Crime Count')

    pivot_table_year.plot(ax=axes[1], marker='o')
    axes[1].set_title('Total Crime Count Per Year (For all of Calgary)')
    axes[1].set_xlabel('Year')
    axes[1].set_ylabel('Total Crime Count')
    axes[1].grid(True)
    axes[1].legend(title='Crime Category', bbox_to_anchor=(1, 1), loc='upper left')

    # --- PRINT PIVOT TABLE OF CATEGORY BY MONTH ---

    # Pivot table: Months as index, numbered category columns as values
    pivot = subset.pivot_table(index='Month', columns='Category', values='Crime Count', aggfunc='sum', fill_value=0)

    # Sort months numerically if needed
    pivot = pivot.sort_index()

    # Sort columns based on total (sum across all months) to match bar graph
    category_totals = pivot.sum()
    sorted_columns = category_totals.sort_values(ascending=False).index
    pivot = pivot[sorted_columns]  # reorder columns by descending total

    # Map categories to numeric column headers in order to fit entire data in console
    category_map = {category: str(i+1) for i, category in enumerate(pivot.columns)}
    renamed_pivot = pivot.rename(columns=category_map)

    # Add a row for totals at the bottom
    total_row = renamed_pivot.sum().to_frame().T
    total_row.index = ['Total']
    renamed_pivot = pd.concat([renamed_pivot, total_row])

    print(f"\nMonthly Crime Count Table for {location_type} {location} ({year}):")
    print(renamed_pivot)

    # Prints numeric column headers legend
    print("\nCategory Legend:")
    for category, number in category_map.items():
        print(f" {number}: {category}")
    print()

    # Layout fix
    plt.tight_layout()
    plt.show(block=False)


def plot_crime_count(final_df, location, year, location_type):
    """
    Creates two subplots: total crime count per month for the specified location and year, 
    and a line plot of total crime per month across all years in Calgary.

    Parameters:
        final_df (DataFrame): The DataFrame containing the cleaned and merged data.
        location (str): The specific location (community, ward, or sector) to filter the data.
        year (int): The year to filter the data.
        location_type (str): The type of location (e.g., 'Community', 'Ward', or 'Sector').
        
    Returns:
        Opens a plt window displaying the plots.
    """
    # ----- PLOT 2.1: TOTAL CRIME COUNT PER MONTH -----

    # Create 2 subplots for Figure 2
    fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(10, 9))  

    # Filter data frame
    subset = final_df[(final_df[location_type] == location) & (final_df['Year'] == year)]

    # Group by Month and sum Crime Count
    monthly_crime = subset.groupby('Month')['Crime Count'].sum().reset_index()
    monthly_crime = monthly_crime.sort_values(by='Month')

    # Plot on first subplot
    axes[0].bar(monthly_crime['Month'], monthly_crime['Crime Count'])
    axes[0].set_title(f'Total Crime Count per Month in {location_type} {location} ({year})')
    axes[0].set_xlabel('Month')
    axes[0].set_ylabel('Total Crime Count')
    axes[0].set_xticks(range(1, 13))
    axes[0].grid(axis='y')

    # ----- PLOT 2.2: CRIME TREND BY MONTH ACROSS YEARS -----

    # Group by Year and Month, then sum Crime Count
    crime_month = final_df.groupby(['Year', 'Month'])['Crime Count'].sum().reset_index()

    # Pivot table so rows = Month, columns = Year
    pivot_table = crime_month.pivot(index='Month', columns='Year', values='Crime Count')
    pivot_table = pivot_table.replace(0, np.nan).dropna(axis=1, how='all')

    # Plot on second subplot
    pivot_table.plot(kind='line', marker='o', ax=axes[1])

    axes[1].set_title('Total Crime Per Month by Year (For all of Calgary)')
    axes[1].set_xlabel('Month')
    axes[1].set_ylabel('Total Crime Count')
    axes[1].set_xticks(range(1, 13))
    axes[1].grid(True)
    axes[1].legend(title='Year', bbox_to_anchor=(1.05, 1), loc='upper left')

    # Plot
    plt.tight_layout()
    plt.show(block=False)


def plot_cc_vs_mdv(final_df, location, year, location_type):
    """
    Creates a scatter plot of median assessed values versus crime per capita for the specified location and year.

    Parameters:
        final_df (DataFrame): The DataFrame containing the cleaned and merged data.
        location (str): The specific location (community, ward, or sector) to filter the data.
        year (int): The year to filter the data.
        location_type (str): The type of location (e.g., 'Community', 'Ward', or 'Sector').
        
    Returns:
        Opens a plt window displaying the scatter plot.
    """

    # ----- PLOT 3: MEDIAN ASSESSED VALUES VERSUS CRIME PER CAPITA -----

    # Filter data for the selected year
    filtered_df = final_df[final_df['Year'] == year]

    # Group by Community
    agg_dict = {
        'Community Code': 'first',
        'Median Assessed Value': 'first',
        'Crime per Capita 1000': 'first',
    }

    if location_type not in ['Community']:
        agg_dict[location_type] = 'first'

    scatter_df = filtered_df.groupby(['Community']).agg(agg_dict).reset_index()

    # Scatter plot, plotting all communities
    plt.figure(figsize=(10, 6))
    plt.scatter(scatter_df['Median Assessed Value'],
                scatter_df['Crime per Capita 1000'],
                alpha=0.5, label='Other Communities')

    # Highlight the specified community or communities if multiple apply
    highlight = scatter_df[scatter_df[location_type] == location]
    if not highlight.empty:
        plt.scatter(highlight['Median Assessed Value'], 
                    highlight['Crime per Capita 1000'],
                    color='red', s=100, label=f"{location_type}: {location}",
                    edgecolor='black')
        # Add labels (community codes)
        for _, row in highlight.iterrows():
            plt.text(row['Median Assessed Value'],
                    row['Crime per Capita 1000'] + 0.2,
                    row['Community Code'],
                    fontsize=10, ha='center', color='red')

    # Plot labels
    plt.title(f'Median Assessed Value vs. Crime per Capita by Community ({year})')
    plt.xlabel('Community Median Assessed Value ($)')
    plt.ylabel('Crime per Capita 1000')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show(block=False)


def plot_cc_vs_bc(final_df, location, year, location_type):
    """
    Creates a scatter plot of total crime count versus total business count for the specified location and year.

    Parameters:
        final_df (DataFrame): The DataFrame containing the cleaned and merged data.
        location (str): The specific location (community, ward, or sector) to filter the data.
        year (int): The year to filter the data.
        location_type (str): The type of location (e.g., 'Community', 'Ward', or 'Sector').
        
    Returns:
        Opens a plt window displaying the scatter plot.
    """
    # ----- PLOT 4: TOTAL CRIME COUNT VERSUS TOTAL BUSINESS COUNT ----- 

    # filter to a specific year
    filtered_df = final_df[final_df['Year'] == year]

    # Group by Community
    agg_dict = {
        'Community Code': 'first',
        'Community Businesses Opened TD Total': 'first',
        'Crime Count': 'sum'
    }

    # Only add location_type if it is not the groupby column to avoid conflict
    if location_type not in ['Community']:
        agg_dict[location_type] = 'first'

    scatter_df = filtered_df.groupby(['Community']).agg(agg_dict).reset_index()

    # Create the scatter plot
    plt.figure(figsize=(10, 6))

    # Plot all communities
    plt.scatter(scatter_df['Community Businesses Opened TD Total'],
                scatter_df['Crime Count'],
                alpha=0.5, label='Other Communities')
    # Highlight the specified community or communities if multiple apply
    highlight = scatter_df[scatter_df[location_type] == location]
    if not highlight.empty:
        plt.scatter(highlight['Community Businesses Opened TD Total'],
                    highlight['Crime Count'],
                    color='red', s=100, edgecolor='black', label=f"{location_type}: {location}")
        # Add labels (community codes)
        for _, row in highlight.iterrows():
            plt.text(row['Community Businesses Opened TD Total'],
                    row['Crime Count'] + 100,
                    row['Community Code'],
                    fontsize=9, ha='center', color='red')

    # Plot labels
    plt.title(f'Total Crime Count vs. Business Count by Communities ({year})')
    plt.xlabel(f'Community Businesses Opened TD Total')
    plt.ylabel('Total Crime Count')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show(block=False)