"""
    A simple scraper to retrieve data from sherdog.py
   

    ===============================================================
    
    Original script - Copyright (c) 2012, Patrick Carey
    
    https://github.com/paddycarey/sherdog-fighter-scraper
    
    ===============================================================
    
    Requires: Python / Beautiful soup min 3.2.1 / requests min 0.14.2
    
    Modified 2018, Dimspace
    
    Dates tidied up and timestamps removed, weight classes added, Nicknames added
    
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

# stdlib imports
import codecs
import csv
import datetime
from BeautifulSoup import BeautifulSoup
import requests
import cStringIO


class Scraper(object):

    """A collection of functions which can be used to retrieve and parse fight related data from sherdog.com"""

    # Base URL for all requests
    base_url = 'http://www.sherdog.com'

    @classmethod
    def fetch_url(self, url):

        """Fetch a url and return it's contents as a string"""

        uf = requests.get(url)
        return uf.text

    @classmethod
    def isNone(self, x):

        """Simple check if an object is None for use in building list comprehensions"""

        if x is not None:
            return False
        else:
            return True

    @classmethod
    def scrape_fighter(self, fighter_id):

        """Retrieve and parse a fighter's details from sherdog.com"""

        # make sure fighter_id is an int
        fighter_id = str(fighter_id)

        # fetch the required url and parse it
        url_content = self.fetch_url('%s/fighter/x-%s' % (self.base_url, fighter_id))
        soup = BeautifulSoup(url_content)

        # get the fighter's name
        name = soup.find('h1', {'itemprop': 'name'}).span.contents[0]

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

        last_fight = soup.find('span', {'class': 'sub_line'}).contents[0]
        last_fight = datetime.datetime.strptime(last_fight, '%b / %d / %Y').date()
        last_fight = last_fight.isoformat()
              
        wld = {}
        wld['wins'] = 0
        wld['losses'] = 0
        wld['draws'] = 0
        wlds = soup.findAll('span', {'class': 'result'})
        for x in wlds:
            wld[x.contents[0].lower()] = x.findNextSibling('span').contents[0]
            

        # build a dict with the scraped data and return it
        result = {
            'name': name,
            'birth_date': birth_date,
            'nickname': nickname,
            'wclass': wclass,
            'nationality': nationality,
            'camp_team': camp_team,
            'id': fighter_id,
            'last_fight': last_fight,
            'wins': wld['wins'],
            'losses': wld['losses'],
            'draws': wld['draws'],
        }
        return result


class UnicodeWriter:

    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        try:
            self.writer.writerow([s.encode("utf-8") for s in row])
        except UnicodeDecodeError:
            self.writer.writerow(row)
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


if __name__ == '__main__':

    scraper = Scraper()
    out_file = open('sherdog-fighters.csv', 'w')
    csv_file = UnicodeWriter(out_file)

    headers = ['ID', 'Name', 'Nickname', 'Date of Birth', 'Nation', 'Weight Class', 'Gym', 'W', 'L', 'D', 'Last Fight']
    csv_file.writerow(headers)

    x = 1
    while True:

        try:
            fighter = scraper.scrape_fighter(x)
            # print json.dumps(fighter, indent=2)
            print "%s: %s" % (fighter['id'].zfill(5), fighter['name'])
        except KeyboardInterrupt:
            break
        except AttributeError:
            x += 1
        else:
            x += 1
            row = [
                fighter['id'],
                fighter['name'],
                fighter['nickname'],
                fighter['birth_date'],
                fighter['nationality'],
                fighter['wclass'],
                fighter['camp_team'],
                fighter['wins'],
                fighter['losses'],
                fighter['draws'],
                fighter['last_fight'],
            ]
            row = [str(c) for c in row]
            csv_file.writerow(row)

    print 'Exiting'
    out_file.close()
