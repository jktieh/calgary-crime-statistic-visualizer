import numpy as np
import pandas as pd
import os
import pandas as pd
import openpyxl

def create_dataframe():
    """
    Summary: This functions imports multiple data files, cleans them, and merges them into a single DataFrame.

    Returns: 
        final_df: A cleaned and merged DataFrame with the following columns:
         - Community Code, Community, Year, Month, Sector, Ward Number
         - Category, Crime Count, Community Crime MTD Total
         - Businesses Opened, Community Businesses Opened TD Total
         - Taxable Accounts, Median Assessed Value, Population Household
         - Crime per Capita 1000
    """
    # ----------- Importing Data Files ------------
        
    census2016_init = pd.read_csv('data/Census_by_Community_2016_20250617.csv')
    census2017_init = pd.read_csv('data/Census_by_Community_2017_20250617.csv')
    census2019_init = pd.read_csv('data/Census_by_Community_2019_20250617.csv')
    census2021_init = pd.read_csv('data/2021_Federal_Census_Population_and_Dwellings_by_Community_20250611.csv')
    assessment_init = pd.read_csv('data/Assessments_by_Community_20250609.csv')
    business_init = pd.read_csv('data/Calgary_Business_Licences_20250611.csv')
    wards_init = pd.read_csv('data/Communities_by_Ward_20250609.csv')
    crime_init = pd.read_csv('data/Community_Crime_Statistics_20250611.csv')

    # ----------- Clean Data Files ------------
    
    ### Combining and Cleaning Census Data  ----------
    # Combining Population Census Data Sets, Multiple Census data sets, 
    # use all and interpolate and extrapolate missing for better accuracy
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
    
    ### Cleaning Business data ----------
    business = business_init.drop(['GETBUSID', 'TRADENAME', 'HOMEOCCIND', 'ADDRESS', 'LICENCETYPES', 'EXP_DT', 'JOBSTATUSDESC', 'POINT', 'GLOBALID'], axis=1)
    business['BUSINESS_COUNT'] = 1
    business.dropna(inplace = True)
    # converting date format into year and month columns
    business['Year'] = business['FIRST_ISS_DT'].astype(str).str[:4].astype(int)
    business['Month'] = business['FIRST_ISS_DT'].astype(str).str[5:7].astype(int)
    business.drop(['FIRST_ISS_DT'], axis=1, inplace = True)
    # creating column for businesses opened to date in a community based on year and month 
    business = business.groupby(['COMDISTNM', 'COMDISTCD', 'Year', 'Month']).sum(numeric_only=True).reset_index()
    business = business.sort_values(['Year', 'Month'], ascending=[True, True])
    business['Community Businesses Opened TD Total'] = business.groupby('COMDISTCD')['BUSINESS_COUNT'].cumsum()

    ## Cleaning Assessment data ----------
    assessment = assessment_init

    # Instead of taking data by year, take the average of the two years. When using data, will include a disclaimer
    assessment = assessment.groupby('COMM_CODE', as_index=False)[[
        'Number of taxable accounts',
        'Median assessed value',
    ]].mean()

    ## Cleaning Wards data ----------
    wards = wards_init.drop(['CLASS', 'CLASS_CODE', 'SRG', 'COMM_STRUCTURE'], axis=1)

    ## Cleaning Crime data ----------
    crime = crime_init
    # Sort to ensure months are in order
    crime = crime.sort_values(by=['Community', 'Year', 'Month'])
    # Group by community and year, and cumsum over months
    crime['Community Crime MTD'] = crime.groupby(['Community', 'Year', 'Month'])['Crime Count'].cumsum()
    crime['Community Crime MTD Total'] = crime.groupby(['Community', 'Year', 'Month'])['Community Crime MTD'].transform('max')
    crime.drop(['Community Crime MTD'], axis=1, inplace=True)

    ### -------------------- MERGING OF DATA --------------------

    ## Merge 1 wards plus business --------------------
    merge1_df = pd.merge(wards, business, how='outer', left_on='COMM_CODE', right_on='COMDISTCD')
    merge1_df['Community'] = merge1_df['NAME']
    merge1_df = merge1_df.drop(['COMDISTNM', 'COMDISTCD', 'NAME'], axis=1)

    ## Merge 1.5 wards plus crime --------------------
    merge1_5_df = pd.merge(wards, crime, how='outer', left_on='NAME', right_on='Community').drop(['NAME'], axis=1)

    ## Merge 2 - merge1 and merge1.5 --------------------
    merge2_df = pd.merge(merge1_df, merge1_5_df, how="outer",
                        left_on = ['COMM_CODE', 'WARD_NUM', 'SECTOR', 'Community', 'Year', 'Month'],
                        right_on = ['COMM_CODE', 'WARD_NUM', 'SECTOR', 'Community', 'Year', 'Month'])

    ## Merge 3 plus assessment --------------------
    merge3_df = pd.merge(merge2_df, assessment, how='outer', left_on='COMM_CODE', right_on='COMM_CODE')

    ## Merge 4 plus census --------------------
    merge4_df = pd.merge(merge3_df, census, how='outer', left_on=['COMM_CODE', 'Year'], right_on=['COMM_CODE', 'Year'])

    ## Final Data --------------------
    final_df = merge4_df
    final_df = merge4_df.sort_values(['COMM_CODE'])
    # Create Crime per capita 1000 date
    final_df['Crime per Capita 1000'] = (final_df['Community Crime MTD Total'] / final_df['TOTAL_POP_HOUSEHOLD']) * 1000
    # filter data to 2018 and after and before 2025
    final_df = final_df[(final_df['Year'] > 2017) & (final_df['Year'] < 2025)]
    final_df['Year'] = final_df['Year'].astype(int).astype(str)
    final_df['WARD_NUM'] = final_df['WARD_NUM'].apply(lambda x: str(int(x)) if pd.notna(x) else "")

    # Rename columns and make title case
    final_df = final_df.rename(columns={
        'COMM_CODE': 'Community Code',
        'SECTOR': 'Sector',
        'WARD_NUM': 'Ward Number',
        'BUSINESS_COUNT': 'Businesses Opened',
        'Number of taxable accounts': 'Taxable Accounts',
        'Median assessed value': 'Median Assessed Value',
        'TOTAL_POP_HOUSEHOLD': 'Population Household',
    })

    # Reorder columns for better organization
    final_df = final_df[['Community Code', 'Community', 'Year', 'Month', 'Sector', 'Ward Number',
        'Category', 'Crime Count', 'Community Crime MTD Total',
        'Businesses Opened', 'Community Businesses Opened TD Total',
        'Taxable Accounts', 'Median Assessed Value',
        'Population Household', 'Crime per Capita 1000']]

    # final sort of year and month columns
    final_df = final_df.sort_values(['Year', 'Month'], ascending=[True, True])
    final_df = final_df.set_index(['Community Code', 'Community', 'Year', 'Month']).reset_index()

    # final_df.to_excel("final_dataframe.xlsx", index=True, header=True)

    return final_df


def export_to_excel(df, filename='output.xlsx', sheet_name='Sheet1'):
    """
    Exports a DataFrame to an Excel file.

    Parameters:
        df (pd.dataframe): pandas DataFrame 
        filename (str): name of the Excel file to create
        sheet_name (str): name of the worksheet
    """
    # Create a multi index dataframe with Community Code, Community, Year, Month

    try:
        df = df.set_index(['Community Code', 'Community', 'Year', 'Month'])
        df.to_excel(filename, sheet_name=sheet_name, index=True)
        print(f"DataFrame exported to '{filename}' with index.")
    except Exception as e:
        print(f"Export failed: {e}")

