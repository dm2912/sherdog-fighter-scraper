Sherdog Fighter Scraper
=======================

A simple scraper to retrieve fighter data from sherdog.py in a predictable/easily machine readable format (.csv)

Updated 17 March 2018:

Added nickname, weight class, and fixed date stripping empty timestamp

Instructions:
-------------

Clone this repo (Or just download requirements.txt and sherdog-scraper.py and open a terminal window):

    git clone git@github.com:dm2912/sherdog-fighter-scraper.git

Install the requirements:

    pip install -r requirements.txt

Run:

    python filename_version.py

V1 - Exports automatically to csv file

V2 - Can now specify range to scrape (see end of file) and exports automatically to Json file
