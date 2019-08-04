import os
from utils import load_data, make_age_df, write_to_calendar


def main():

    # Set up data paths
    cwd = os.getcwd()
    contacts_file = os.path.join(cwd, 'Data', 'contacts.csv')
    anniversaries_file = os.path.join(cwd, 'Data', 'anniversaries.csv')
    address_file = os.path.join(cwd, 'Data', 'names_addresses.txt')

    # CalendarId
    # service.calendarList().list().execute()  # Run line to get calendar list
    calendarId = 'la6vnilmh89u8c85s4rgqi8c40@group.calendar.google.com'

    # Load data
    df_bday, df_anni = load_data(contacts_file, anniversaries_file, address_file)

    # print(df_bday)
    # print(df_anni)

    # Format for upload
    df = make_age_df(df_bday, df_anni, start_year=2015, years_to_extend=20)
    print(df.to_string())

    # Create Google calendar
    write_to_calendar(df, calendarId)


if __name__ == "__main__":

    main()
