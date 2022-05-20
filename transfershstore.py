#!/usr/bin/env python3

from time import time
from sqlite3 import connect
from datetime import datetime
from sys import argv
from os import remove, path, makedirs
from os.path import exists
from getpass import getuser
from subprocess import run

# Code developed by OLoKo64
# Thanks for using it :)

# Path to database
folderPath = '/home/' + getuser() + '/.config/transfer-sh-database'

# Name of the database file
databaseFile = 'transfer-sh.db'

# Create the database if there is not one already created
if (not exists(path.join(folderPath, databaseFile))):
    if not path.exists(folderPath):
        makedirs(folderPath)
    fc = open(path.join(folderPath, databaseFile), 'x')
    fc.close()
    conn = connect(path.join(folderPath, databaseFile))
    conn.execute('''CREATE TABLE "transfer_data" (
                    "id"	INTEGER,
                    "name"	TEXT,
                    "link"	TEXT,
                    "deleteLink"	TEXT,
                    "unixTime"	INTEGER,
                    PRIMARY KEY("id" AUTOINCREMENT));''')
    conn.close()

# Initiate sqlite3 database
conn = connect(path.join(folderPath, databaseFile))
c = conn.cursor()

# One week in unix time equals 1209600
unixWeek = 1209600


# Gets the current unix time
def current_time():
    return int(time())


# Asks for user confirmation
def ask_confirmation(text):
    question = input(f'Are you sure you want to {text}? (y/N) ')
    if (question == 'y' or question == 'Y' or question == 'yes'):
        return True
    else:
        return False


# Drop the entire database
def delete_database():
    if (ask_confirmation('DELETE THE DATABASE FILE')):
        remove(path.join(folderPath, databaseFile))


# Convert unix time into readable time
def readable_time(time):
    return datetime.utcfromtimestamp(time).strftime('%d-%m-%Y')


# Check if the provided unix time is a week or more older
def is_out_of_date(previous_date):
    return (current_time() - previous_date) > unixWeek


# Get all the data from the database
def read_data():
    c.execute("SELECT * from transfer_data")

    data = c.fetchall()
    return data


# Insert provided data into database
def data_entry(data):
    c.execute(f"INSERT INTO transfer_data(name, link, deleteLink, unixTime) VALUES(?, ?, ?, ?)",
              (data['name'], data['link'], data['deleteLink'], data['unixTime']))

    conn.commit()


# Prints the data to the console
def print_data():
    print()
    for row in read_data():
        print(
            f'Id: {row[0]} -> {row[1]} | Link: {row[2]} | Delete Link: {row[3]} | Created Time: {readable_time(row[4])} | Expired Time: {readable_time(row[4] + unixWeek)} | Expired: {is_out_of_date(row[4])}')
    print()


# Delete data from the table based on the id provided
def execute_delete(delete_id):
    c.execute("DELETE from transfer_data WHERE id = ?", delete_id)
    conn.commit()


# Asks the user what is the id to execute the deletion from the database
def delete_data():
    print_data()
    delete_id = input('Type the id of the entry you want to delete: ')
    execute_delete(delete_id)


# Retrieves the delete link from the output of the curl command
def get_delete_link(link):
    lines = link.split('\n')
    for line in lines:
        if 'x-url-delete:' in line:
            return line.split(' ')[2].replace('\r', '')


# Sends the file to transfer.sh and add it to the database
def send_file(filename):
    title = input('Add a simple title for the file: ') or 'No title'
    print('Uploading file...')
    output = run(f'curl -v --upload-file {filename} https://transfer.sh/{filename}', shell=True, capture_output=True)

    local_data = {
        "name": title,
        "link": output.stdout.decode("utf-8"),
        "deleteLink": get_delete_link(output.stderr.decode("utf-8")),
        "unixTime": current_time()
    }

    data_entry(local_data)
    print_data()


# Prints all the help commands
def print_help():
    print('List of commands:')
    print(' -h  | --help                => Help on how to use it.')
    print(' -r  | --read                => Read data from database.')
    print(' -u  | --upload              => Upload a file to Transfer.sh.')
    print(' -d  | --delete              => Delete data from database.')
    print(' -DD | --drop                => Delete the entire database.')
    print()


# Manage all the arguments provided
def arg_parser(args):
    if len(args):
        if args[0] == '-u' or args[0] == '--upload':
            send_file(args[1])
        elif args[0] == '-r' or args[0] == '--read':
            print_data()
        elif args[0] == '-d' or args[0] == '--delete':
            delete_data()
        elif args[0] == '-DD' or args[0] == '--drop':
            delete_database()
        elif args[0] == '-h' or args[0] == '--help':
            print(
                '\nThis app lets you manage your transfer.sh links, by adding the links when you created them you can '
                'know if they are already expired.\n')
            print_help()
    else:
        print_data()


# Main code execution
if __name__ == "__main__":
    try:
        arg_parser(argv[1:])
    except KeyboardInterrupt:
        print('\n\nExiting...\n')
        exit()
    finally:
        c.close()
        conn.close()
