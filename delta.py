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
        filter(lambda i: (not(len(i) < 2 or len(i) >= 7)), splits))

    print(splits)

    foundAirportCodes = set([])
    foundDeltaCodes = set([])
    returnText = ''

    IGNORE_LIST = ['TSA', 'MQM', 'MQD', 'MQS',
                   "TIA", "CDC", 'JAL', 'ATL', "AND", 'IMO', 'NOW']

    # Check for Delta acronyms first, to skip over any airports that match it too.
    for i in splits:
        if i in IGNORE_LIST:
            pass
        elif i in DELTA_ACRONYM:
            acronym = DELTA_ACRONYM.get(i)
            foundDeltaCodes.add(i + ": " + acronym['name'])
        elif i in AIRPORTS:
            airport = AIRPORTS.get(i)
            foundAirportCodes.add(
                i + ": " + airport['name'] + " (" + airport['city'] + ")")

    if len(foundAirportCodes) != 0:
        returnText = "**Airports:**" + NEW_LINE + \
            NEW_LINE.join(foundAirportCodes) + NEW_LINE

    if len(foundDeltaCodes) != 0:
        returnText = returnText + "**Acronyms:**" + NEW_LINE + \
            NEW_LINE.join(foundDeltaCodes)

    if len(returnText) != 0:
        returnText = returnText + NEW_LINE + \
            "^(I am a bot. If you don't like me, feel free to [block me](https://www.reddit.com/settings/privacy).)"

    return returnText


def main():
    log("LOG: Called Main")
    reddit = praw.Reddit(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        password=PASSWORD,
        user_agent="web:AirportCodeBot:v1.0.0 (by /u/Airport-Code-Bot)",
        username=USERNAME,
    )

    unread_messages = []

    for mention in reddit.inbox.mentions(limit=10):
        try:
            if mention.new:
                content = mention.body

                if mention.parent_id.startswith('t1_'):
                    comment = reddit.comment(mention.parent_id)
                    content = content + " " + comment.body

                content = content + " " + mention.submission.title + \
                    " " + mention.submission.selftext

                acronyms = find_acronyms(content)

                if acronyms != '':
                    mention.reply(body=acronyms)
                    log("INFO: Replied to: " + " " + mention.body)

                unread_messages.append(mention)

        except Exception as e:
            log("ERROR: in main()")
            print(e)

    if len(unread_messages):
        reddit.inbox.mark_read(unread_messages)


log("LOG: App started")

while (True):
    main()
    time.sleep(15)
