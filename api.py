from flask import Flask, request, jsonify,render_template
import traceback
import tweepy as tw
import pandas as pd
import re
import nltk
try:
    nltk.data.find('/app/nltk_data/vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import praw

def cleanResume(resumeText):
    resumeText = re.sub('http\S+\s*', ' ', resumeText) 
    resumeText = re.sub('RT|cc', ' ', resumeText)
    resumeText = re.sub('#\S+', '', resumeText)
    resumeText = re.sub('@\S+', '  ', resumeText)
    resumeText = re.sub('[%s]' % re.escape("""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""), ' ', resumeText)
    resumeText = re.sub(r'[^\x00-\x7f]',r' ', resumeText) 
    resumeText = re.sub('\s+', ' ', resumeText)
    return resumeText.lower()



# Your API definition
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/result',methods = ['POST', 'GET'])
def result():
    if request.method == 'POST':
        result = request.form['file_name']
        access_token="1238649645615566848-KxUwD20cSaLCzMxKdBu2ECWqsxgSnr"
        access_token_secret="g1jNl3iJU34oGfw2W5ixLDVF34jnPhFSZCFdbRRTBZcfw"
        consumer_key="CPQGQmythvDe8aOdWr7Ac3HxE"
        consumer_secret="qBs5fPH96N0x9z2218MkAbyWo3l9vMmGedcWi5sQ04rTXSf4CT"
        auth= tw.OAuthHandler(consumer_key,consumer_secret)
        auth.set_access_token(access_token,access_token_secret)
        api = tw.API(auth, wait_on_rate_limit=True)
        search_words = '#'+result
        date_since = "2021-06-10"
        new_search = search_words
        tweets = tw.Cursor(api.search,q=search_words,lang="en",since=date_since).items(200)
        users_locs = [[tweet.text, tweet.user.screen_name] for tweet in tweets]
        tweet_text = pd.DataFrame(data=users_locs,columns=['text', "user_name"])
        tweet_text['cleaned_text'] = tweet_text.text.apply(lambda x: cleanResume(x))
        sia=SentimentIntensityAnalyzer()
        neg=0
        pos=0
        neut=0
        for i in range(len(tweet_text)):  
            score=sia.polarity_scores(tweet_text['cleaned_text'][i])['compound']
            if score>=-1.0 and score<=-0.1:
                neg=neg+1
            elif score>-0.1 and score<=0.1:
                neut=neut+1
            elif score>0.1:
                pos=pos+1
        reddit = praw.Reddit(client_id='tkGO7shOiNMcRg',client_secret='A6pGiADSTt3neqyBmY871DXChKg8Xg',user_agent='Sentiment',username='milind_raj_',password='Mraj@1000')
        subreddit = reddit.subreddit(result)
        top_subreddit = subreddit.hot(limit=100)
        topics_dict = { "title":[],"id":[]}
        for submission in top_subreddit:
            topics_dict["title"].append(submission.title)
            topics_dict["id"].append(submission.id)
        reddit_data=pd.DataFrame(topics_dict)
        reddit_data['cleaned_text'] = reddit_data.title.apply(lambda x: cleanResume(x))
        for i in range(len(reddit_data)):  
            score=sia.polarity_scores(reddit_data['cleaned_text'][i])['compound']
            if score>=-1.0 and score<=-0.1:
                neg=neg+1
            elif score>-0.1 and score<=0.1:
                neut=neut+1
            elif score>0.1:
                pos=pos+1
        commentlist = []
        for i in range(len(reddit_data)):
            submission = reddit.submission(id=reddit_data['id'][i])
            submission.comments.replace_more(limit=None)
            comment_queue = submission.comments[:]  
            while comment_queue:
                comment = comment_queue.pop(0)
                commentsdata = {}
                commentsdata["body"] = str(comment.body)
                commentlist.append(commentsdata)
                comment_queue.extend(comment.replies)
        replies=pd.DataFrame(commentlist)
        replies['cleaned_text'] = replies.body.apply(lambda x: cleanResume(x))
        for i in range(len(replies)):  
            score=sia.polarity_scores(replies['cleaned_text'][i])['compound']
            if score>=-1.0 and score<=-0.1:
                neg=neg+1
            elif score>-0.1 and score<=0.1:
                neut=neut+1
            elif score>0.1:
                pos=pos+1
        return render_template("home.html",result ='Analyzed latest '+str(len(tweet_text))+' tweets'+' and '+str(len(reddit_data)+len(replies))+' reddit posts and their replies',result1='Positive = '+str(pos)+'\nNegative = '+str(neg)+'\nNeutral = '+str(neut))

if __name__ == '__main__':
    
    app.run()
    
    
