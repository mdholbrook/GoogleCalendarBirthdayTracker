import os
from utils import load_data, make_age_df


def main():

    # Set up data paths
    cwd = os.getcwd()
    contacts_file = os.path.join(cwd, 'Data', 'contacts.csv')
    anniversaries_file = os.path.join(cwd, 'Data', 'king_anniversaries.csv')
    family_file = os.path.join(cwd, 'Data', 'family_names.txt')

    # Load data
    df_bday, df_anni = load_data(contacts_file, anniversaries_file, family_file)

    print(df_bday)
    print(df_anni)

    # Format for upload
    df = make_age_df(df_bday, df_anni, start_year=2019, years_to_extend=10)
    # print(df.head(df.shape[0]//2))

    # Create Google calendar



if __name__ == "__main__":

    main()
