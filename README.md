# StickyBot

##### A Slack bot that stickies Reddit posts from Slack commands.

This bot was created for the r/GlobalOffensive Match Thread team to allow them the ability to sticky threads if certain criteria was met first.

[](https://i.imgur.com/oTiT1aa.png)

### Requirements
* [Python 3](https://www.python.org/downloads/)
* [SlackClient](https://github.com/slackapi/python-slackclient) - Official Slack Python library. Install with `pip install slackclient`
* [Praw 4.5+](https://praw.readthedocs.io/en/latest/) - Python wrapper for the Reddit API

### Setup
First, you'll need to [create a bot user](https://my.slack.com/services/new/bot) in your slack for StickyBot and add the integration to your team. 
Make sure you save it with the name 'stickybot' or you'll need to change the `BOT_NAME` variable in the `get_bot_id` script later. Once your new bot 
has been created, copy the API token and add it to `settings.json` on line 3. 

With the bot added to your Slack team, run the script in the tests folder named `get_bot_id`. You'll need to edit the bots API token into line 7. 
When this completes, you should be given the user ID for your bot. It will look something like `U01234567`. Copy that and add it to line 4 in settings.json

To get your Reddit API credentials, log into the Reddit account you wish to authenticate with the bot, and go to preferences>apps and create a new 'SCRIPT' app.
You can leave the 'about URL' blank and provide `http://localhost/reddit-oauth` for the redirect URI. The client_id will be underneath your new app name, and the
client_secret will be next to the `secret` field. Copy those and paste them on lines 14 & 15 in `settings.json`, then include your user/pass and the name of the 
subreddit the bot will be stickying to. 

You can store the bots user ID in the 'users' section of `settings.json`.

### Usage
StickyBot accepts two commands. You can either mention him with `@stickybot` or use `!sticky`. Either option needs to be done at the start of your message.

E.g. `!sticky https://www.reddit.com/r/GlobalOffensive/comments/6ai5j6/newbie_thursday_11th_of_may_2017_your_weekly/`

The bot will first make sure the message was sent from an approved user, then will proceed to validate the URL. If there aren't already 2 stickies on the 
subreddit, it will sticky the post and return a success message in chat. Otherwise, it will reject and say he's very sorry. If you screw up the link and StickyBot
can't validate it, however, he may not be so nice. 

For the purposes of r/GlobalOffensive, the bot will also make sure that if 1 sticky does already exist, the request to sticky a post isn't coming less than 6 
hours from the time that a weekly, scheduled sticky should go live.
