
\set ON_ERROR_STOP on

BEGIN;
CREATE TABLE users (
    id_users BIGINT PRIMARY KEY,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ,
    urls TEXT,
    friends_count INTEGER,
    listed_count INTEGER,
    favourites_count INTEGER,
    statuses_count INTEGER,
    protected BOOLEAN,
    verified BOOLEAN,
    screen_name TEXT,
    name TEXT,
    password TEXT,
    location TEXT,
    description TEXT,
    withheld_in_countries VARCHAR(2)[]
);

CREATE TABLE tweets (
    id_tweets BIGINT PRIMARY KEY,
    id_users BIGINT,
    created_at TIMESTAMPTZ,
    in_reply_to_status_id BIGINT,
    in_reply_to_user_id BIGINT,
    quoted_status_id BIGINT,
    retweet_count SMALLINT,
    favorite_count SMALLINT,
    quote_count SMALLINT,
    withheld_copyright BOOLEAN,
    withheld_in_countries VARCHAR(2)[],
    source TEXT,
    text TEXT,
    country_code VARCHAR(2),
    state_code VARCHAR(2),
    lang TEXT,
    place_name TEXT
);

CREATE TABLE tweet_urls (
    id_tweets BIGINT,
    urls TEXT,
    PRIMARY KEY (id_tweets, urls)
);

COMMIT;
