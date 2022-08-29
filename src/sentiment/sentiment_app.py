from flask import request, session, redirect
from sentiment.sentiments import SentimentAnalysis
from flask import Blueprint, render_template

sentiment_blueprint = Blueprint("sentiment_blueprint", __name__, static_folder="../static",
                                template_folder="../templates")

# render page when url is called
@sentiment_blueprint.route("/sentiment_analyzer")
def sentiment_analyzer():
    if 'user_id' in session:
        return render_template("sentiment_analyzer.html")
    else:
        return redirect("/")


@sentiment_blueprint.route('/visualize')
def visualize():
    if 'user_id' in session:
        return render_template("PieChart.html")
    else:
        return redirect("/")


@sentiment_blueprint.route('/sentiment_logic', methods=['POST', 'GET'])
def sentiment_logic():
    if 'user_id' in session:
        # get user input of keyword to search and number of tweets from html form.
        keyword = request.form.get('keyword')
        n_tweets = request.form.get('tweets')
        n_tweets = int(n_tweets)

        keyword = keyword.lower()
        print(f"Number of tweets is of Type: {type(n_tweets)}")

        # Location logic
        # location = request.form.get('location') # -> location: Delhi/Mumbai
        # Map location according to dictionary and get geo code

        # keyword = 'covid'
        # n_tweets = 100

        sa = SentimentAnalysis()
        api = sa.authorisation()
        tweets = sa.search_tweets(api, keyword, n_tweets)
        sentiment_data, final_stats = sa.process_tweets(tweets, n_tweets)
        sentiment_data['keyword'] = keyword
        # sentiment_data['location'] = [location] * len(keyword)
        # sentiment_data['location_geo_code'] = [location_geo_code] * len(keywords)
        final_stats['keyword'] = keyword
        final_stats['n_tweets'] = n_tweets
        # Update location when fetched
        # final_stats['location'] = location
        sa.insert_into_db(sentiment_data, final_stats)


        sa.plotPieChart(final_stats)

        return render_template('sentiment_analyzer.html',
                               polarity=final_stats['polarity'], htmlpolarity=final_stats['total_polarity'],
                               positive=final_stats['positive'], wpositive=final_stats['wpositive'],
                               spositive=final_stats['spositive'], negative=final_stats['negative'],
                               wnegative=final_stats['wnegative'], snegative=final_stats['snegative'],
                               neutral=final_stats['neutral'], keyword=final_stats['keyword'],
                               tweets=final_stats['n_tweets'])
    else:
        return redirect("/")
