import os
import pandas as pd
import numpy as np
from datetime import datetime
import pickle
from googleapiclient.discovery import build


def correct_matt(names):

    for i in range(len(names)):

        if 'Matthew' in names[i]:

            names[i] = 'Matt'

    return names


def clean_family_names(names):

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


def load_addresses(address_file):

    # Read addresses
    addresses = pd.read_csv(address_file)

    # Concatenate the address
    concat_addresses = {'Name': [], 'Address': []}
    for i in range(addresses.shape[0]):

        concat_addresses['Name'].append(addresses.iloc[i]['Name'])

        concat_addresses['Address'].append(addresses.iloc[i]['Address'].lstrip() + ', '
                                           + addresses.iloc[i]['City'] + ', '
                                           + addresses.iloc[i]['State'] + ', '
                                           + addresses.iloc[i]['Country'])

    return pd.DataFrame.from_dict(concat_addresses)


def address_to_anniversary(df_address, df_anni):

    # Add an address column to df_anni
    df_anni = pd.concat((df_anni, pd.DataFrame.from_dict({'Address': [None]*df_anni.shape[0]})), axis=1)

    # Get the list of unique addreses
    addresses = df_address['Address'].unique()

    for address in addresses:

        names = df_address.loc[df_address['Address'] == address, 'Name'].to_list()

        match = np.array([0] * len(df_anni))
        for name in names:
            fn = name.split()
            match = match + np.array([fn[0] in i for i in df_anni['Name']])

        if match.max() == 1:  # Pappa and Nanna
            df_anni.loc[df_anni['Name'] == 'Pappa & Nanna', 'Address'] = address

        else:

            # Find maximum indicies
            inds = match == 2

            # Update the anniversary df
            df_anni.loc[inds, 'Address'] = address

    return df_anni


def load_data(contacts_file, anniversaries_file, address_file):

    # Set up dataframe
    df_bday = {"First Name": [], "Last Name": [], "Birthdate": [], "Address": []}

    # Load raw data
    contacts = load_contacts(contacts_file)
    df_anni = pd.read_csv(anniversaries_file)

    # Load addresses
    addresses = load_addresses(address_file)

    # Append addresses to anniversaries
    df_anni = address_to_anniversary(addresses, df_anni)

    # Correct for Matt and Matthew
    contacts['Given Name'] = correct_matt(contacts['Given Name'].to_list())

    # Clean up names
    addresses['Name'] = clean_family_names(addresses['Name'].to_list())

    # Filter contacts for family names
    for i, name in enumerate(addresses['Name']):

        # Set up indicies
        first_ind = contacts['Given Name'] == name[0]
        last_ind = contacts['Family Name'] == name[1]

        # Get specific person
        person = contacts.loc[first_ind & last_ind]

        # Populate df
        df_bday['First Name'].append(person['Given Name'].to_list()[0])
        df_bday['Last Name'].append(person['Family Name'].to_list()[0])
        df_bday['Birthdate'].append(person['Birthday'].to_list()[0])
        df_bday['Address'].append(addresses.iloc[i]['Address'])

    df_bday = pd.DataFrame.from_dict(df_bday)

    return df_bday, df_anni


def make_age_df(df_bday, df_anni, start_year=2010, years_to_extend=10):

    # Initialize output dataframe
    df = {'Subject': [], 'Title': [], 'Date': [], 'Age': [], 'Type': [], 'Address': []}

    # Add birthdays
    for i in range(len(df_bday)):

        subject = df_bday.iloc[i]['First Name'] + ' ' + df_bday.iloc[i]['Last Name']

        birthdate = datetime.strptime(df_bday.iloc[i]['Birthdate'], '%m/%d/%Y')

        for year in range(start_year, start_year + years_to_extend):

            # Compute new and date
            year_dt = datetime(year, birthdate.month, birthdate.day)
            age = year_dt.year - birthdate.year

            # Create new event title
            title = '{} ({})'.format(subject, age)

            # Append to df
            df['Subject'].append(subject)
            df['Title'].append(title)
            df['Date'].append(year_dt)
            df['Age'].append(age)
            df['Type'].append('Birthday')
            df['Address'].append(df_bday.iloc[i]['Address'])

    # Add anniversaries
    for i in range(len(df_anni)):

        # Get name and start date
        subject = df_anni.iloc[i]['Name']
        anni_date = datetime.strptime(df_anni.iloc[i]['Date'], '%m/%d/%Y')

        for year in range(start_year, start_year + years_to_extend):

            # Compute new date and Age
            year_dt = datetime(year, anni_date.month, anni_date.day)
            age = year_dt.year - anni_date.year

            # Create new event title
            title = '{} ({})'.format(subject, age)

            # Append to df
            df['Subject'].append(subject)
            df['Title'].append(title)
            df['Date'].append(year_dt)
            df['Age'].append(age)
            df['Type'].append('Anniversary')
            df['Address'].append(df_anni.iloc[i]['Address'])

    return pd.DataFrame.from_dict(df)


def write_to_calendar(df, calendarId):

    # Load security token
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)

    # Create calendar service
    service = build('calendar', 'v3', credentials=creds)

    # Remove existing events
    delete_events(service, calendarId)

    # Add new events
    num_events = df.shape[0]
    n = 0
    for i in range(num_events):

        flag = True
        n += 1
        while flag:
            id = 'b{:09d}'.format(n)

            event = {
                  'summary': df.iloc[i]['Title'],
                  'id': id,
                  'location': df.iloc[i]['Address'],
                  'description': '',
                  'start': {
                    'date': datetime.strftime(df.iloc[i]['Date'], '%Y-%m-%d'),
                    'timeZone': 'America/Denver'
                  },
                    'end': {
                    'date': datetime.strftime(df.iloc[i]['Date'], '%Y-%m-%d'),
                    'timeZone': 'America/Denver'
                  },
                  'reminders': {
                    'useDefault': True,
                  },
                }

            try:
                event = service.events().insert(calendarId=calendarId, body=event).execute()
                flag = False
            except:
                n += 1
        print('Event created: %s' % (event.get('id')))


def delete_events(service, calendarId):

    # Get the list of events - some may be on other pages
    ids = []
    page_token = None
    while True:
        events = service.events().list(calendarId=calendarId, pageToken=page_token).execute()
        for event in events['items']:
            ids.append(event['id'])
        page_token = events.get('nextPageToken')
        if not page_token:
            break

    # Determine if event was automatically generated
    true_ids = []
    for i, id in enumerate(ids):

        if id[0] == 'b':

            if id[1:].isnumeric():

                true_ids.append(id)

    # Delete events with ids
    if len(true_ids) > 0:
        print('Removing events:')
        for id in true_ids:
            res = service.events().delete(calendarId=calendarId, eventId=id, sendUpdates='none').execute()
            print('\t{}'.format(id))
