# Data Rover
# Copyright (C) 2022  Vitalant
# Developed by Vincent Chiang

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import pyodbc
import pandas as pd
import numpy as np

# cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER='+server_url+';DATABASE='+database+';Trusted_Connection=yes')

# output = pd.read_sql('SELECT   \
#     f.name AS foreign_key_name\
#     ,OBJECT_NAME(f.parent_object_id) AS table_name  \
#     ,COL_NAME(fc.parent_object_id, fc.parent_column_id) AS constraint_column_name  \
#     ,OBJECT_NAME (f.referenced_object_id) AS referenced_object  \
#     ,COL_NAME(fc.referenced_object_id, fc.referenced_column_id) AS referenced_column_name  \
#     FROM sys.foreign_keys AS f  \
#     INNER JOIN sys.foreign_key_columns AS fc   \
#     ON f.object_id = fc.constraint_object_id', cnxn) 

# names = pd.read_sql("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES", cnxn)["TABLE_NAME"]

def key_helper(cnxn):
    # asPrimary = relations[relations['table_name'].isin(existings) & (relations["referenced_object"] == target)]
    # asForeign = relations[(relations["table_name"] == target) & relations['referenced_object'].isin(existings)]
    # df = pd.concat([asPrimary, asForeign])

    r1 = pd.read_sql('SELECT   \
    OBJECT_NAME(f.parent_object_id) AS table_name  \
    ,COL_NAME(fc.parent_object_id, fc.parent_column_id) AS constraint_column_name  \
    ,OBJECT_NAME (f.referenced_object_id) AS referenced_object  \
    ,COL_NAME(fc.referenced_object_id, fc.referenced_column_id) AS referenced_column_name  \
    FROM sys.foreign_keys AS f  \
    INNER JOIN sys.foreign_key_columns AS fc   \
    ON f.object_id = fc.constraint_object_id', cnxn) 


    r2 = pd.read_sql('WITH TEMP AS (SELECT \
    OBJECT_NAME(f.parent_object_id) AS table_name\
    ,COL_NAME(fc.parent_object_id, fc.parent_column_id) AS constraint_column_name\
    ,OBJECT_NAME (f.referenced_object_id) AS referenced_object\
    ,COL_NAME(fc.referenced_object_id, fc.referenced_column_id) AS referenced_column_name\
    FROM sys.foreign_keys AS f\
    INNER JOIN sys.foreign_key_columns AS fc \
    ON f.object_id = fc.constraint_object_id) \
SELECT a.table_name AS table_name\
, a.constraint_column_name AS constraint_column_name\
, b.table_name AS referenced_object\
, b.constraint_column_name AS referenced_column_name\
 FROM TEMP a JOIN TEMP b on a.referenced_object = b.referenced_object AND \
a.referenced_column_name = b.referenced_column_name WHERE a.table_name != b.table_name', cnxn)

    relations = pd.concat([r1, r2])
    # print(relations)
    row_list = relations.values.tolist()
    retVal = {}
    retSet = set()
    for r in row_list:
        t1 = r[0]
        t2 = r[2]
        pairs = [".".join(c) for c in zip(r[0::2], r[1::2])]
        retSet.add(pairs[0])
        retSet.add(pairs[1])
        if t1 in retVal:
            temp = retVal[t1]
            if t2 in temp:
                temp[t2].append(pairs)
            else:
                temp[t2] = [pairs]
        else:
            temp = {t2:[pairs]}
            retVal[t1] = temp
        
        if t2 in retVal:
            temp = retVal[t2]
            if t1 in temp:
                temp[t1].append(pairs)
            else:
                temp[t1] = [pairs]
        else:
            temp = {t1:[pairs]}
            retVal[t2] = temp

    

    # row_list = df.values.tolist()
    # for i in range(len(row_list)):
    #     temp = row_list[i]

    #     row_list[i] = [".".join(c) for c in zip(temp[0::2], temp[1::2])]
    return retVal, retSet

def generateTable(names, joinT, joinK, schema):
    if schema != 'dbo':
        names = np.char.add(schema + ".", names)
        # names = schema + "." + np.array(names).astype(str)
    tname = " " + names[0]
    for i in range(len(names) - 1):
        name = names[i+1]
        join = joinT[i]
        key = " = ".join((joinK[i]).split(','))

        tname += " " + join + " " + name + " ON " + key
    return tname

# names = ['vitros_nc_results', 'roche_results'] 
# joinT = ['INNER JOIN'] 
# joinK = ['roche_results.SAMPLEID,vitros_nc_results.SAMPLEID']

# print(generateTable(names, joinT, joinK))