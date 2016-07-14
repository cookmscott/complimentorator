# -*- coding: utf-8 -*-
import subprocess
import csv
import os
import re
from os import path
import random
import pygame
from pygame.locals import *
import csv
import sqlite3
import time

###############################################
###                 FUNCTIONS 
###############################################

#picture display size
width = 1920
height = 1080
windowSurfaceObj = pygame.display.set_mode((width,height),FULLSCREEN)
pygame.display.set_caption('compli-buddy')

# create function to display images
def display_image(image_file_path):
    image=pygame.image.load(image_file_path)
    windowSurfaceObj.fill((0,0,0))
    windowSurfaceObj.blit(image,(width/4,0))
    pygame.display.update()

###############################################
### RUN FACIAL RECOGNITION ALGORITHM 
###############################################

# show "smile" text
display_image("/home/pi/Documents/complimentorator/camera.png")

# capture image of viewer
# subprocess.call('fswebcam --no-banner viewer.jpg', shell=True)

# if need to re-enroll friend picture gallery: br -algorithm FaceRecognition -enrollAll -enroll ./compliment_pictures friends.gal
subprocess.call('br -algorithm FaceRecognition -compare viewer.jpg friends.gal match_scores.csv', shell=True)

###############################################
### INGEST SCORES, ANALYSE, AND ASSIGN VIEWER
###############################################

# ingest match_scores.csv
with open('match_scores.csv', 'rb') as f:
    next(f) # skip header
    reader = csv.reader(f)
    match_scores_list = list(reader)

# use regex to pull first name only from file name in match scores output
for i in range(len(match_scores_list)): 
    match_scores_list[i][0]=re.sub("\s(.*)","", os.path.basename(match_scores_list[i][0]))

# convert list to sql table and generate avg usage
# creates table that has name and score (every name score pair in record in table)
db = sqlite3.connect(':memory:')

def init_db(cur):
    cur.execute('''CREATE TABLE name_score_table (
        name TEXT,
        score INTEGER)''')

def populate_db(cur, match_score_list):
    cur.executemany('''
        INSERT INTO name_score_table (name, score)
        VALUES (?,?)''', match_score_list)

cur = db.cursor()
init_db(cur)
populate_db(cur, match_scores_list)
db.commit()

cur.execute('SELECT name, AVG(score) FROM name_score_table GROUP BY name order by AVG(score) desc')
all_rows = cur.fetchall()

#logging average scores
for row in all_rows:
	print('{0} : {1}'.format(row[0], row[1]))

# set highest avg score as viewer of complimentorator	
viewer = all_rows[0][0]
print viewer

##################################################################
###                 SPEECH & VISUAL SYNTHESIS                  ###
##################################################################

# create emoji map from file of emoticons :) and file paths to each image
with open('./compliment_bank/emoji_map.txt', 'rb') as f:
    reader = csv.reader(f)
    emoji_map = list(reader)

# create function to give file path of matching emoji
def emoji_file_path(emoji_from_compliment):
    # pull second column of faces
    list_of_emojis = zip(*emoji_map)[1]
    # emoji must be in file to get assigned a file path
    if emoji_from_compliment in list_of_emojis:
        index = list_of_emojis.index(emoji_from_compliment)
    else:
        index=0
    return 'compliment_emojis/'+emoji_map[index][2]

##                                                              ##
## Decide what compliment that friendly viewer is going to hear ##
##                                                              ##

# function to return position of randomly weighted selection
def weighted_choice(weights):
    totals = []
    running_total = 0

    for w in weights:
        running_total += w
        totals.append(running_total)

    rnd = random.random() * running_total
    for i, total in enumerate(totals):
        if rnd < total:
            return i

# pick regular or name based compliment
if random.random() > 0.08:
    with open('./compliment_bank/compliment_list.txt', 'rb') as f:
        reader = csv.reader(f)
        compliment_list = list(reader)
else:
    with open('./compliment_by_name/%s.txt' % viewer, 'rb') as f:
        reader = csv.reader(f)
        compliment_list = list(reader)
        
# function to choose a compliment by weight, and break into components
compliment=[]
# get all weights and convert to int
compliment_weights = [ int(s) for s in zip(*compliment_list)[0] ]
# select a compliment
compliment_pos = weighted_choice(compliment_weights)
# get compliment text
compliment = compliment_list[compliment_pos][1]
# create individual compliment components
compliment_components=compliment.split('/')

#
# Prepend the personalized Greeting
#
greeting=[]
greeting.append("Hello %s!" % viewer)
opening_smile=[]
opening_smile.append('/:)/')
compliment_components = opening_smile + greeting + compliment_components

##
## SPEAK & DISPLAY
##

# speak and display emojis
for block in compliment_components:
    print emoji_file_path(block)
    # if alphanumeric, speak!
    if re.match('^[A-Za-z\s]{1}',block) is not None:
        subprocess.call("pico2wave -w speak_now.wav '%s'" % block,shell=True)
        subprocess.call("aplay speak_now.wav",shell=True)
    else:
        display_image(emoji_file_path(block))
