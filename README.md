# Note: this repository is no longer being maintained.

# Journal Parser

Current Version: 2.0
Date: 3/9/2020
Creator: Jeffrey Lu

For queries, assistance, or bug reporting, please email: j.lu@perkinseastman.com

## Introduction

Journal Parser is a tool that collects journal files from a chosen directory, and allows you to query individual journal files for a "human-readable" output. Both basic information such as the user's Revit version and session time, and more advanced information such as usage statistics can be queried.

## Prerequisites

Journal Parser and Journal Collector have been tested for use in Python 3.7.4 and a Windows 10 Enterprise environment. If you do not have Python 3.7.4, [download the latest version here](https://www.python.org/downloads/release/python-382/).

# Usage
## Local Connections
### Open Local Directory

 1. Select `Open Local Directory` to go directly to the Revit journal
    directory for the current user. This is equivalent to navigating to
    `%localappdata%\autodesk\revit\`
 2. Open the folder corresponding to the Revit Version you wish to
    investigate.
 3. Sort the list of files by Date Modified to see the most recent
    journals at the top. Note that only `.txt` files are displayed.
 4. Select a journal to investigate and click `Open`. If it is a valid
    journal file, it will be automatically parsed.
> Note that journals with large file sizes will take longer to open. Be patient.

### Open Last Journal Directory
Once a journal file has been queried, you may use the `Open Last Journal Directory` function to quickly access the last visited folder.

## Remote Connections
### New Remote Connection

 1. Select the `New Remote Connection` function to initiate a new remote
    connection.
 2. In the login window, enter the user's computer ID and login ID.

>Note: use the PE PC Manager tool to quickly retrieve computer IDs. 
>Contact Cesar Rosales (c.rosales@perkinseastman.com) for more information.
3. Open the folder corresponding to the Revit Version you wish to
    investigate.
4. Sort the list of files by Date Modified to see the most recent
    journals at the top. Note that only `.txt` files are displayed.
5. Select a journal to investigate and click `Open`. If it is a valid
    journal file, it will be automatically parsed.
    
### Last Remote Connection
Once a remote connection has been established, you may use the `Last Remote Connection` function to quickly access the last visited remote connection.

### Remote Connections Log
The `Remote Connections Log` function will display all the previously made remote connections for quick access. Select one from the list and click `Open Selected Connection` to re-open it. Choose `Clear Logs` to empty the list.

## Archive of Journal Files
Journal Parser automatically makes a copy of *any* accessed journals - both local and remote - for quick access. These are all saved in `C:\Logs\journals`. Use the `Open Local Copy of Journal` function to access the archive folder.

# Features
To be completed.# Journal Parser

Current Version: 2.0
Date: 8/20/2019
Creator: Jeffrey Lu

For queries, assistance, or bug reporting, please email: j.lu@perkinseastman.com

## Introduction

Journal Parser is a tool that collects journal files from a chosen directory, and allows you to query individual journal files for a "human-readable" output. Both basic information such as the user's Revit version and session time, and more advanced information such as usage statistics can be queried.

## Prerequisites

Journal Parser and Journal Collector have been tested for use in Python 3.7.4 and a Windows 10 Enterprise environment. If you do not have Python 3.7.4, [download the latest version here](https://www.python.org/downloads/release/python-382/).

# Usage
## Local Connections
### Open Local Directory

 1. Select `Open Local Directory` to go directly to the Revit journal
    directory for the current user. This is equivalent to navigating to
    `%localappdata%\autodesk\revit\`
 2. Open the folder corresponding to the Revit Version you wish to
    investigate.
 3. Sort the list of files by Date Modified to see the most recent
    journals at the top. Note that only `.txt` files are displayed.
 4. Select a journal to investigate and click `Open`. If it is a valid
    journal file, it will be automatically parsed.
> Note that journals with large file sizes will take longer to open. Be patient.

### Open Last Journal Directory
Once a journal file has been queried, you may use the `Open Last Journal Directory` function to quickly access the last visited folder.

## Remote Connections
### New Remote Connection

 1. Select the `New Remote Connection` function to initiate a new remote
    connection.
 2. In the login window, enter the user's computer ID and login ID.

>Note: use the PE PC Manager tool to quickly retrieve computer IDs. 
>Contact Cesar Rosales (c.rosales@perkinseastman.com) for more information.
3. Open the folder corresponding to the Revit Version you wish to
    investigate.
4. Sort the list of files by Date Modified to see the most recent
    journals at the top. Note that only `.txt` files are displayed.
5. Select a journal to investigate and click `Open`. If it is a valid
    journal file, it will be automatically parsed.
    
### Last Remote Connection
Once a remote connection has been established, you may use the `Last Remote Connection` function to quickly access the last visited remote connection.

### Remote Connections Log
The `Remote Connections Log` function will display all the previously made remote connections for quick access. Select one from the list and click `Open Selected Connection` to re-open it. Choose `Clear Logs` to empty the list.

## Archive of Journal Files
Journal Parser automatically makes a copy of *any* accessed journals - both local and remote - for quick access. These are all saved in `C:\Logs\journals`. Use the `Open Local Copy of Journal` function to access the archive folder.

# Features
To be completed.
<!--stackedit_data:
eyJoaXN0b3J5IjpbODQzMTc2NjQsLTk1ODU0NzhdfQ==
-->
