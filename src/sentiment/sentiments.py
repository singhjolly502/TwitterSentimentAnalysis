from datetime import datetime
import os
import re
import matplotlib.pyplot as plt
import pandas as pd
import tweepy
from textblob import TextBlob
from src.auth import engine, config


# class with main logic
class SentimentAnalysis:

    def __init__(self):
        pass

    # function to clean the tweet
    def clean_tweet(self, text):
        text = re.sub(r'@[A-Za-z0-9]+', '', text)
        text = re.sub(r'#', '', text)
        text = re.sub(r'RT\s+', '', text)
        text = re.sub(r'http\S+', '', text)
        return text

    # function to calculate percentage
    def percentage(self, value, whole):
        final_percent = 100 * float(value) / float(whole)
        return round(final_percent, 2)

    # This func make connection to the Tweepy API
    def authorisation(self):
        consKey = '4edL39Tj7KxBWGyS0G9wOkuLz'
        consSecret = 'DJ3statUgZr1tvscyyUXOXHNKZHAdBaJ9ycBrLllOKgjwL7Nu7'
        accessToken = '1543101708242661377-ZZ0torUtKyU1s0ECPLQ713J6i1DtBt'
        accessTokenSecret = 'dfe1IPYDCaFK0UTAUoEyQCfAnzyo62gOW0DWkZ3KeOkfW'
        auth = tweepy.OAuthHandler(consKey, consSecret)
        auth.set_access_token(accessToken, accessTokenSecret)
        api = tweepy.API(auth, wait_on_rate_limit=True)
        return api

    def search_tweets(self, api, keyword, n_tweets):
        # searching for tweets
        # searchTerm = input("Enter Keyword/Tag to search about: ")
        # NoOfTerms = int(input("Enter how many tweets to search: "))
        tweets = tweepy.Cursor(api.search_tweets, q=keyword, lang="en").items(n_tweets)
        return tweets

    def process_tweets(self, tweets, n_tweets):
        # def process_tweets(tweets_data):
        results = []
        count_stats = {'polarity': 0, 'total_polarity': 0, 'positive': 0, 'wpositive': 0, 'spositive': 0,
                       'negative': 0, 'wnegative': 0, 'snegative': 0, 'neutral': 0}
        final_stats = {'polarity': 0, 'total_polarity': 0, 'positive': 0, 'wpositive': 0, 'spositive': 0, 'negative': 0,
                       'wnegative': 0, 'snegative': 0, 'neutral': 0}
        for tweet in tweets:
            text = tweet.text
            clean_text = self.clean_tweet(text)
            tweet_id = int(tweet.id_str)
            time = datetime.strftime(tweet.created_at, "%d-%m-%Y %H:%M:%S")
            # print(time)
            polarity = self.predict(clean_text)
            count_stats['polarity'] += polarity

            # adding reaction of how people are reacting to find average later
            if polarity == 0:
                count_stats['neutral'] += 1
            elif 0 < polarity <= 0.3:
                count_stats['wpositive'] += 1
            elif 0.3 < polarity <= 0.6:
                count_stats['positive'] += 1
            elif 0.6 < polarity <= 1:
                count_stats['spositive'] += 1
            elif -0.3 < polarity <= 0:
                count_stats['wnegative'] += 1
            elif -0.6 < polarity <= -0.3:
                count_stats['negative'] += 1
            elif -1 < polarity <= -0.6:
                count_stats['snegative'] += 1

            results.append({'tweet_id': tweet_id, 'text': text, 'clean_text': clean_text, 'tweet_time': time,
                            'polarity': polarity})

        # finding average of how people are reacting
        final_stats['positive'] = self.percentage(count_stats['positive'], n_tweets)
        final_stats['wpositive'] = self.percentage(count_stats['wpositive'], n_tweets)
        final_stats['spositive'] = self.percentage(count_stats['spositive'], n_tweets)
        final_stats['negative'] = self.percentage(count_stats['negative'], n_tweets)
        final_stats['wnegative'] = self.percentage(count_stats['wnegative'], n_tweets)
        final_stats['snegative'] = self.percentage(count_stats['snegative'], n_tweets)
        final_stats['neutral'] = self.percentage(count_stats['neutral'], n_tweets)

        # finding average reaction
        final_stats['polarity'] = count_stats['polarity'] / n_tweets

        if final_stats['polarity'] == 0:
            final_stats['total_polarity'] = "Neutral"
        elif 0 < final_stats['polarity'] <= 0.3:
            final_stats['total_polarity'] = "Weakly Positive"
        elif 0.3 < final_stats['polarity'] <= 0.6:
            final_stats['total_polarity'] = "Positive"
        elif 0.6 < final_stats['polarity'] <= 1:
            final_stats['total_polarity'] = "Strongly Positive"
        elif -0.3 < final_stats['polarity'] <= 0:
            final_stats['total_polarity'] = "Weakly Negative"
        elif -0.6 < final_stats['polarity'] <= -0.3:
            final_stats['total_polarity'] = "Negative"
        elif -1 < final_stats['polarity'] <= -0.6:
            final_stats['total_polarity'] = "strongly Negative"

        print(results)
        sentiment_data = pd.DataFrame.from_records(results)
            # Insert to DB

        print(f"Count Stats: {count_stats}")
        print(f"Final Stats: {final_stats}")
        return sentiment_data, final_stats

    def predict(self, text):
        analysis = TextBlob(text)

        polarity = analysis.sentiment.polarity
        return polarity

    def insert_into_db(self, sentiment_data, stats):
        # Removing duplicate insertion of tweets into the DB
        tweets_table = config['DATABASE']['tweets_table']
        stats_table = config['DATABASE']['statistics_table']
        sentiment_data.to_sql(tweets_table, engine, if_exists='append', index=False)

        stats = pd.DataFrame([stats])
        stats.to_sql(stats_table, engine, if_exists='append', index=False)

    def plotPieChart(self, stats):
        figure = plt.figure()
        positive, wkpositive, stpositive = stats['positive'], stats['wpositive'], stats['spositive']
        negative, wknegative, stnegative = stats['negative'], stats['wnegative'], stats['snegative']
        neutral = stats['neutral']
        labels = ['Positive [' + str(positive) + '%]', 'Weakly Positive [' + str(wkpositive) + '%]',
                  'Strongly Positive [' + str(stpositive) +
                  '%]', 'Neutral [' + str(neutral) + '%]',
                  'Negative [' + str(negative) +
                  '%]', 'Weakly Negative [' + str(wknegative) + '%]',
                  'Strongly Negative [' + str(stnegative) + '%]']
        sizes = [positive, wkpositive, stpositive,
                 neutral, negative, wknegative, stnegative]
        colors = ['lightcoral', 'deepskyblue', 'lightpink',
                  'royalblue', 'red', 'lightsalmon', 'darkred']
        patches, texts = plt.pie(sizes, colors=colors, startangle=90)
        plt.legend(patches, labels, loc="best")
        plt.axis('equal')
        plt.tight_layout()
        strFile = "static/image/pie_chart.png"
        if os.path.isfile(strFile):
            os.remove(strFile)  # Opt.: os.system("rm "+strFile)
        plt.savefig(strFile)
        # plt.show()



