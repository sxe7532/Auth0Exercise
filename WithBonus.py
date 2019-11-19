#!/usr/bin/python
#IT Systems Engineer - Technical Exercise

import csv
from datetime import datetime, timedelta
from prettytable import PrettyTable
from flask import Flask
import os

app = Flask(__name__)

directory = []
inventory = []
auditUserList = []
auditCompList = []

@app.route('/checkassets', methods=['POST'])

#Slack Command
def checkassets():
    getDirectory()
    getInventory()
    getUnregistered()
    auditCheckIns()

    t1 = PrettyTable(['No.', 'Name', 'Email'])
    t2 = PrettyTable(['No.','Serial Number', 'User', 'Time Offline (Days)'])

    n = 0
    for user in auditUserList:
        n += 1
        t1.add_row([n, user["Name"], user["Email"]])

    n = 0
    for computer in auditCompList:
        n += 1
        t2.add_row([n, computer["Serial Number"], computer["User"], computer["Time offline"]])

    message = str(t1) + "\n\n" + str(t2)

    return message

#Get List of All Employees
def getDirectory():
    file = 'Data/directory.csv'
    with open(file) as f:
        reader = csv.DictReader(f, delimiter=',')
        for row in reader:
            employee = {
                "Name": row['first_name'] + " " + row['last_name'],
                "Email": row['email']
            }

            directory.append(employee)

#Get List of All Computers registered on Jamf
def getInventory():
    file = 'Data/inventory.csv'
    with open(file) as f:
        reader = csv.DictReader(f, delimiter=',')
        for row in reader:
            computer = {
                "Serial Number": row['Serial Number'],
                "User": row['Name'],
                "Last Check-in": datetime.strptime(row['Last Check-in'], "%m/%d/%y %H:%M")
            }

            inventory.append(computer)

#Find computers not registered on Jamf
def getUnregistered():
    all_employees = [employee['Name'] for employee in directory]
    registered = [employee['User'] for employee in inventory]
    unregistered = list(set(all_employees) - set(registered))

    for employee in directory:
        if employee["Name"] in unregistered:
            unregisteredList = {
                "Name": employee["Name"],
                "Email": employee["Email"]
            }

            auditUserList.append(unregisteredList)

#Find computers that have not checked in to Jamf in 3+ weeks
def auditCheckIns():
    old_dt = datetime.today() - timedelta(weeks=3)

    for computer in inventory:
        if computer['Last Check-in'] < old_dt:
            days_away = datetime.today() - computer['Last Check-in']

            offlineList = {
                "Serial Number": computer['Serial Number'],
                "User": computer["User"],
                "Time offline": days_away.days
            }

            auditCompList.append(offlineList)


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
