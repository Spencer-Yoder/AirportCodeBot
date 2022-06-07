import json
import re
import praw
import time
import os

CLIENT_ID = os.environ['CLIENT_ID']
CLIENT_SECRET = os.environ['CLIENT_SECRET']
PASSWORD = os.environ['PASSWORD']
USERNAME = os.environ['USERNAME']

NEW_LINE = "\n\n "

# https://github.com/ram-nadella/airport-codes/blob/master/airports.json
AIRPORTS_FILE = open('airports.json', encoding="utf8")
DELTA_ACRONYM_FILE = open('deltaAcronym.json', encoding="utf8")

AIRPORTS = json.load(AIRPORTS_FILE)
DELTA_ACRONYM = json.load(DELTA_ACRONYM_FILE)

AIRPORTS_FILE.close()
DELTA_ACRONYM_FILE.close()


def log(message):
    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)
    print(current_time + " - " + message)


def find_acronyms(text):

    # Convert the post to uppercase and split on any non normal character
    splits = re.split('[^A-Za-z0-9+]', text)

    # Skip any words that are under 2 or more then 5 characters
    splits = list(
        filter(lambda i: (not(len(i) < 2 or len(i) >= 5)), splits))

    foundAirportCodes = set([])
    foundDeltaCodes = set([])
    returnText = ''

    # Check for Delta acronyms first, to skip over any airports that match it too.
    for i in splits:
        if i in DELTA_ACRONYM:
            acronym = DELTA_ACRONYM.get(i)
            foundDeltaCodes.add(i + ": " + acronym['name'])
        elif i in AIRPORTS:
            airport = AIRPORTS.get(i)
            foundAirportCodes.add(i + ": " + airport['name'])

    if len(foundAirportCodes) != 0:
        returnText = "**Airports:**" + NEW_LINE + \
            NEW_LINE.join(foundAirportCodes) + NEW_LINE

    if len(foundDeltaCodes) != 0:
        returnText = returnText + "**Acronyms:**" + NEW_LINE + \
            NEW_LINE.join(foundDeltaCodes)

    return returnText


def has_posted(comments):
    for comment in comments:
        if comment.author == USERNAME:
            return True

    return False


def main():
    reddit = praw.Reddit(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        password=PASSWORD,
        user_agent="web:AirportCodeBot:v1.0.0 (by /u/Airport-Code-Bot)",
        username=USERNAME,
    )

    subreddit = reddit.subreddit("delta")
    # subreddit = reddit.subreddit("test")

    for submission in subreddit.new(limit=1):
        if not has_posted(submission.comments):
            acronyms = find_acronyms(
                submission.title + " " + submission.selftext)
            if acronyms != '':
                submission.reply(body=acronyms)
                log("INFO: post response posted successfuly")

        for comment in submission.comments:
            if comment.is_submitter:
                if not has_posted(comment.replies):
                    acronyms = find_acronyms(comment.body)
                    comment.reply(body=acronyms)
                    log("INFO: comment response posted successfuly")


while(True):
    try:
        main()
    except Exception as e:
        log("ERROR: in main()")
        print(e)

    log("INFO: Main Compleated")
    time.sleep(300)
