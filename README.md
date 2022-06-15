# Data Rover

Web front-end for research databases (initially MASS-BD database)

Framework: Python Flask

packages: flask, pandas, pyodbc, os

# Configuration

The configuration is expected in a JSON file config.json in the app directory.

To use this application with MS SQL Server, an appropriate ODBC driver must be 
installed. On Windows, the following usually works:

```
{
    "ODBC_DRIVER": "{SQL Server}",
    "WINDOWS_AUTHENTICATION": true
}
```

and on Unix, if Microsoft's ODBC driver is installed, the following:

```
{
    "ODBC_DRIVER": "{ODBC Driver 17 for SQL Server}",
    "WINDOWS_AUTHENTICATION": false
}
```

# Change Log

## 2/1/2022

Fixed an issue where integer columns were casted to float when there are missing values.

## 1/26/2022

Added Bit filed / Boolean as a possible selection type

## 1/25/2022

Fixed password requirements issue

## 1/18/2022

Enforce password complexity

Fixes bug where security authentication using APIs no longer supported in FLASK SECURITY TOO

Remove index in downloaded csv

## Update 1/14/2022

Switched to flask security too since flask security is no longer maintained

## Update 1/12/2022

Updated requirements.txt to latest version

## Update 1/11/2022

Remove an issue with queries has to start with WHERE

## Update 1/3/2022

Fixed a bug where a non-existent object g.title was used

Upgraded dependencies to address security vulnerabilities

## Update 12/30/2021
Added Configuring options for app title

Fix a bug where non-meaningful columns showing up in filter despite turning config off

Fix a bug where not all relationships are added to the keys dropdown

Fix a bug where outer join is not excuted

## Update 12/29/2021
Refactored into a package in preparation for docker deployment and running on Unix systems.

## Update 12/29/2021
added bootstrap for navigation bar

## Update 12/28/2021
added some updates on docker

## Update 12/23/2021
Removed all commented out code, support user/pass login to the database

## Update 12/22/2021
Removed dependency with the date config (Merged)

## Update 12/21/2021
Updated some bugs in helper function.

## Update 12/7/2021
Reformat admin panel

## Update 12/6/2021
Give an option for odering in config file

Reformate filtering page for ordering input

## Update 11/29/2021

Compile all updates from previous week

Fixed all the bugs regarding table generations.

## Update 11/23/2021

Change the partial variables to a set to support faster searches

Change the variable for ordering to be a set

## Update 11/15/2021
Update the input selection to have be table column specific

Still need to update the html table displaying code to get rid of all the legacy code from first version

The Current version is not a stable release, will not work on displaying table

## Update 11/1/2021
Update to the latest version

Highlight:

Admin and Super user account password management

When admin or super user changes a password, account holders have to change the password on login

Users can now specify which key to join on

join keys will be populated by the following logic:

Foreign to Primary key 

common primary key relations

Schema will be appended to the table name when not using dbo schema

## Update 9/13/2021

Updated to the latest version

Highlight: account management, configuration file added

Next up: Date format error fix and account management hierarchy

## Update 8/4/2021

Completely implemented user saved queries

Implemented user change password

need to implement admin change password and enable/disable account

## Update 8/3/2021

Saved query access completed, need to work on redirecting to corresponding query

## Update 8/2/2021

Query Saving Implemented

Need to consider retrieving model and other displaying options.

## Update 7/30/2021

Fixed Some Bugs

## Update 7/29/2021

Updated endpoints for logout

## Update 7/28/2021

Added admin role which can register users

## Update 7/27/2021

Created Logins and basic authentication

Need to explore admin roles and email configurations.

## Update 7/26/2021

Created App Factory

Supports both partial and exact match search

created sql dabase for user information

## Update 7/21/2021

Added multiple selection on table selection

Allowed user to choose join type between tables

Enforced singular appearence of tables

## Update 7/20/2021

Added better Navigaions and input fields

Looking at dynamic table selections.

## Update 7/13/2021

Filtering option implemented, 

further testing may be needed for edge cases

Next Step is to explore adding filtering options on the table previewing page

## Update 7/12/2021

Multiple slect implemented with bootstrap multiselect

exploring sql generating methods to implement the filter

## Update 7/9/2021

Working on multiple select on the input page,

Ran into bug regarding the use of dropdown checkbox

Will explore more next week.

## Update 7/2/2021:

Added individual column search

Looking into customization

## Update 6/29/2021: 

Basic framework established. 

Table display and sample_id search.

Preview display using jquery datatable

Known issue: slow load time for large data

Next goal: Establish individual Search functions and talk more about table joining and column dropping.