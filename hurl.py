# History of URLs (HURL)
# Rod Rickenbach
# 9/23/16
#
# HURL is used to determine whether historical snapshots of a URL exist in any
# Internet archives (ala wayback machine).  The goal is to take a graphical 
# snapshot of the historic URLs so that they can be examined for content 
# offline quickly.  

import argparse
import json
import urllib3
import datetime
import os
import string
from selenium import webdriver
from sys import exit

#Default master Memento server URL which returns data in a json format.  
#This probably shouldn't change...
MEMENTO_SERVER_URL="http://timetravel.mementoweb.org/timemap/json"


##############################################################################
# Parse a given timemap index and return valid urls from timemaps contained 
# therein.  Only scan memento compliant archives(?) 
##############################################################################
def get_history(source_url):

    # Normalize the url. This means strip off a leading http:// or https://
    # The strip command removes all of the listed leading characters
    
    if source_url.startswith('http'):
        source_url=source_url.strip('htps:/')

    memento_query=MEMENTO_SERVER_URL+'/http://'+source_url
    
    # Retrieve info from the URL we provide 
    r = http.request('GET', memento_query)

    # If we get an "OK" response (200) ie web page exists and is returned, then we
    # will process it

    if r.status==200:
        logfile.write('Successfully retrieved timemaps for %s from %s\n' % \
            (source_url,memento_query))

        mementos = []

        # Load data in json format
        json_data = json.loads(r.data)

        # Save the timemap index to log
        logfile.write('Timemap index:\n')
        logfile.write(json.dumps(json_data['timemap_index']))
        logfile.write('\n')

        # Parse the json data to get 
        mementos = parse_timemap_index(json_data['timemap_index'])

        for memento in mementos:
            memento_url=memento[0]
            memento_datetime=memento[1]
            memento_archiveid=memento[2]

            if memento_datetime >= start_datetime and \
                memento_datetime <= end_datetime:
                logfile.write('\t+ creating snapshot for %s : %s\n' % \
                    (memento_archiveid,str(memento_datetime)))
                create_image_snapshot(memento_url,memento_datetime,\
                    source_url, memento_archiveid)
            else:
                logfile.write('\t- skipped snapshot for %s : %s\n' % \
                    (memento_archiveid,str(memento_datetime)))

    else:
        logfile.write('Could not retrieve timemaps for %s from %s\n' % \
            (source_url,memento_query))
    
    return

##############################################################################
# Parse a given timemap index and return valid urls from timemaps contained 
# therein.  Only scan memento compliant archives(?) 
##############################################################################
def parse_timemap_index(timemap_index):

    mementos=[]

    for timemap in timemap_index:
        # Unsure if timemaps need be memento compliant...
        if timemap['memento_compliant'] =='yes':
            new_mementos=get_urls_from_timemap(timemap['uri'],\
                timemap['archive_id'])
            if new_mementos:
                mementos+=new_mementos
    
    return(mementos)

##############################################################################
# Open a timemap link and extract all urls
# All observed instances of timemaps are returned as a "link" type and not in
# json format although the memento specifications permit either type.  It 
# appears that link format has won. I was going to write a module to parse 
# json formatted timemaps, but it seems pointless until I can test the code 
# on something in the wild... But I am naming/structuring as if json exists.
##############################################################################
def get_urls_from_timemap(timemap_url,timemap_archiveid):

    #Get the data from a given timemap url 
    r = http.request('GET', timemap_url)
    
    # If we get a response, parse it... For now we assume link format
    if r.status==200: 
        logfile.write('\t+ extracting URLs from archive: %s\n' % \
                    timemap_archiveid)
        return(extract_urls_from_link_format(r.data,timemap_archiveid))
    else:
        logfile.write('\t- could not access archive: %s\n' % \
                    timemap_archiveid)

    return

##############################################################################
# Parse the "link" type format of a timemap.  Extract mementos.
##############################################################################

def extract_urls_from_link_format(link_data,archiveid):
    
    mementos = []

    for line in link_data.split('\n'):
        # Only return urls that are marked as mementos
        # Includes: "first memento","memento",and "last memento"
        if 'memento\"; datetime' in line:
    
            # This returns the first element of a link style memento which
            # holds the proper URL.  This field starts with a < which we bypass 
            # with an index of 1 and ends with a ">; ".  While > and ; can be
            # part of a valid URL, that sequnce ending with a space cannot...
            memento=line[1:line.find('>; ')]

            # Example tail of line is: datetime="Fri, 18 Dec 2009 16:07:02 GMT",
            # This grabs the last element in the string which identifies
            # the date and time.  Trim things up (+15) to lose the 'datetime'
            # part of the string as well as the three letter day of the week
            # we wont need.  We can use datetime for narrowing our search...
            # BTW, the date_time[:24] thing only took me 3 hours to get right.
            # For some reason me using rstrip to trim up the end of the line
            # worked on every site except the library of congress, which
            # reared it's ugly head as I was about to demo this on video
            # I HAVE NO IDEA WHY IT WON'T WORK THE WAY I HAD IT.
            # Anyway this is simpler, thank God that the datetime field is of
            # length due to formatting...          
            
            date_time=line[line.find('datetime=\"')+15:]
            date_time=date_time[:24]

            # Create a comparable date
            memento_datetime=datetime.datetime.strptime(\
                date_time,'%d %b %Y %X %Z')

            # Pass appropriate info including archive id
            mementos.append([memento,memento_datetime,archiveid])

    return(mementos)

##############################################################################
# Parse the "json" type format of a timemap.  Does nothing now.  Placeholder.
##############################################################################

def extract_urls_from_json_format(link_data):
    
    mementos = []

    # link data is one long string. Split on newlines to get individual lines
    for line in link_data.split('\n'):
        pass
    return

##############################################################################
# Create jpeg image snapshots of each webpage (list of urls)
# Some info on using selenium to take screenshots found here:
# http://stackoverflow.com/questions/18067021/how-do-i-generate-a-png-file-w-selenium-phantomjs-from-a-string
# Also in https://github.com/scottymeyers/layback which is a similar project
# Layback looks like better python code than mine, probably would have been
# Easier to start with that but I would have learned less ;)
##############################################################################

def create_image_snapshot(memento_url,url_datetime,original_url,archiveid):
    
    driver = webdriver.PhantomJS() 
    driver.set_window_size(1024, 768)
    
    print 'Saving image of '+original_url+' (archive: '+archiveid+') from '+\
        str(url_datetime) 
    driver.get(memento_url)
    # Get the "base" url (remove http:// from head and / from tail)
    #base_url=url.rstrip('/')
    #base_url=base_url[base_url.rfind('/')+1:]
    # remove colons from time, generally a bad idea in a Windows filename
    driver.save_screenshot(os.path.join(output_dir,\
        original_url.translate(None,':/\\') +' ('+ archiveid+') ' + \
        str(url_datetime).replace(':','')+'.png'))

    driver.quit()
    
    return

##############################################################################
# The main program
##############################################################################

# Set up the arguments list using argparse
parser = argparse.ArgumentParser(description='Generate snapshots to show the history of a given URL')
parser.add_argument('-d', '--dir', help='output directory')
parser.add_argument('-s', '--startdate', help='start creating images from date formatted MM-DD-YYYY')
parser.add_argument('-e', '--enddate', help='stop creating images at date formatted MM-DD-YYYY')
#parser.add_argument('-t', '--text', help='add textual info on top of snapshot images')
parser.add_argument('-l','--logfile', help='logfile name (default is logfile.txt)')
group = parser.add_mutually_exclusive_group()
group.add_argument('-u', '--urls', help = 'text file containing list of urls to process (one URL per line)')
group.add_argument('-i', '--individual', help='single URL to process')
args = parser.parse_args()

# Start making sense of the args

if not args.urls and not args.individual:
    print 'Must have a single url (-i) or list of urls (-u) to process'
    print '\n use -h argument for basic help.'
    exit()

if args.dir == None:
    args.dir = '.'
# Create output directory if it doesn't exist
elif not os.path.exists(args.dir):
    os.makedirs(args.dir)

# Set the starting date for image processing
if not args.startdate:
    start_datetime=datetime.datetime(1970,1,1,0,0,0)
else:
    split_date=args.startdate.split('-')
    if len(split_date) != 3:
        print 'Start date must be in format MM-DD-YYYY'
        exit()
    else:
        start_datetime=datetime.datetime(int(split_date[2]),\
            int(split_date[0]),int(split_date[1]),0,0,0)

# Set the ending date for image processing
if not args.enddate:
    end_datetime=datetime.now()
else:
    split_date=args.enddate.split('-')
    if len(split_date) != 3:
        print 'End date must be in format MM-DD-YYYY'
        exit()
    else:
        end_datetime=datetime.datetime(int(split_date[2]),\
            int(split_date[0]),int(split_date[1]),23,59,59)

if end_datetime<start_datetime:
    print 'Start date must be before the end date!'
    exit()

#determine path to the output directory and create appropriate variable
output_dir=os.path.abspath(args.dir)

# Start a logfile
if args.logfile:
    logfile = open(os.path.join(output_dir,args.logfile),'w')
else:
    logfile = open(os.path.join(output_dir,'logfile.txt'),'w')


# Setup Http pool manager
http = urllib3.PoolManager()

# Work on individual or lists of urls
if args.individual:
    get_history(args.individual)
else:
    #Loop to parse urls from file
    with open(args.urls) as fp:
        for line in fp:
            line=line.rstrip('\n')
            get_history(line)