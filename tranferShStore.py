import time
import sqlite3
from datetime import datetime
import sys

conn = sqlite3.connect('database/transferSh.db')
c = conn.cursor()


def currentTime():
    return int(time.time())

def readableTime(time):
    return datetime.utcfromtimestamp(time).strftime('%d-%m-%Y')

def isOutOfDate(previousDate):
    # One week in unix time equals 1209600
    return (currentTime() - previousDate) > 1209600

def readData():
    c.execute("SELECT * from transferData")

    data = c.fetchall()
    return data

def dataEntry(data):
    c.execute(f"INSERT INTO transferData(name, link, deleteLink, unixTime) VALUES(?, ?, ?, ?)", (data['name'], data['link'], data['deleteLink'], data['unixTime']))

    conn.commit()
    c.close()
    conn.close()

def printData():
    print()
    for row in enumerate(readData()):
        print(f'Id: {list(row[1])[0]} - Name: {list(row[1])[1]} | Link: {list(row[1])[2]} | Delete Link: {list(row[1])[3]} | Created Time: {readableTime(list(row[1])[4])} | Expired Time: {readableTime(list(row[1])[4] + 1209600)} | Expired: {isOutOfDate(list(row[1])[4])}')
    print()

def ExecuteDelete(id):
    c.execute("DELETE from transferData WHERE id = ?", id)

    conn.commit()
    c.close()
    conn.close()

def deleteData():
    printData()
    id = input('Type the id of the entry you want to delete: ')
    ExecuteDelete(id)

def insertData():
    name = input('Type the name of the entry: ')
    link = input('Type the link of the entry: ')
    deleteLink = input('Type the delete link of the entry: ')

    localData = {
        "name": name,
        "link": link,
        "deleteLink": deleteLink,
        "unixTime": currentTime()
    }

    dataEntry(localData)

def printHelp():
    print('List of commands:')
    print(' -h | --help                => Help on how to use it')
    print(' -r | empty                 => Read data from database')
    print(' -i | --insert              => Insert data into database')
    print(' -d | --delete              => Delete data from database')
    print()

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



if __name__ == "__main__":
    argParser(sys.argv[1:])
