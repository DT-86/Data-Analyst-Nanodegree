# Written for Python 3.7
# -*- coding: utf-8 -*-
import sqlite3
import csv
from pprint import pprint as pp

# 1. Create database file
sqlite_file = "openstreetmap_xml.db"

# 2. Create connection to the database
conn = sqlite3.connect(sqlite_file)

# 3. Assign cursor object
cur = conn.cursor()

# 4. Create queries to drop tables if they exist, and create new tables
drop_node_tags = """ DROP TABLE IF EXISTS nodes_tags"""
create_node_tags_table = """
    CREATE TABLE nodes_tags (
    id INTEGER,
    key TEXT,
    value TEXT,
    type TEXT,
    FOREIGN KEY (id) REFERENCES nodes(id)
)"""

drop_nodes = """ DROP TABLE IF EXISTS nodes"""
create_nodes_table = """
    CREATE TABLE nodes (
    id INTEGER PRIMARY KEY NOT NULL,
    lat REAL,
    lon REAL,
    user TEXT,
    uid INTEGER,
    version INTEGER,
    changeset INTEGER,
    timestamp TEXT
)"""

drop_ways = """ DROP TABLE IF EXISTS ways"""
create_ways_table = """
CREATE TABLE ways (
    id INTEGER PRIMARY KEY NOT NULL,
    user TEXT,
    uid INTEGER,
    version TEXT,
    changeset INTEGER,
    timestamp TEXT
)"""

drop_ways_tags = """ DROP TABLE IF EXISTS ways_tags"""
create_ways_tags_table = """
CREATE TABLE ways_tags (
    id INTEGER NOT NULL,
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    type TEXT,
    FOREIGN KEY (id) REFERENCES ways(id)
)"""

drop_ways_nodes = """ DROP TABLE IF EXISTS ways_nodes"""
create_ways_nodes_table = """
CREATE TABLE ways_nodes (
    id INTEGER NOT NULL,
    node_id INTEGER NOT NULL,
    position INTEGER NOT NULL,
    FOREIGN KEY (id) REFERENCES ways(id),
    FOREIGN KEY (node_id) REFERENCES nodes(id)
)"""


def reset_table(drop_instructions, create_instructions):
    """reset_table drops current table and creates a new table

    :param drop_instructions: valid sql query to drop table
    :type drop_instructions: string
    :param create_instructions: valid sql query to create table
    :type create_instructions: string
    """
    cur.execute(drop_instructions)
    conn.commit()
    cur.execute(create_instructions)
    conn.commit()


# drop node_tags table if it exists, create new table, and transfer csv contents
reset_table(drop_node_tags, create_node_tags_table)
with open("nodes_tags.csv", "r", encoding="utf-8") as csv_file:
    csv_reader = csv.DictReader(csv_file)
    # comma is the default delimiter
    push_to_db = [(i["id"], i["key"], i["value"], i["type"]) for i in csv_reader]
cur.executemany("INSERT INTO nodes_tags(id, key, value,type) VALUES (?, ?, ?, ?);", push_to_db)
conn.commit()

# drop node_ table if it exists, create new table, and transfer csv contents
reset_table(drop_nodes, create_nodes_table)
with open("nodes.csv", "r", encoding="utf-8") as csv_file:
    csv_reader = csv.DictReader(csv_file)  # comma is the default delimiter
    push_to_db = [
        (
            col["id"],
            col["lat"],
            col["lon"],
            col["user"],
            col["uid"],
            col["version"],
            col["changeset"],
            col["timestamp"],
        )
        for col in csv_reader
    ]
cur.executemany(
    "INSERT INTO nodes(id, lat, lon, user, uid, version, changeset, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?);",
    push_to_db,
)
conn.commit()

# drop ways table if it exists, create new table, and transfer csv contents
reset_table(drop_ways, create_ways_table)
with open("ways.csv", "r", encoding="utf-8") as csv_file:
    csv_reader = csv.DictReader(csv_file)  # comma is the default delimiter
    push_to_db = [
        (col["id"], col["user"], col["uid"], col["version"], col["changeset"], col["timestamp"]) for col in csv_reader
    ]
cur.executemany(
    "INSERT INTO ways(id, user, uid, version, changeset, timestamp) VALUES (?, ?, ?, ?, ?, ?);", push_to_db,
)
conn.commit()

# drop ways_tag table if it exists, create new table, and transfer csv contents
reset_table(drop_ways_tags, create_ways_tags_table)
with open("ways_tags.csv", "r", encoding="utf-8") as csv_file:
    csv_reader = csv.DictReader(csv_file)  # comma is the default delimiter
    push_to_db = [(i["id"], i["key"], i["value"], i["type"]) for i in csv_reader]

cur.executemany("INSERT INTO ways_tags(id, key, value,type) VALUES (?, ?, ?, ?);", push_to_db)
conn.commit()

# drop ways_nodes table if it exists, create new table, and transfer csv contents
reset_table(drop_ways_nodes, create_ways_nodes_table)
with open("ways_nodes.csv", "r", encoding="utf-8") as csv_file:
    csv_reader = csv.DictReader(csv_file)  # comma is the default delimiter
    push_to_db = [(col["id"], col["node_id"], col["position"]) for col in csv_reader]
cur.executemany("INSERT INTO ways_nodes(id, node_id, position) VALUES (?, ?, ?);", push_to_db)
conn.commit()

# check that all tables have items after insertions are complete
table_list = ["ways", "nodes", "ways_tags", "nodes_tags", "ways_nodes"]
for table in table_list:
    query = f"SELECT count(*) FROM {table}"
    cur.execute(query)
    pp(f"{table.capitalize()} Table:   {cur.fetchall()[0][0]} items")

# close the connection
conn.close()
