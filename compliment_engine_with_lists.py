import csv
import sqlite3

import subprocess
import os
import re
from os import path

##
## RUN FACIAL RECOGNITION ALGORITHM ON PHOTO DB
##
#if need to re-enroll friend picture gallery: br -algorithm FaceRecognition -enrollAll -enroll ./compliment_pictures friends.gal
# subprocess.call('br -algorithm FaceRecognition -compare viewer.jpg friends.gal match_scores.csv', shell=True)


##
## IMPORT AND DETERMINE HIGHEST FACIAL RECOGNITION SCORE
##

# cleanup file


db = sqlite3.connect(':memory:')

def init_db(cur):
    cur.execute('''CREATE TABLE name_score_table (
        name TEXT,
        score INTEGER)''')

def populate_db(cur, csv_fp):
    rdr = csv.reader(csv_fp)
    cur.executemany('''
        INSERT INTO name_score_table (name, score)
        VALUES (?,?)''', rdr)

cur = db.cursor()
init_db(cur)
populate_db(cur, open('match_scores.csv'))
db.commit()

cur.execute('SELECT name, AVG(score) FROM name_score_table GROUP BY name order by AVG(score) desc')
all_rows = cur.fetchall()

#logging average scores
for row in all_rows:
	print('{0} : {1}'.format(row[0], row[1]))

# set highest avg score as viewer of complimentorator	
viewer = all_rows[0][0]
print viewer
