CKAN Tagger
============

The idea of the CKAN tagger is to add tags to certain datasets and/or results of search queries.
Have a look at the example YAML config (`example.yml`) in this directory to see how to configure the tagger.

The tagger should be run regularly using something like cron or GitHub Actions.

This script was created as a easy way to tag datasets across multiple harvesters with a common topic.
Usually this kind of tagging is used temporary to group together datasets for an event like a hackathon.

It must be run regularly as otherwise the harvesters running in the background would overwrite the tags from their source.
Ideally the tags would already be defined in the source, but this is not always possible (think Geoportal) so therefore this script provides a band-aid.

## Usage

```
python tagger.py -c config.yml
```

This script makes use of dotenv (i.e. environment variables) to determine which CKAN instance it should connect to.

