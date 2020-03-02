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

    posts = pd.DataFrame(posts, columns = ['Group','Title', 'Url'])

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

# DynamoDB
import boto3
import pandas as pd

dynamodb_resource = boto3.resource('dynamodb', region_name = 'us-west-1')
table_names = ['Depression', 'Anxiety', 'OCD', 'Social_Anxiety', 'Panic_Disorder']

def upload_to_dynamodb(df, subreddit):
    idx = Reddit_groups.index(subreddit)
    for index, row in df.iterrows():
        date = row['Date']
        index = row['Index']
        title = row['Title']
        url = row['Url']
        table_name = table_names[idx]
        table = dynamodb_resource.Table(table_name)
        table.put_item(
        Item = {
        'Date':date,
        'Index':int(index),
        'Title':title,
        'Url':url
        }
        )

# Main Function
if __name__ == "__main__":

    df = posts_to_df() # get posts title and body dataframe
    date = get_date()

    df['Date'] = date
    index_list = list(range(1,11))*5
    df['Index'] = index_list
    df = df[['Date','Group','Index','Title','Url']] # change the order of cloumn

    # write a for loop to iterate group
    for subreddit in Reddit_groups:
        data = df[df.Group == subreddit]
        data = data.drop(['Group'],axis=1)
        upload_to_dynamodb(data,subreddit)
