#!/bin/bash

files=$(find data/*)
# files='/data/tweets/geoTwitter21-01-01.zip

time for file in $files; do
	python3 -u load_tweets_batch.py --db=postgresql://hello_flask:hello_flask@localhost:1368/hello_flask_dev --inputs $file
done
