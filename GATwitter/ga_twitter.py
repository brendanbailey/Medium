import twitter #http://python-twitter.readthedocs.io/en/latest/twitter.html
import pandas as pd
import sqlalchemy
import datetime
import mysql

CONSUMER_KEY = 
CONSUMER_SECRET =
OATH_TOKEN =
OAUTH_TOKEN_SECRET =
DB_USER_NAME =
DB_PASSWORD =
DB_HOST =
DB_NAME =
def get_max_id():
    engine = sqlalchemy.create_engine("mysql://%s:%s@%s/%s" % (DB_USER_NAME, DB_PASSWORD, DB_HOST, DB_NAME))
    max_id = int(pd.read_sql("SELECT MAX(tweet_id) from tweets AS MAX_ID", engine).iloc[0])
    return max_id


def collect_twitter_data(count = None, since_id = None):
    twitter_api = twitter.Api(consumer_key = CONSUMER_KEY, consumer_secret = CONSUMER_SECRET, access_token_key = OATH_TOKEN, access_token_secret= OAUTH_TOKEN_SECRET)

    #GA Location List https://twitter.com/GA/lists/ga-locations/members
    twitter_data = twitter_api.GetListTimeline(slug="ga-locations", owner_screen_name="GA", count = count, since_id = since_id) #since_id

    if twitter_data != []:
        tweet_list = []
        hash_tag_list = []
        mention_list = []
        url_list = []
        for status in twitter_data:
            tweet = status.AsDict()
            tweet_list.append({"tweet_id": tweet["id_str"], "user_id": tweet["user"]["id"], "user_screen_name": tweet["user"]["screen_name"], "source": tweet["source"], "text": tweet["text"], "created_at": tweet["created_at"]})
            if tweet["hashtags"] != []:
                for hash_tag in tweet["hashtags"]:
                    hash_tag_list.append({"tweet_id": tweet["id_str"], "text": hash_tag["text"]})
            if tweet["user_mentions"] != []:
                for user_mention in tweet["user_mentions"]:
                    mention_list.append({"tweet_id": tweet["id_str"], "mentioned_id": user_mention["id"], "mentioned_screen_name": user_mention["screen_name"]})
            if tweet["urls"] != []:
                for url in tweet["urls"]:
                    url_list.append({"tweet_id": tweet["id_str"], "url": url["url"], "expanded_url": url["expanded_url"]})

        tweet_df = pd.DataFrame.from_dict(tweet_list)
        tweet_df['created_at'] = pd.to_datetime(tweet_df.created_at)
        tweet_df['text']=tweet_df.text.apply(lambda x: x.encode('ascii', 'ignore'))
        hash_tag_df = pd.DataFrame(hash_tag_list)
        mention_df = pd.DataFrame(mention_list)
        url_df = pd.DataFrame(url_list)

        print "Data from Twitter API Collected"
        return {"tweets": tweet_df, "hash_tags": hash_tag_df, "mentions" : mention_df, "urls" : url_df}
    else:
        return twitter_data

def load_data_to_sql(df_dict):
    engine = sqlalchemy.create_engine("mysql://%s:%s@%s/%s" % (DB_USER_NAME, DB_PASSWORD, DB_HOST, DB_NAME))
    complete_report = open("reports/complete_report_%s.txt" %  datetime.datetime.now().strftime("%Y%m%d_%H%M%S"), "w")
    for key in df_dict:
        df_dict[key].to_sql(key, engine, if_exists = "append")
        complete_report.write("%s: %s\n" % (key, len(df_dict[key])))
    complete_report.close()
    print "Twitter Data Loaded"

try:
    max_id = get_max_id()
    df_dict = collect_twitter_data(count = 200, since_id = max_id)
    if df_dict == []:
        report = open("reports/complete_report_%s.txt" %  datetime.datetime.now().strftime("%Y%m%d_%H%M%S"), "w")
        report.write("No new tweets\n")
        report.close()
        print "No new tweets"
    else:
        load_data_to_sql(df_dict)
except Exception as detail:
    report = open("reports/error_report_%s.txt" % datetime.datetime.now().strftime("%Y%m%d_%H%M%S"), "w")
    print detail
    report.write(str(detail))
