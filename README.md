# HURL
History of URLs - Creates historical images of websites based on Mementos

https://youtu.be/5DwryR43a9Q

Rod Rickenbach

HURL is used to determine whether historical snapshots of a URL exist in any Internet archives (ala wayback machine).  The goal is to take a graphical snapshot of the historic URLs so that they can be examined for content offline quickly.  

usage: hurl.py [-h] [-d DIR] [-s STARTDATE] [-e ENDDATE] [-l LOGFILE]
               [-u URLS | -i INDIVIDUAL]

Generate snapshots to show the history of a given URL

optional arguments:
  -h, --help            show this help message and exit
  -d DIR, --dir DIR     output directory
  -s STARTDATE, --startdate STARTDATE
                        start creating images from date formatted MM-DD-YYYY
  -e ENDDATE, --enddate ENDDATE
                        stop creating images at date formatted MM-DD-YYYY
  -l LOGFILE, --logfile LOGFILE
                        logfile name (default is logfile.txt)
  -u URLS, --urls URLS  text file containing list of urls to process (one URL
                        per line)
  -i INDIVIDUAL, --individual INDIVIDUAL
                        single URL to process
