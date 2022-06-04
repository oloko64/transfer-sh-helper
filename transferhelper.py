#!/usr/bin/env python3

from time import time
from sqlite3 import connect, ProgrammingError
from datetime import datetime
from os import remove, path, makedirs
from os.path import exists, join
from getpass import getuser
from subprocess import run
from multiprocessing import Pool
from argparse import ArgumentParser


# Code developed by OLoKo64
# Thanks for using it :)

# Application version
def version() -> None:
    print('Version: 0.3.8')


# Gets the current unix time
def current_time() -> int:
    return int(time())


# Asks for user confirmation
def ask_confirmation(text: str) -> bool:
    question = input(text).lower()
    if question == 'y' or question == 'yes':
        return True
    else:
        return False


# Drop the entire database
def delete_database() -> None:
    if ask_confirmation('Are you sure you want to DELETE THE DATABASE FILE? (y/N) '):
        remove(path.join(folderPath, databaseFile))


# Convert unix time into readable time
def readable_time(local_time: int) -> str:
    return datetime.utcfromtimestamp(local_time).strftime('%d-%m-%Y')


# Check if the provided unix time is a week or older
def is_out_of_date(previous_date: int) -> bool:
    return (current_time() - previous_date) > 1209600


# Get all the data from the database
def read_data() -> list:
    c.execute("SELECT * FROM transfer_data")

    data = c.fetchall()
    return data


# Get only the one entry from the database
def get_single_entry(entry_id: any) -> list:
    c.execute("SELECT * FROM transfer_data WHERE id = ?", entry_id)

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
            f'Id: {row[0]} -> {row[1]} '
            f'| Link: {row[2]} | Delete Link: {row[3]} '
            f'| Created At: {readable_time(row[4])} '
            f'| Expiration Date: {readable_time(row[4] + 1209600)} '
            f'| Expired: {is_out_of_date(row[4])}')
    print()


# Delete data from the table based on the id provided
def execute_delete(delete_id: str) -> None:
    c.execute("DELETE from transfer_data WHERE id = ?", delete_id)
    conn.commit()


# Delete the file from the cloud
def delete_from_cloud(delete_link: str) -> None:
    run(f'curl -X DELETE {delete_link}', shell=True, capture_output=True)


# Asks the user what is the id to execute the deletion from the database
def delete_data() -> None:
    print_data()
    delete_id = input('Type the id of the entry you want to delete: ')
    cloud_delete = ask_confirmation('Do you also want to delete the file from the cloud? (y/N) ')
    try:
        if cloud_delete:
            delete_from_cloud(get_single_entry(delete_id)[0][3])
        execute_delete(delete_id)
    except ProgrammingError:
        print()
        print('The id provided probably does not exist, exiting...')
        exit(1)


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
    filename_link = file[1].replace(' ', '\ ')
    local_file = (file[0] + file[1]).replace(' ', '\ ')
    output = run(
        f'curl -v --upload-file {local_file} https://transfer.sh/{filename_link}', shell=True,
        capture_output=True)

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


# Create the database if there is not one already created
def check_database() -> None:
    if not exists(join(folderPath, databaseFile)):
        if not exists(folderPath):
            makedirs(folderPath)
        conn = connect(join(folderPath, databaseFile))
        conn.execute('''CREATE TABLE "transfer_data" (
                            "id"	INTEGER,
                            "name"	TEXT,
                            "link"	TEXT,
                            "deleteLink"	TEXT,
                            "unixTime"	INTEGER,
                            PRIMARY KEY("id" AUTOINCREMENT));''')
        conn.commit()


# Prints all the help commands
def print_help() -> None:
    print('List of commands:')
    print(' -h  | --help                => Help on how to use it.')
    print(' -r  | --read                => Read data from database.')
    print(' -u  | --upload              => Upload a file to Transfer.sh.')
    print(' -d  | --delete              => Delete single entry from database.')
    print(' -V  | --version             => Prints the version of the application.')
    print(' -DD | --drop                => Delete the entire database.')
    print()


# Manage all the arguments provided
def arg_parser(args) -> None:
    if any(list(args.__dict__.values())):
        if args.read:
            print_data()
        if args.version:
            version()
        if args.upload:
            send_file(args.upload)
        if args.delete:
            delete_data()
        if args.drop:
            delete_database()
    else:
        print_data()


if __name__ == "__main__":

    # Path to database
    folderPath = '/home/' + getuser() + '/.config/transfer-sh-helper-database'

    # Name of the database file
    databaseFile = 'transfer-sh-helper.db'

    # Check if the database exists
    check_database()

    # Initiate sqlite3 database
    conn = connect(join(folderPath, databaseFile))
    c = conn.cursor()

    # One week in unix time equals 1209600

    try:
        parser = ArgumentParser(description='Transfer.sh Helper')
        parser.add_argument('-u', '--upload', type=str, nargs='+', help='upload a file to transfer.sh')
        parser.add_argument('-r', '--read', action='store_true', help='read data from database')
        parser.add_argument('-d', '--delete', action='store_true', help='delete a single entry from database')
        parser.add_argument('-DD', '--drop', action='store_true', help='delete the entire database file')
        parser.add_argument('-V', '--version', action='store_true', help='prints the version of the application')
        arg_parser(parser.parse_args())
    except KeyboardInterrupt:
        print('\n\nExiting...\n')
        exit(1)
    finally:
        c.close()
        conn.close()
