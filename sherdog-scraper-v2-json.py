"""
    A simple scraper to retrieve data from sherdog.py
   
    ===============================================================
    
    Original script - Copyright (c) 2012, Patrick Carey
    
    https://github.com/paddycarey/sherdog-fighter-scraper
    
    ===============================================================
    
    Requires: Python / Beautiful soup min 3.2.1 / requests min 0.14.2
    
    v1. Modified 2018, Dimspace
    Dates tidied up and timestamps removed, weight classes added, Nicknames added
    
    https://github.com/dm2912/sherdog-fighter-scraper/
    
    v2. Modifed 2018, Alejandro Castellanos Jaramillo 
    ID iteration report added, ability to specify scrape range. Exports to json now.
    
    https://gitlab.com/alejandrocastellanosjaramillo/MMA_cosas/tree/master
    
    ================================================================
    Permission to use, copy, modify, and/or distribute this software for any
    purpose with or without fee is hereby granted, provided that the above
    copyright notice and this permission notice appear in all copies.
    THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
    WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
    MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
    ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
    WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
    ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR
    IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
    
"""
#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# stdlib imports
import codecs
import datetime
from BeautifulSoup import BeautifulSoup
import requests



import json#--to import the file.



def scrape_fighter(fighter_id,FIGHTERS):
	#fighter_id = 8000
	fighter_text_id = str(fighter_id)

	# fetch the required url and parse it
	url_content = requests.get('%s/fighter/x-%s' % (base_url, fighter_text_id)).text
	soup = BeautifulSoup(url_content)
	name = soup.find('h1', {'itemprop': 'name'}).span.contents[0]# get the fighter's name

	# get the fighter's birth date
	try:
	  birth_date = soup.find('span', {'itemprop': 'birthDate'}).contents[0]
	except AttributeError:
	  birth_date = None
	else:
	    if birth_date == 'N/A':
	      birth_date = None
	    else:
		 birth_date = datetime.datetime.strptime(birth_date, '%Y-%m-%d').date()
		 birth_date = birth_date.isoformat()
	# get the fighter's nickname
	try:
	  nickname = soup.find('span', {'class': 'nickname'}).em.contents[0]
	except AttributeError:
	  nickname = None
	# get the fighter's weight-class
	try:
	  wclass = soup.find('h6', {'class': 'item wclass'}).strong.a.contents[0]
	except AttributeError:
	  wclass = None
	# get the fighter's nationality
	try:
	  nationality = soup.find('strong', {'itemprop': 'nationality'}).contents[0]
	except AttributeError:
	  nationality = None
	# get the fighter's camp/team
	try:
	  camp_team = soup.find('h5', {'class': 'item association'}).strong.span.a.span.contents[0]
	except AttributeError:
	  camp_team = None
	#  settling last fight (sounds dramatic!):
	last_fight = soup.find('span', {'class': 'sub_line'}).contents[0]
	last_fight = datetime.datetime.strptime(last_fight, '%b / %d / %Y').date()
	last_fight = last_fight.isoformat()
	#  building record:
	record = {}#-- WIN -- LOSS -- DRAW #(variable was named 'wld' previously).
	record['wins'] = 0
	record['losses'] = 0
	record['draws'] = 0
	records = soup.findAll('span', {'class': 'result'})
	for x in records:
	  record[x.contents[0].lower()] = x.findNextSibling('span').contents[0]

	# build a dict with the scraped data and return it
	fighter_data = {
		    'name': name,
		    'birth_date': birth_date,
		    'nickname': nickname,
		    'wclass': wclass,
		    'nationality': nationality,
		    'camp_team': camp_team,
		    'id': fighter_id,
		    'last_fight': last_fight,
		    'wins': record['wins'],
		    'losses': record['losses'],
		    'draws': record['draws'],
		}
	#--creating a container for the fighters named FIGHTERS:
	FIGHTERS.append(fighter_data)
#_________________________________________#
#_________________________________________#
def scrape_fighterS(fighter_id_start,fighter_id_end,FIGHTERS,chirp):
	fighter_id = fighter_id_start
	while fighter_id <= fighter_id_end:
	  try:
	    scrape_fighter(fighter_id, FIGHTERS)
	  except AttributeError:
	    fighter_id = fighter_id + 1
	  if fighter_id % chirp == 0:#--check iteration. 
	    print("**ID report:",fighter_id)
	  fighter_id=fighter_id + 1
#_________________________________________#
#_________________________________________#
def export_json(FIGHTERS,file_name):
	with open(file_name, "w") as file:
	  file.write(json.dumps(FIGHTERS)) #--writing straight to json.
#####
#####
#--IMPLEMENTATION:
#####
#####
FIGHTERS = []#--where fighter data will be stored.

fighter_id_start = 115437
fighter_id_end   = fighter_id_start+8
chirp = 1#--an ID will be reported for every multiple of this number.

# Base URL for all requests
base_url = 'http://www.sherdog.com'
#--SCRAPING FIGHTER CHUNK:
print("--scraping fighters within interval...")
scrape_fighterS(fighter_id_start,fighter_id_end,FIGHTERS,chirp)
#--SAVING THE FILE:
print("--exporting to JSON file...")
file_name = "fighterIDs_"+str(fighter_id_start)+"--"+str(fighter_id_end)+".json"
print("                     ...finished.")
export_json(FIGHTERS,file_name)


#-----------------
print(" ")
print("______________________")
print("FINISHED SUCCESSFULLY.")
