import praw
import pandas as pd
from datetime import datetime
from praw.models import MoreComments

import re
from collections import Counter
import itertools

import gensim
import gensim.corpora as corpora
from gensim.utils import simple_preprocess
from gensim.models import CoherenceModel

import spacy

import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.ERROR)

import warnings
warnings.filterwarnings("ignore",category=DeprecationWarning)

import nltk
nltk.download('stopwords')

from nltk.corpus import stopwords
stop_words = stopwords.words('english')
stop_words.extend(['im']) # too lazy to use Inverse Document Frequency to filter 'im'

import gspread
from oauth2client.service_account import ServiceAccountCredentials

import time
import pprint
pp = pprint.PrettyPrinter()

# Enter key and spreadsheet name
json_key_file_name = 'google.json'
spreadsheet_name = 'Hot Key Words'

# Enter your client id, secret and user agent
reddit = praw.Reddit(client_id = 'k_irONQxgcqWFg',
                     client_secret = 'A6udBWn-8PXi2p7X34K7HT5THiA',
                     user_agent = 'Test')

# Reddit groups that Drew wants us to look at
Reddit_groups = ['depression', 'anxiety', 'OCD', 'socialanxiety', 'panicdisorder']
Reddit_str = ''
for group in Reddit_groups:
    Reddit_str = Reddit_str + '+' + group

# Create a dataframe to store text data
def posts_to_df():
    # Write a loop to put hot post from all groups and their key info into one dataframe
    posts = []
    for group in Reddit_groups:
        print(group)
        mental_subreddit = reddit.subreddit(Reddit_str)
        for post in mental_subreddit.hot(limit=30): # you can change the top number of posts

            posts.append([post.title, post.score, post.num_comments, post.selftext])

    posts = pd.DataFrame(posts, columns = ['title', 'score','num_comments','body'])

    return posts


# Clean Title and Body
def remove_char(content):
    """
    Remove unnecessay characters
    """
    # remove new line character
    content = [re.sub('\s+', ' ', word) for word in content]

    # remove single quotes
    content = [re.sub("\'", "", word) for word in content]

    # remove *
    content = [re.sub("\*", ' ', word) for word in content]

    # remove /r/
    content = [re.sub("/r/", ' ', word) for word in content]

    return content

def content_to_words(sentences):
    """
    Transform string to list
    """
    for sentence in sentences:
        yield(gensim.utils.simple_preprocess(str(sentence), deacc=True))

def remove_stopwords(texts):
    """
    Remove stopwords
    """
    return [[word for word in simple_preprocess(str(doc)) if word not in stop_words] for doc in texts]

def make_bigrams(texts):
    """
    Bigram: two words frequently occuring (2-word phrase)
    """
    bigram = gensim.models.Phrases(texts, min_count=5, threshold=60) # higher threshold fewer phrases
    bigram_mod = gensim.models.phrases.Phraser(bigram)

    return [bigram_mod[doc] for doc in texts]

def lemmatization(texts, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV']):
    """
    https://spacy.io/api/annotation"""

    nlp = spacy.load('en', disable=['parser','ner'])

    texts_out = []
    for sent in texts:
        doc = nlp(" ".join(sent))
        texts_out.append([token.lemma_ for token in doc if token.pos_ in allowed_postags])

    return texts_out

def text_to_keywords(text):
    """
    Process text with above functions
    """
    content = remove_char(text) # remove unnecessary characs

    words_list = list(content_to_words(content)) # use gensim package to simple process texts

    words_nonstop = remove_stopwords(words_list) # remove stop words like "the" or "a"

    words_bigrams = make_bigrams(words_nonstop) # find two words frequently appear together

    data_lemmatized = lemmatization(words_bigrams, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV']) # Lemmatize e.g swam -> swim

    data_list = list(itertools.chain.from_iterable(data_lemmatized)) # join list of lists

    data_tuple = Counter(data_list).most_common(30) # extract top 30 words
    key_words_tuple = list(zip(*data_tuple))[0] # extract words
    key_words_list = [word for word in key_words_tuple] # data tuple to list
    print (key_words_list)

    return key_words_list

# Insert today's date MM-DD-YYYY
import datetime

def get_date():
    """
    Get today's date (MM-DD-YYYY)
    """
    d = datetime.datetime.today()
    date = d.strftime('%m-%d-%Y')

    return date

# credentials and client API
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive'] # access spreasheet and drive
creds = ServiceAccountCredentials.from_json_keyfile_name(json_key_file_name, scope) # enter your json file name
client = gspread.authorize(creds)

# Open worksheet and append row
def upload_to_sheet(info):
    sheet = client.open(spreadsheet_name).sheet1 # open spreadsheet and then worksheet
    sheet.insert_row(info) # add a row to worksheet
#     pp.pprint(sheet.get_all_records())

def list_to_string(list_words):
    str_words = ''
    for word in list_words:
        str_words = str_words + ' ' + word
    return str_words

# Main Function
if __name__ == "__main__":
    # count = 0
    while True:
        posts = posts_to_df() # get posts title and body dataframe
        content_title = posts.title.values.tolist() # list of title
        content_body = posts.body.values.tolist() # list of body
        kw_title = text_to_keywords(content_title) # list of title key words
        kw_body = text_to_keywords(content_body) # list of body key words

        date = get_date()
        str_title = list_to_string(kw_title)
        str_body =list_to_string(kw_body)

        sheet_info = []
        sheet_info.extend([date,str_title,str_body])

        upload_to_sheet(sheet_info)

        # count += 1 # set up count for while loops
        time.sleep(86400)
        # time.sleep(60) # set up sleep time, 86400 second for a day
