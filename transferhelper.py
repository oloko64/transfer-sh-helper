#!/usr/bin/env python3

from time import time
from sqlite3 import connect
from datetime import datetime
from sys import argv
from os import remove, path, makedirs
from os.path import exists, join
from getpass import getuser
from subprocess import run
from multiprocessing import Pool

# Code developed by OLoKo64
# Thanks for using it :)

# Path to database
folderPath = '/home/' + getuser() + '/.config/transfer-sh-helper-database'

# Name of the database file
databaseFile = 'transfer-sh-helper.db'

# Create the database if there is not one already created
if not exists(join(folderPath, databaseFile)):
    if not exists(folderPath):
        makedirs(folderPath)
    fc = open(join(folderPath, databaseFile), 'x')
    fc.close()
    conn = connect(join(folderPath, databaseFile))
    conn.execute('''CREATE TABLE "transfer_data" (
                    "id"	INTEGER,
                    "name"	TEXT,
                    "link"	TEXT,
                    "deleteLink"	TEXT,
                    "unixTime"	INTEGER,
                    PRIMARY KEY("id" AUTOINCREMENT));''')
    conn.close()

# Initiate sqlite3 database
conn = connect(join(folderPath, databaseFile))
c = conn.cursor()

# One week in unix time equals 1209600
unixWeek = 1209600


# Gets the current unix time
def current_time() -> int:
    return int(time())


# Asks for user confirmation
def ask_confirmation(text: str) -> bool:
    question = input(f'Are you sure you want to {text}? (y/N) ')
    if (question == 'y' or question == 'Y' or question == 'yes'):
        return True
    else:
        return False


# Drop the entire database
def delete_database() -> None:
    if (ask_confirmation('DELETE THE DATABASE FILE')):
        remove(path.join(folderPath, databaseFile))


# Convert unix time into readable time
def readable_time(local_time: int) -> str:
    return datetime.utcfromtimestamp(local_time).strftime('%d-%m-%Y')


# Check if the provided unix time is a week or more older
def is_out_of_date(previous_date: int) -> bool:
    return (current_time() - previous_date) > unixWeek


# Get all the data from the database
def read_data() -> list:
    c.execute("SELECT * from transfer_data")

    data = c.fetchall()
    return data


# Insert provided data into database
def data_entry(data: dict) -> None:
    c.execute(f"INSERT INTO transfer_data(name, link, deleteLink, unixTime) VALUES(?, ?, ?, ?)",
              (data['name'], data['link'], data['deleteLink'], data['unixTime']))

    conn.commit()


# Prints the data to the console
def print_data() -> None:
    print()
    for row in read_data():
        print(
            f'Id: {row[0]} -> {row[1]} | Link: {row[2]} | Delete Link: {row[3]} | Created Time: {readable_time(row[4])} | Expired Time: {readable_time(row[4] + unixWeek)} | Expired: {is_out_of_date(row[4])}')
    print()


# Delete data from the table based on the id provided
def execute_delete(delete_id: str) -> None:
    c.execute("DELETE from transfer_data WHERE id = ?", delete_id)
    conn.commit()


# Asks the user what is the id to execute the deletion from the database
def delete_data() -> None:
    print_data()
    delete_id = input('Type the id of the entry you want to delete: ')
    execute_delete(delete_id)


# Retrieves the delete link from the output of the curl command
def get_delete_link(link: str) -> str:
    lines = link.split('\n')
    for line in lines:
        if 'x-url-delete:' in line:
            return line.split(' ')[2].replace('\r', '')


# Split the path to get the filename and the path
def treat_path(file_path: list) -> list:
    files = []
    for file in file_path:
        combined_path = file.split('/')
        filename = combined_path[-1]
        only_path = file.replace(filename, '')
        files.append([only_path, filename])
    return files


# Check if the file exists
def check_file_exists(file_path: list) -> None:
    for file in file_path:
        if not exists(file):
            print(f'The file {file} does not exist')
            exit(1)


def upload_file(file: list) -> dict:
    output = run(
        f'curl -v --upload-file {file[0] + file[1]} https://transfer.sh/{file[1]}', shell=True, capture_output=True)

    return {
        "name": file[2],
        "link": output.stdout.decode("utf-8"),
        "deleteLink": get_delete_link(output.stderr.decode("utf-8")),
        "unixTime": current_time()
    }


# Sends the file to transfer.sh and add it to the database
def send_file(path_file: list) -> None:
    check_file_exists(path_file)
    files = treat_path(path_file)
    for index, title in enumerate([input(f'Add a title for the {file[1]} file: ') or 'No Title' for file in files]):
        files[index].append(title)
    print()
    print('Uploading file(s)...')
    with Pool() as pool:
        entries = pool.map(upload_file, files)

    for entry in entries:
        data_entry(entry)
    print_data()


# Prints all the help commands
def print_help() -> None:
    print('List of commands:')
    print(' -h  | --help                => Help on how to use it.')
    print(' -r  | --read                => Read data from database.')
    print(' -u  | --upload              => Upload a file to Transfer.sh.')
    print(' -d  | --delete              => Delete data from database.')
    print(' -V  | --version             => Prints the version of the application.')
    print(' -DD | --drop                => Delete the entire database.')
    print()


# Manage all the arguments provided
def arg_parser(args: list) -> None:
    if len(args):
        if args[0] == '-u' or args[0] == '--upload':
            send_file(args[1:])
        elif args[0] == '-r' or args[0] == '--read':
            print_data()
        elif args[0] == '-d' or args[0] == '--delete':
            delete_data()
        elif args[0] == '-DD' or args[0] == '--drop':
            delete_database()
        elif args[0] == '-V' or args[0] == '--version':
            print('Version -> 0.3.6')
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
        exit(1)
    finally:
        c.close()
        conn.close()
