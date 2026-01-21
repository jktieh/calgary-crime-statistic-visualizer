from dataVisualizer import show_regions_available

def get_location(df):
    """
    Prompts the user to select a location type (Sector, Ward, or Community) and redirects the 
    user to another method to get the Sector, Ward, or Community.
    
    Parameters:
        df (pd.DataFrame): The DataFrame containing the crime statistics data.
    Returns:
        (str): Specified string representing the location types column name in the main df
        (str): name of the specific location/region chosen
    """
    print("Data can be analyzed in either City Sectors, City Wards, or City Communities.")
    while True:
        location_in = input("Type 'Sector' 'Ward' or 'Community' for the type of location you wish to analyze data on: ")
        location = location_in.strip().upper()
        try:
            if (location == 'SECTOR'):
                return 'Sector', get_sector(df)
            elif (location == 'WARD'):
                return 'Ward Number', get_ward(df)
            elif (location == 'COMMUNITY'):
                return get_community(df)
            else:
                raise KeyError("\n" + location_in + ' is not a valid location. Please try again.\n')
        except KeyError as e:
            print(e.args[0])


def get_community(df):
    """
    Prompts the user to enter a community name or code available in the dataset and returns the community.
    
    Parameters:
        df (pd.DataFrame): The DataFrame containing the crime statistics data.
    Returns:
        (str): the string 'Community'
        (str): name of the specific community chosen
    """
    table = input(f"Would you like to view a list of valid Communities? (Y/N): ").strip().upper()
    if table == 'Y':
        show_regions_available(df, 'Community')

    while True:
        # formating input to be case insensitive and ignore spaces at beginning and end
        community = input("Please enter a community by name or 3 character code to analyze data on: ").strip().upper()
        df['Community Code'] = df['Community Code'].str.upper()
        df['Community'] = df['Community'].str.upper()
        try:
            if (community not in df['Community Code'].values) and (community not in df['Community'].values):
                raise KeyError('\nThis community was not found in the data. Please try again.\n')
            if community in df['Community Code'].values:
                return 'Community', df.loc[df['Community Code'] == community, 'Community'].iloc[0]
            elif  community in df['Community'].values:
                return 'Community', df.loc[df['Community'] == community, 'Community'].iloc[0]
        except KeyError as e:
            print(e.args[0])


def get_year(df):
    """
    Prompts the user to enter a year available in the dataset and returns the year.
    
    Parameters:
        df (pd.DataFrame): The DataFrame containing the crime statistics data.
    Returns:
        (str): specific year chosen
    """
    while True:
        year = input("Please enter the year of data to analyze (2018-2024): ").strip()
        try:
            if (year not in df['Year'].values):
                raise KeyError('\nThis year was not found in the data. Please try again.\n')
            if year in df['Year'].values:
                return df.loc[df['Year'] == year, 'Year'].iloc[0]
            elif year == 'Q':
                return year
        except KeyError as e:
            print(e.args[0])


def get_ward(df):
    """
    Prompts the user to enter a ward number available in the dataset and returns the ward number.
    
    Parameters:
        df (pd.DataFrame): The DataFrame containing the crime statistics data.
    Returns:
        (str): the specific ward number chosen
    """
    table = input(f"Would you like to view a list of valid Wards? (Y/N): ").strip().upper()
    if table == 'Y':
        show_regions_available(df, 'Ward Number')

    while True:
        # formating input to be case insensitive and ignore spaces at beginning and end
        ward = input("Please enter the city ward to analyze data on (i.e. 1-14): ")
        try:
            if (ward not in df['Ward Number'].values):
                raise KeyError('\nThis city ward was not found in the data. Please try again.\n')
            if ward in df['Ward Number'].values:
                return df.loc[df['Ward Number'] == ward, 'Ward Number'].iloc[0]
            elif ward == 'Q':
                return ward
        except KeyError as e:
            print(e.args[0])


def get_sector(df):
    """
    Prompts the user to enter a sector name available in the dataset and returns the sector name.
    
    Parameters:
        df (pd.DataFrame): The DataFrame containing the crime statistics data.
    Returns:
        (str): name of the city sector chosen
    """
    table = input(f"Would you like to view a list of valid Sectors? (Y/N): ").strip().upper()
    if table == 'Y':
        show_regions_available(df, 'Sector')

    while True:
        # formating input to be case insensitive and ignore spaces at beginning and end
        sector = input("Please enter the city sector to analyze data on: ").strip().upper().replace(" ", "")
        df['Sector'] = df['Sector'].str.upper()
        try:
            if sector in df['Sector'].values:
                return df.loc[df['Sector'] == sector, 'Sector'].iloc[0]
            elif sector == 'CITYCENTRE':
                return 'CENTRE'
            elif (sector not in df['Sector'].values):
                raise KeyError('\nThis city sector was not found in the data. Please try again.\n')
        except KeyError as e:
            print(e.args[0])
