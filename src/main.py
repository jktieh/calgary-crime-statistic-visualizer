"""
main.py

Entry point of the ENSF 692 Spring 2025 final project.

This script coordinates the overall program execution, including loading data,
getting user input, performing analysis, and exporting results.

Responsibilities:
- Call all main functions in proper ordercl
- Ensure no global variables are used
- Document structure clearly with inline comments

Note:
This file must be executable from the terminal and should orchestrate the full program.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def main():     

    # Load data from CSV files and perform initial cleaning    
    df = load_data()       
    print(df.head())

    community_code, year = get_user_input(df)
    # Generate and display plots based on the final DataFrame
    get_plots(df, community_code, year)



def load_data():
    # ----------- Importing Data Files ------------
        
    census2016_init = pd.read_csv('data/Census_by_Community_2016_20250617.csv')
    census2017_init = pd.read_csv('data/Census_by_Community_2017_20250617.csv')
    census2019_init = pd.read_csv('data/Census_by_Community_2019_20250617.csv')
    census2021_init = pd.read_csv('data/2021_Federal_Census_Population_and_Dwellings_by_Community_20250611.csv')
    assessment_init = pd.read_csv('data/Assessments_by_Community_20250609.csv')
    business_init = pd.read_csv('data/Calgary_Business_Licences_20250611.csv')
    wards_init = pd.read_csv('data/Communities_by_Ward_20250609.csv')
    crime_init = pd.read_csv('data/Community_Crime_Statistics_20250611.csv')

    # Print crime_init dataframe for verification
    # print(crime_init.head())

    # Find relevant categories and years in the crime dataset
    # print(crime_init['Category'].unique())
    # Print(crime_init['Year'].unique())

        # ----------- Clean Data Files ------------
        
    ### Combining and Cleaning Census Data  ----------
    ## Combining Population Census Data Sets
    # Multiple Census data sets, use all and interpolate and extrapolate for better accuracy
    census2016 = census2016_init[['COMM_CODE', 'CNSS_YR', 'RES_CNT']].copy()
    census2017 = census2017_init[['COMM_CODE', 'CNSS_YR', 'RES_CNT']].copy()
    census2019 = census2019_init[['COMM_CODE', 'CNSS_YR', 'RES_CNT']].copy()
    census2021 = census2021_init[['COMMUNITY_CODE', 'TOTAL_POP_HOUSEHOLD']].copy()
    census2021['CNSS_YR'] = 2021
    census2021.rename(columns={'COMMUNITY_CODE': 'COMM_CODE', 'TOTAL_POP_HOUSEHOLD': 'RES_CNT'}, inplace=True)

    # combining of different year census dats sets
    census = pd.concat([census2016, census2017, census2019, census2021], ignore_index=True)
    census.rename(columns={'CNSS_YR': 'Year', 'RES_CNT': 'Population Household'}, inplace=True)

    # convert years into columns for each year
    census = census.set_index(['COMM_CODE', 'Year'])
    census = census['Population Household'].unstack()
    census.dropna(inplace=True)
    # add columns for interpolated and extrapolated extra years needed and ordering columns based on year
    census[['2018', '2020', '2022', '2023', '2024']] = np.nan
    census.columns = census.columns.astype(str)
    census = census.reindex(sorted(census.columns), axis=1)

    # converting data in given data sets to int to allow proper computation
    census[['2016', '2017', '2019', '2021']] = census[['2016', '2017', '2019', '2021']].astype(int)

    ## Interpolation and Extrapolation
    # interpolate for 2018, 2020 years
    census['2016_2017'] = census['2017'] - census['2016']
    census['2017_2019'] = (census['2019'] - census['2017']) // 2
    census['2018'] = census['2017'] + census['2017_2019']
    census['2019_2021'] = (census['2021'] - census['2019']) // 2
    census['2020'] = census['2019'] + census['2019_2021']
    # take average of slopes for population change from given datasets, and averages for a general change to extrapolate
    census['slope'] = (census['2016_2017'] + census['2017_2019'] + census['2019_2021']) // 3
    census['2022'] = (census['2021'] + census['slope'])
    census['2023'] = census['2022'] + census['slope']
    census['2024'] = census['2023'] + census['slope']
    # remove no longer needed columns
    census.drop(['2016_2017', '2017_2019', '2019_2021', 'slope'], axis=1, inplace=True)

    # convert individual year columns into a single index year column
    census = census.stack('Year').reset_index()
    census.columns = ['COMM_CODE', 'Year', 'TOTAL_POP_HOUSEHOLD']
    census['Year'] = census['Year'].astype(int)

    # census = pd.merge(census, census2021_init[['COMMUNITY_CODE', 'COMMUNITY_NAME']], left_on = 'Community Code', right_on='COMMUNITY_CODE').drop(['COMMUNITY_CODE'], axis=1)
        
    ### Cleaning Business data ----------
    business = business_init.drop(['GETBUSID', 'TRADENAME', 'HOMEOCCIND', 'ADDRESS', 'LICENCETYPES', 'EXP_DT', 'JOBSTATUSDESC', 'POINT', 'GLOBALID'], axis=1)
    business['BUSINESS_COUNT'] = 1
    business.dropna(inplace = True)
    # converting date format into year and month columns
    business['Year'] = business['FIRST_ISS_DT'].astype(str).str[:4].astype(int)
    business['Month'] = business['FIRST_ISS_DT'].astype(str).str[5:7].astype(int)
    business.drop(['FIRST_ISS_DT'], axis=1, inplace = True)
    # print(business.isnull().any())
    # print(business.shape)
    business = business.groupby(['COMDISTNM', 'COMDISTCD', 'Year', 'Month']).sum(numeric_only=True).reset_index()
    business = business.sort_values(['Year', 'Month'], ascending=[True, True])
    business['Community Business Total'] = business.groupby('COMDISTCD')['BUSINESS_COUNT'].cumsum()
    # print(business.shape)

    # business.to_csv('business.csv', index=False)

    ## Cleaning Assessment data ----------
    assessment = assessment_init
    # assessment['Community name'] = assessment['Community name'].str.capitalize()
    # assessment['Estimated Community Property Base In Millions ($)'] = assessment['Number of taxable accounts'] * assessment['Median assessed value'] / 1000000

    # Instead of taking data by year, take the average of the two years. When using data, will include a disclaimer
    assessment = assessment.groupby('COMM_CODE', as_index=False)[[
        'Number of taxable accounts',
        'Median assessed value',
    ]].mean()
    # print(assessment.isnull().any())

    ## Cleaning Wards data ----------
    wards = wards_init.drop(['SRG', 'COMM_STRUCTURE'], axis=1)
    # print(wards.isnull().any())

    ## Cleaning Crime data ----------
    crime = crime_init
    # Sort to ensure months are in order
    crime = crime.sort_values(by=['Community', 'Year', 'Month'])

    # Group by community and year, and cumsum over months
    crime['Community Crime MTD'] = crime.groupby(['Community', 'Year', 'Month'])['Crime Count'].cumsum()
    crime['Max Community Crime MTD'] = crime.groupby(['Community', 'Year', 'Month'])['Community Crime MTD'].transform('max')
    # crime.to_csv('crime.csv', index=False)
    # print(crime.isnull().any())

    ### -------------------- MERGING OF DATA --------------------

    ## Merge 1 wards plus business --------------------
    # print("wards size:", wards.shape)
    # print("business size:", business.shape)
    merge1_df = pd.merge(wards, business, how='outer', left_on='COMM_CODE', right_on='COMDISTCD')
    merge1_df['Community'] = merge1_df['NAME']
    merge1_df = merge1_df.drop(['COMDISTNM', 'COMDISTCD', 'NAME'], axis=1)
    # print("merge1 size:", merge1_df.shape)
    # print(merge1_df.head())
    # print("merge1 columns:", merge1_df.columns)
    # print(merge1_df.isnull().any())
    # merge1_df.to_csv('check1.csv', index=False)

    ## Merge 1.5 wards plus crime --------------------
    # print("crime size:", crime.shape)
    merge1_5_df = pd.merge(wards, crime, how='outer', left_on='NAME', right_on='Community').drop(['NAME'], axis=1)
    # print("merge1.5 size:", merge1_5_df.shape)
    # merge1_5_df.to_csv('check1_5.csv', index=False)
    # print(merge1_5_df.head())
    # print("merge1.5 columns:", merge1_5_df.columns)
    # print(merge1_5_df.isnull().any())

    ## Merge 2 - merge1 and merge1.5 --------------------
    merge2_df = pd.merge(merge1_df, merge1_5_df, how="outer",
                        left_on = ['COMM_CODE', 'CLASS', 'CLASS_CODE', 'SECTOR', 'WARD_NUM', 'Community', 'Year', 'Month'],
                        right_on = ['COMM_CODE', 'CLASS', 'CLASS_CODE', 'SECTOR', 'WARD_NUM', 'Community', 'Year', 'Month'])
    # print("merge2 size:", merge2_df.shape)
    # print(merge2_df.head())
    # print(merge2_df.isnull().any())
    # print("merge2 columns:", merge2_df.columns)
    # merge2_df.to_csv('check2.csv', index=False)

    ## Merge 3 plus assessment --------------------
    # print("assessment size:", assessment.shape)
    merge3_df = pd.merge(merge2_df, assessment, how='outer', left_on='COMM_CODE', right_on='COMM_CODE')
    # print("merge3 size:", merge3_df.shape)
    # print("merge3 columns:", merge3_df.columns)
    # print(merge3_df.head())
    # merge3_df.to_csv('check3.csv', index=False)

    ## Merge 4 plus census --------------------
    # print("census size:", census.shape)
    merge4_df = pd.merge(merge3_df, census, how='outer', left_on=['COMM_CODE', 'Year'], right_on=['COMM_CODE', 'Year'])

    # print("merge4 size:", merge4_df.shape)
    # print(merge4_df.head())
    # merge4_df.to_csv('check4.csv', index=False)

    ## Final Data --------------------
    final_df = merge4_df
    final_df = merge4_df.sort_values(['COMM_CODE', 'Year', 'Month'])
    final_df['Crime per Capita'] = (final_df['Max Community Crime MTD'] / final_df['TOTAL_POP_HOUSEHOLD']) * 1000
    final_df = final_df.set_index(['COMM_CODE', 'Community', 'Year', 'Month']).reset_index()
    # filter data to 2018 and after
    final_df = final_df[final_df['Year'] > 2017]
    final_df.to_csv('check5.csv', index=False)

    # Rename columns and make title case
    final_df = final_df.rename(columns={
        'COMM_CODE': 'Community Code',
        'CLASS': 'Class',
        'CLASS_CODE': 'Class Code',
        'SECTOR': 'Sector',
        'WARD_NUM': 'Ward Number',
        'BUSINESS_COUNT': 'Businesses Opened',
        'Number of taxable accounts': 'Taxable Accounts',
        'Median assessed value': 'Median Assessed Value',
        'TOTAL_POP_HOUSEHOLD': 'Population Household',
    })

    print("final_df columns:", final_df.columns)
    # print first five rows
    print(final_df.shape)
    final_df.tail()
    final_df.to_csv('check5.csv', index=False)

    # final_df.to_excel("final_dataframe.xlsx", index=True, header=True)

    return final_df



def get_plots(final_df, community_code, year):
    """
    Generates and displays various plots based on the final DataFrame.

    Args:
        final_df (DataFrame): The final DataFrame containing the cleaned and merged data.
    """
    # Create 2 subplots for Figure 1
    fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(10, 9))

    # ----- PLOT 1.1: TOTAL CRIME COUNT PER CATEGORY FOR SPECIFIED COMMUNITY AND YEAR -----
    subset = final_df[(final_df['Community Code'] == community_code) & (final_df['Year'] == year)]
    crime_by_category = subset.groupby('Category')['Crime Count'].sum().reset_index()
    crime_by_category = crime_by_category.sort_values(by='Crime Count', ascending=False)

    axes[0].bar(crime_by_category['Category'], crime_by_category['Crime Count'])
    axes[0].set_title(f'Total Crime by Category in {community_code} ({year})')
    axes[0].set_xlabel('Crime Category')
    axes[0].set_ylabel('Total Crime Count')
    axes[0].tick_params(axis='x', rotation=45)
    axes[0].grid(axis='y')

    # ----- PLOT 1.2: LINE PLOT TOTAL CRIME COUNT PER YEAR ALL CATEGORIES -----
    total_crime_category = final_df.groupby(['Category', 'Year'])['Crime Count'].sum().reset_index()
    pivot_table = total_crime_category.pivot(index='Year', columns='Category', values='Crime Count')

    pivot_table.plot(ax=axes[1], marker='o')
    axes[1].set_title('Total Crime Count Per Year (All Communities)')
    axes[1].set_xlabel('Year')
    axes[1].set_ylabel('Total Crime Count')
    axes[1].grid(True)
    axes[1].legend(title='Crime Category', bbox_to_anchor=(1, 1), loc='upper left')

    # Layout fix
    plt.tight_layout()
    plt.show()


    # ----- PLOT 2.1: TOTAL CRIME COUNT PER MONTH -----

    # Create 2 subplots for Figure 2
    fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(10, 9))  

    # Filter data frame
    subset = final_df[(final_df['Community Code'] == community_code) & (final_df['Year'] == year)]

    # Group by Month and sum Crime Count
    monthly_crime = subset.groupby('Month')['Crime Count'].sum().reset_index()
    monthly_crime = monthly_crime.sort_values(by='Month')

    # Plot on first subplot
    axes[0].bar(monthly_crime['Month'], monthly_crime['Crime Count'])
    axes[0].set_title(f'Total Crime Count per Month in {community_code} ({year})')
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

    axes[1].set_title('Total Crime Per Month by Year')
    axes[1].set_xlabel('Month')
    axes[1].set_ylabel('Total Crime Count')
    axes[1].set_xticks(range(1, 13))
    axes[1].grid(True)
    axes[1].legend(title='Year', bbox_to_anchor=(1.05, 1), loc='upper left')

    # Plot
    plt.tight_layout()
    plt.show()

    # ----- PLOT 3: MEDIAN ASSESSED VALUES VERSUS CRIME PER CAPITA -----

    # Filter data for the selected year
    filtered_df = final_df[final_df['Year'] == year]

    # Group by Community: take average values
    scatter_df = filtered_df.groupby('Community Code').agg({
        'Median Assessed Value': 'mean',
        'Crime per Capita': 'mean'
    }).reset_index()

    # Scatter plot
    plt.figure(figsize=(10, 6))

    # Plot all communities
    plt.scatter(scatter_df['Median Assessed Value'], scatter_df['Crime per Capita'], alpha=0.6, label='Other Communities')

    # Highlight the specified community
    highlight = scatter_df[scatter_df['Community Code'] == community_code]
    if not highlight.empty:
        plt.scatter(highlight['Median Assessed Value'], highlight['Crime per Capita'],
                    color='red', s=100, label=community_code, edgecolor='black')
        plt.text(highlight['Median Assessed Value'].values[0],
                highlight['Crime per Capita'].values[0] + 1,
                community_code,
                fontsize=10, ha='center', color='red')

    # --- Plot labels ---
    plt.title(f'Median Assessed Value vs. Crime per Capita by Community ({year})')
    plt.xlabel('Median Assessed Value ($)')
    plt.ylabel('Crime per Capita')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()
    
    # ----- PLOT 4: TOTAL CRIME COUNT VERSUS TOTAL BUSINESS COUNT ----- 

    # Define community to highlight
    community_code = 'BRI'

    # Optional: filter to a specific year
    # year = 2022
    # filtered_df = final_df[final_df['Year'] == year]
    # Otherwise, use full dataset
    filtered_df = final_df

    # Group by community
    scatter_df = filtered_df.groupby('Community Code').agg({
        'Community Business Total': 'mean', 
        'Crime Count': 'sum'
    }).reset_index()

    # Create the scatter plot
    plt.figure(figsize=(10, 6))

    # Plot all communities
    plt.scatter(scatter_df['Community Business Total'], scatter_df['Crime Count'], alpha=0.6, label='Other Communities')

    # Highlight the selected community
    highlight = scatter_df[scatter_df['Community Code'] == community_code]
    if not highlight.empty:
        plt.scatter(highlight['Community Business Total'], highlight['Crime Count'],
                    color='red', s=100, edgecolor='black', label=community_code)
        plt.text(highlight['Community Business Total'].values[0],
                highlight['Crime Count'].values[0] + 200,  # adjust offset as needed
                community_code,
                fontsize=10, ha='center', color='red')

    # Add plot details
    plt.title('Total Crime Count vs. Community Business Total')
    plt.xlabel('Community Business Total')
    plt.ylabel('Total Crime Count')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()
    

    # # Create a single figure with 3 subplots (3 rows, 1 column)
    # fig, axes = plt.subplots(3, 1, figsize=(10, 18))  # Adjust height for spacing

    # # ---------------- Plot 1: Total Crime Count Per Year by Crime Category ----------------
    # # Group by Category and Year, then sum Crime Count
    # plot1_df = final_df.groupby(['Category', 'Year'])['Crime Count'].sum().reset_index()
    # # Create a pivot table where rows = Year, columns = Category, values = total crime count
    # plot1_pt = plot1_df.pivot(index='Year', columns='Category', values='Crime Count')
    # # Plot each category's crime trend across years
    # plot1_pt.plot(kind='line', marker='o', ax=axes[0])
    # axes[0].set_title('Total Crime Count Per Year')
    # axes[0].set_xlabel('Year')
    # axes[0].set_ylabel('Total Crime Count')
    # axes[0].grid(True)
    # axes[0].legend(title='Crime Category', fontsize='small', loc='upper left')

    # # ---------------- Plot 2: Total Crime Per Month by Year ----------------
    # # Group by Year and Month, then sum Crime Count
    # plot2_df = final_df.groupby(['Year', 'Month'])['Crime Count'].sum().reset_index()
    # # Create a pivot table where rows = Month, columns = Year, values = total crime count
    # plot2_pt = plot2_df.pivot(index='Month', columns='Year', values='Crime Count')
    # # Replace all 0s with NaN and drop years (columns) where all values are NaN
    # plot2_pt = plot2_pt.replace(0, np.nan).dropna(axis=1, how='all')
    # # Plot total crime per month for each year
    # plot2_pt.plot(kind='line', marker='o', ax=axes[1])
    # axes[1].set_title('Total Crime Per Month by Year')
    # axes[1].set_xlabel('Month')
    # axes[1].set_ylabel('Total Crime Count')
    # axes[1].set_xticks(range(1, 13))
    # axes[1].grid(True)
    # axes[1].legend(title='Year', fontsize='small', loc='upper left')

    # # ---------------- Plot 3: Year-over-Year % Change in Total Crime ----------------
    # # Group by Year and get Total of Crime Count
    # plot3_df = final_df.groupby('Year')['Crime Count'].sum().sort_index()
    # # Remove years with 0 or NaN crime count
    # plot3_df = plot3_df[plot3_df > 0]
    # # Compute percent change
    # plot3_pct_change = plot3_df.pct_change() * 100
    # plot3_pct_change.dropna().plot(kind='bar', ax=axes[2], color='coral')
    # axes[2].set_title('YoY % Change in Total Crime')
    # axes[2].set_xlabel('Year')
    # axes[2].set_ylabel('Percent Change (%)')
    # axes[2].axhline(0, color='gray', linestyle='--')
    # axes[2].grid(axis='y')

    # # ---------------- Layout adjustment ----------------
    # plt.tight_layout()
    # plt.show()

   

def get_user_input(df):
    # Get unique valid values
    valid_community_codes = df['Community Code'].unique()
    valid_years = df['Year'].unique()

    # Get and validate community code
    print(f"Community Codes: {', '.join(map(str, valid_community_codes))}")
    while True:
        community_code = input("Enter a valid Community Code (e.g. ): ").strip()
        if community_code in valid_community_codes:
            break
        print(f"Invalid code. Available codes: {', '.join(map(str, valid_community_codes))}")

    # Get and validate year
    print(f"Available years: {', '.join(map(str, valid_years))}")
    while True:
        year_input = input("Enter a valid Year (e.g., 2022): ").strip()
        if year_input.isdigit():
            year = int(year_input)
            if year in valid_years:
                break
        print(f"Invalid year. Available years: {', '.join(map(str, sorted(valid_years)))}")

    return community_code, year

    pass  # Implement user input logic here if needed


if __name__ == "__main__":
    main()