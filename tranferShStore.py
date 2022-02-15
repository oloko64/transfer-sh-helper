import time
import sqlite3
from datetime import datetime
import sys

# Initiate sqlite3 database
conn = sqlite3.connect('database/transferSh.db')
c = conn.cursor()

# One week in unix time equals 1209600
unixWeek = 1209600

# Gets the current unix time
def currentTime():
    return int(time.time())

# Convert unix time into readable time
def readableTime(time):
    return datetime.utcfromtimestamp(time).strftime('%d-%m-%Y')

# Check if the provided unix time is a week or more older
def isOutOfDate(previousDate):
    return (currentTime() - previousDate) > unixWeek

# Get all the data from the database
def readData():
    c.execute("SELECT * from transferData")

    data = c.fetchall()
    return data

# Insert provided data into database
def dataEntry(data):
    c.execute(f"INSERT INTO transferData(name, link, deleteLink, unixTime) VALUES(?, ?, ?, ?)", (data['name'], data['link'], data['deleteLink'], data['unixTime']))
    
    conn.commit()
    c.close()
    conn.close()

# Prints the data to the console
def printData():
    print()
    for row in readData():
        print(f'Id: {list(row[1])[0]} - Name: {list(row[1])[1]} | Link: {list(row[1])[2]} | Delete Link: {list(row[1])[3]} | Created Time: {readableTime(list(row[1])[4])} | Expired Time: {readableTime(list(row[1])[4] + unixWeek)} | Expired: {isOutOfDate(list(row[1])[4])}')
    print()

# Delete data from the table based on the id provided
def executeDelete(id):
    c.execute("DELETE from transferData WHERE id = ?", id)

    conn.commit()
    c.close()
    conn.close()

# Asks the user what is the id to execute the deletion from the database
def deleteData():
    printData()
    id = input('Type the id of the entry you want to delete: ')
    executeDelete(id)

# Asks the user for the information to be added to the database
def insertData():
    name = input('(1/3) - Type the name of the entry: ')
    link = input('(2/3) - Type the link of the entry: ')
    deleteLink = input('(3/3) - Type the delete link of the entry: ')

    localData = {
        "name": name,
        "link": link,
        "deleteLink": deleteLink,
        "unixTime": currentTime()
    }

    dataEntry(localData)

# Prints all the help commands
def printHelp():
    print('List of commands:')
    print(' -h | --help                => Help on how to use it')
    print(' -r | empty                 => Read data from database')
    print(' -i | --insert              => Insert data into database')
    print(' -d | --delete              => Delete data from database')
    print()

# Manage all the arguments provided
def argParser(args):
    if len(args):
        for arg in args:
            if (arg == '-r' or arg == 'empty'):
                printData()
            elif (arg == '-i' or arg == '--insert'):
                insertData()
            elif (arg == '-d' or arg == '--delete'):
                deleteData()
            elif (arg == '-h' or arg == '--help'):
                print('\nThis app lets you manage your transfer.sh links, by adding the links when you created them you can know if they are already expired\n')
                printHelp()
            else:
                printHelp()
    else:
        printData()


# Main code execution
if __name__ == "__main__":
    argParser(sys.argv[1:])
