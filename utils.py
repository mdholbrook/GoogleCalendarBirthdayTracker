import os
import pandas as pd
from datetime import datetime


def correct_matt(names):

    for i in range(len(names)):

        if 'Matthew' in names[i]:

            names[i] = 'Matt'

    return names


def read_family_names(family_file):

    # Load the list of family names
    with open(family_file, 'r') as f:
        names = f.readlines()

    # Remove formating characters and empty spaces
    names = [i.strip() for i in names if i not in '']
    names = [i for i in names if i not in '']

    # Get first and last names
    all_names = [[None, None]]*len(names)
    for i, name in enumerate(names):

        tmp = name.split()

        if len(tmp) == 2:

            first, last = tmp

        elif len(tmp) > 2:
            # If there are multiple part last last names
            first = tmp[0]

            # Combine last name
            last = ''
            for p in tmp[1:]:

                last = last + p + ' '

            # Remove last space
            last = last.strip()

        all_names[i] = [first, last]

    return all_names


def load_contacts(contacts_file):

    # Load data file
    contacts = pd.read_csv(contacts_file)

    # Only pass values which contain birthdays
    inds = [type(i) != float for i in contacts['Birthday']]
    contacts = contacts.loc[inds]

    # Filter out NaN values
    inds = [type(i) == str for i in contacts['Given Name']]
    contacts = contacts.loc[inds]

    return contacts


def load_data(contacts_file, anniversaries_file, family_file):

    # Set up dataframe
    df_bday = {"First Name": [], "Last Name": [], "Birthdate": []}

    # Load raw data
    contacts = load_contacts(contacts_file)
    df_anni = pd.read_csv(anniversaries_file)

    # Load family names
    names = read_family_names(family_file)

    # Correct for Matt and Matthew
    contacts['Given Name'] = correct_matt(contacts['Given Name'].to_list())

    # Filter contacts for family names
    for name in names:

        # Set up indicies
        first_ind = contacts['Given Name'] == name[0]
        last_ind = contacts['Family Name'] == name[1]

        # Get specific person
        person = contacts.loc[first_ind & last_ind]

        # Populate df
        df_bday['First Name'].append(person['Given Name'].to_list()[0])
        df_bday['Last Name'].append(person['Family Name'].to_list()[0])
        df_bday['Birthdate'].append(person['Birthday'].to_list()[0])

    df_bday = pd.DataFrame.from_dict(df_bday)

    return df_bday, df_anni


def make_age_df(df_bday, df_anni, start_year=2010, years_to_extend=10):

    # Initialize output dataframe
    df = {'Subject': [], 'Date': [], 'Age': [], 'Type': []}

    # Add birthdays
    for i in range(len(df_bday)):

        subject = df_bday.iloc[i]['First Name'] + ' ' + df_bday.iloc[i]['Last Name']

        birthdate = datetime.strptime(df_bday.iloc[i]['Birthdate'], '%m/%d/%Y')

        for year in range(start_year, start_year + years_to_extend):

            # Compute new and date
            year_dt = datetime(year, birthdate.month, birthdate.day)
            age = year_dt.year - birthdate.year

            # Append to df
            df['Subject'].append(subject)
            df['Date'].append(year_dt)
            df['Age'].append(age)
            df['Type'].append('Birthday')

    # Add anniversaries
    for i in range(len(df_anni)):

        # Get name and start date
        subject = df_anni.iloc[i]['Name']
        anni_date = datetime.strptime(df_anni.iloc[i]['Date'], '%m/%d/%Y')

        for year in range(start_year, start_year + years_to_extend):

            # Compute new date and Age
            year_dt = datetime(year, anni_date.month, anni_date.day)
            age = year_dt.year - anni_date.year

            # Append to df
            df['Subject'].append(subject)
            df['Date'].append(year_dt)
            df['Age'].append(age)
            df['Type'].append('Anniversary')

    return pd.DataFrame.from_dict(df)
