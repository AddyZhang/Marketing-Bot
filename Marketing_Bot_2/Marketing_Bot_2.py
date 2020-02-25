import praw
import pandas as pd
from datetime import datetime
from praw.models import MoreComments

# Enter your client id, secret and user agent
reddit = praw.Reddit(client_id = 'k_irONQxgcqWFg',
                     client_secret = 'A6udBWn-8PXi2p7X34K7HT5THiA',
                     user_agent = 'Test')

# Reddit groups that Drew wants us to look at
Reddit_groups = ['depression', 'anxiety', 'OCD', 'socialanxiety', 'panicdisorder']

# Create a dataframe to store text data
def posts_to_df():
    # Write a loop to put hot post from all groups and their key info into one dataframe
    posts = []
    for group in Reddit_groups:
        mental_subreddit = reddit.subreddit(group)
        for post in mental_subreddit.hot(limit=10): # you can change the top number of posts

            posts.append([group, post.title, post.url])

    posts = pd.DataFrame(posts, columns = ['group','title', 'url'])

    return posts

# Insert today's date MM-DD-YYYY
import datetime

def get_date():
    """
    Get today's date (MM-DD-YYYY)
    """
    d = datetime.datetime.today()
    date = d.strftime('%m-%d-%Y')

    return date

# Google spreasheet
import gspread
from oauth2client.service_account import ServiceAccountCredentials

import time
import pprint
pp = pprint.PrettyPrinter()

# Enter key and spreadsheet key, name
json_key_file_name = 'New_Google.json'
spreadsheet_name = 'Popular Posts'
worksheet_list = ['Depression', 'Anxiety', 'OCD', 'Social Anxiety', 'Panic Disorder']

# credentials and client API
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive'] # access spreasheet and drive
creds = ServiceAccountCredentials.from_json_keyfile_name(json_key_file_name, scope) # enter your json file name
client = gspread.authorize(creds)

# Open worksheet and append dataframe
def upload_to_sheet(df, subreddit):
    idx = Reddit_groups.index(subreddit)
    sheet = client.open(spreadsheet_name).worksheet(worksheet_list[idx]) # open spreadsheet and then worksheet
    data_list = df.values.tolist()
    for info in data_list:
        sheet.insert_row(info, index=5) # add a row to worksheet

# Main Function
if __name__ == "__main__":
    # count = 0
    while True:
        df = posts_to_df() # get posts title and body dataframe
        date = get_date()

        df['date'] = date
        df = df[['date','group','title','url']] # change the order of cloumn
        # write a for loop to iterate group
        for subreddit in Reddit_groups:
            data = df[df.group == subreddit]
            data = data.drop(['group'],axis=1)
            upload_to_sheet(data,subreddit)
        # count += 1 # set up count for while loops
        time.sleep(86400) # set up sleep time, 86400 second for a day
