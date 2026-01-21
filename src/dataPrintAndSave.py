import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import os

def save_plot(location_type, year, plot_name, location):
    """
    Saves the current matplotlib plot to the 'images' directory as a png.

    Parameters:
        location_type (str): 'Community', 'Ward', or 'Sector'
        year (int): Year as int
        plot_name (str): A short name describing the plot (e.g., 'crimecategoryplot')
        location (str): Location name or number
    """
    # Build filename
    location = str(location).replace(" ", "_")
    ltype = location_type.replace(" ", "")
    filename = f"{ltype}_{year}_{location}_{plot_name}.png"

    # Build path
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # One level above /src
    images_dir = os.path.join(base_dir, "images")
    os.makedirs(images_dir, exist_ok=True)

    # Saving plot to file path
    filepath = os.path.join(images_dir, filename)
    fig = plt.gcf()
    fig.savefig(filepath, bbox_inches='tight', dpi=300)
    print(f"Plot saved as: {filepath}")


def print_describe(df):
    """
    Prints overall statistics of the final dataset, specifically for Crime Count, 
    Crime per Capita 1000, Businesses Opened, and Median Assessed Value if applicable

    Parameters:
        df (pd.DataFrame): The DataFrame containing the final crime data.

    Returns:
        Prints the describe method statistics directly to the console.
    """
    # removal of any inf values with nan
    describe_df = df.replace([np.inf, -np.inf], np.nan)
    
    # grouping data by main indices and chooses sum or first as required
    describe_df = describe_df.groupby(['Year', 'Month', 'Community'], as_index=False).agg({
        'Crime Count': 'sum',
        'Crime per Capita 1000': 'first',  # these don't change within community/month
        'Businesses Opened': 'first',
    })
    
    # grouping data to produce 1 row for each month
    describe_df = describe_df.groupby(['Year', 'Month'], as_index=False).agg({
        'Crime Count': 'sum',
        'Crime per Capita 1000': 'mean',
        'Businesses Opened': 'sum',
    })
    
    # applying describe method
    describe_stats = describe_df[['Crime Count',
                                  'Crime per Capita 1000',
                                  'Businesses Opened',
                                  ]].describe()
    
    # similar method for assessment column case but grouping is different
    assessment_stats = df.replace([np.inf, -np.inf], np.nan)
    assessment_stats = assessment_stats.groupby(['Community'], as_index=False).agg({'Median Assessed Value': 'first'})
    median_assess_describe = assessment_stats['Median Assessed Value'].describe()
    
    describe_stats_t = describe_stats.T
    
    # concatonating median assessment as a new row
    describe_stats_t.loc['Median Assessed Value'] = median_assess_describe
    
    # Transpose back to original format (stats as rows)
    describe_stats_final = describe_stats_t.T

    # convert median assessed values into numeric instead of scientific
    describe_stats_final['Median Assessed Value'] = describe_stats_final['Median Assessed Value'].apply(
        lambda x: f"{x:,.2f}" if pd.notna(x) else x
    )
    
    # Print final table
    print("================ Overall Stats of the dataset oganized by Months ==================" \
    "\n===================================================================================")
    print(describe_stats_final)
    print("===================================================================================")


def location_year_summary(df, location, year, location_type):
    """
    Generates a summary of crime statistics for the user specified location and year, including total population,
    median assessed value, number of businesses, total crime incidents, crime per 1000 residents, and business 
    density per 1000 residents.

    Parameters:
        df (pd.DataFrame): The DataFrame containing the final dataset
        location (str): The name of the location to analyze (e.g., community name, ward number, or sector).
        year (int): The year of the data to analyze. (2018-2024)
        location_type (str): The type of location (e.g., 'Community', 'Ward', or 'Sector').

    Returns:
        Prints a short table of statistics directly to the console.
    """
    # Filter by year
    year_df = df[df['Year'] == year]

    # Special handling for blank/NaN wards
    if location_type == 'Ward Number':
        year_df = year_df[year_df['Ward Number'].notna() & (year_df['Ward Number'].astype(str).str.strip() != '')]

    # Case for non matching location
    if year_df.empty or location not in year_df[location_type].unique():
        print(f"No data found for {location_type}: {location} in {year}.")
        return

    # Aggregate stats, groupby differently depending on location type to get proper desired stats
    if (location_type == 'Community'):
        grouped = year_df.groupby(location_type).agg({
            'Population Household': 'first',
            'Median Assessed Value': 'first',
            'Community Businesses Opened TD Total': 'max',
            'Crime Count': 'sum'
        }).reset_index()
    else:
        grouped = year_df.groupby('Community').agg({
            location_type: 'first',
            'Population Household': 'first',
            'Median Assessed Value': 'first',
            'Community Businesses Opened TD Total': 'max',
            'Crime Count': 'sum'
        }).reset_index()
        grouped = grouped.groupby(location_type).agg({
            'Population Household': 'sum',
            'Median Assessed Value': 'mean',
            'Community Businesses Opened TD Total': 'sum',
            'Crime Count': 'sum'
        }).reset_index()

    # Calculate per capita for the year
    grouped['Crime per 1000'] = grouped['Crime Count'] / grouped['Population Household'] * 1000
    grouped['Business Density'] = grouped['Community Businesses Opened TD Total'] / grouped['Population Household'] * 1000

    # Rank each column, skipping NaNs
    stat_cols = [
        'Population Household',
        'Median Assessed Value',
        'Community Businesses Opened TD Total',
        'Crime Count',
        'Crime per 1000',
        'Business Density'
    ]

    # creating ranking of chosen stats to all stats
    for col in stat_cols:
        ascending = False
        valid = grouped[col].notna()
        grouped[f'{col} Rank'] = np.nan
        grouped.loc[valid, f'{col} Rank'] = grouped.loc[valid, col].rank(ascending=ascending, method='min')

    row = grouped[grouped[location_type] == location].iloc[0]

    # Printing of the summary table
    print(f"\nSummary for {location_type}: {location} ({year})")
    print("-" * 60)

    for col, label in zip(stat_cols, [
        "Total Population",
        "Median Assessed Value",
        "Number of Businesses",
        "Total Crime Incidents",
        "Crime per 1,000 residents",
        "Business Density (/1000)"
    ]):
        value = row[col]
        average = grouped[col].mean()
        rank = row[f'{col} Rank']
        total = grouped[col].notna().sum()
        print(format_line(label, round(value, 2) if pd.notna(value) else value, average, rank, total))

    print("-" * 60)
    print("*Note: The larger the value, the higher the rank" \
    "\n**Notes: If the location type is a sector or ward, the Median Assessed Value"
    "\n         is an average of the communities within these regions")
    

def format_line(label, val, avg, rank, total):
    """
    Formats a summary line displaying a statistical value along with its average and rank.

    Parameters:
        label (str): The label or descriptor for the metric (e.g., "Total Population").
        val (float): The actual value for the selected region. May be NaN.
        avg (float): The average value across all regions (including NaNs for comparison).
        rank (float): The rank of the selected region among regions with valid (non-NaN) values.
        total (int): The total number of valid entries used to calculate the rank.

    Return:
        A formatted string like:
        "Total Population             : 6,200 (Avg: 5,812) | Rank: 3/14"
        or if value is missing:
        "Total Population             : N/A (Avg: 5,812) | Rank: N/A/14"
    """
    avg_fmt = f"{avg:,.0f}" if not pd.isna(avg) else "N/A"
    if pd.isna(val):
        return f"{label:<30}: N/A (Avg: {avg_fmt}) | Rank: N/A/{total}"
    return f"{label:<30}: {val:,} (Avg: {avg_fmt}) | Rank: {int(rank)}/{total}"