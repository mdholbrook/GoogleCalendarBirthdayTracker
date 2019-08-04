# Google Calendar Birthday Tracker

This tool creates Google Calendar events to keep track of birthdays and anniversaries. While creating such events is easy using Google contacts information or repeating calendar events, Google does not offer native support for age tracking. 

This code adds annual events given in the format: `mdholbrook (25)` and can be used for your entire Google address book.

## Installation
Set up a connection your your Google calendar using the `quickstart.py` script and the instructions contained in Google's [quickstart guide for Python](https://developers.google.com/calendar/quickstart/python). The `credientials.json` file you downloaded is expected to be in `\Data\`, but this path can be modified in the code.

Clone the project and Install dependent packages using the following commands. I highly recommend using a virtual environment.
```sh
$ git clone https://github.com/mdholbrook/GoogleCalendarBirthdayTracker.git
$ cd GoogleCalendarBirthdayTracker
$ pip install -r requirements.txt
```

## Setup
This section will help you set up the necessary data files. 

**Headers shown in the text files must be included as shown in the tables, separated by commas.**

For the current revision of this project, all of the following files and fields must be populated. Files can be left blank (aside from headers).
#### Birthday information
Add or update your Google contacts with birthdays information. Since your contacts are somewhat hidden in current versions of Gmail here a [link to your Google contacts](https://contacts.google.com/?hl=en). For ages to correctly show up be sure to **add the birth year**.

Once updated export your contacts as a `Google CSV` and save to `Data\contacts.csv` within the project directory.

#### Name and addresses
Save names and adresses in a text file called `\Data\names_addresses.txt`. Use the following fields:

|Name|Address|City|State|Country|
| --- | ------ | --- | ---- | ----- |
|John Smith|16070 E Dartmouth Ave| Aurora| CO 80013| USA|
|Jill Bowden| 140 N Prospect St| Granville| OH 43023| USA|

Separate each field with **commas** (eg., John Smith, 16979 E Dartmouth Ave, Aurora, CO 80013, USA). Place each person on a separate line.

Only names included in this file will be used to create events. This works as a filter for your Google contacts.

#### Anniversaries

Anniversary events can be created by setting up another data file: `\Data\anniversaries.txt`. These events can have any name you with so long as it does not contain commas which will mess up the parsing. 

|Name|Date|
| ---|---|
|David & Marge|12/6/2010|


## Usage
**Danger: DO NOT USE THIS CODE ON YOUR MAIN CALENDAR.** It shouldn't harm that calendar if you run it, but the potential is there to modify your events. Instead make a new calendar and modify the `calendarId` to match that calendar. This also makes these events easier to share. 

Step:
1. Modify the `main.py` code to include the Id for the calendar.
2. Add the start year.
3. Add the number of years to make events for.

The program is run using:
```sh
$ python main.py
```

The code will clear events already created using this script before adding new ones; duplicate events shouldn't be a problem.
