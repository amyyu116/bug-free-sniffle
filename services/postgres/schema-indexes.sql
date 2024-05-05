CREATE EXTENSION rum;

CREATE INDEX rum_index_tweets_text ON tweets USING rum (text);
