# StickyBot

##### A Slack bot that stickies Reddit posts from Slack commands.

This bot was created for the r/GlobalOffensive Match Thread team to allow them the ability to sticky threads if certain criteria was met first.

![StickyBot](http://i.imgur.com/PLhIz8K.png)

### Requirements
* [Python 3](https://www.python.org/downloads/)
* [SlackClient](https://github.com/slackapi/python-slackclient) - Official Slack Python library. Install with `pip install slackclient`
* [Praw 4.5+](https://praw.readthedocs.io/en/latest/) - Python wrapper for the Reddit API

### Setup
First, you'll need to [create a bot user](https://my.slack.com/services/new/bot) in your slack for StickyBot and add the integration to your team. 
**Make sure you save it with the name 'stickybot' or you'll need to change the `BOT_NAME` variable in the `get_bot_id` script later.**

Once your new bot has been created, follow these steps:

1) Copy the bots API token and add it to `settings.json` on line 3
2) Run `get_bot_id.py` from the `tests` folder, replacing 'SLACK_BOT_TOKEN' on line 7 with the API token. It will look something like `U01234567`
3) Add the UserID returned from `get_bot_id.py` to `settings.json` on line 4
4) Run `get_bot_id.py` again, replacing `BOT_NAME` on line 5 with the slack name of the user that will be given permission to use stickybot
5) Add the users ID to `settings.json` under the `users` section. The example names of "John", "Jane" can be whatever you like to distinguish the user(s).
 * To clarify, the name(s) and user ID(s) listed in the `users` section of `settings.json` represent people authorized to use stickybot. Anyone not listed here will be rejected.
6) Fill out the `reddit` section of `settings.json` with the relevant Reddit and Reddit API information (see `Reddit API info` below if this is unfamiliar to you)
7) Add a list of **Reddit** usernames that should be allowed to unsticky a post to line 17 of `settings.json`
8) If you wish to use `call_home`, set it to true on line 18 of `settings.json`, and add the slack channel name to announce on line 19. In my case, stickybot sits in the MatchThread 
teams' Slack (separate from our mod team). This alerts us when one of the Match Thread guys uses stickybot so that we can check it.

### Reddit API Info
To get your Reddit API credentials, log into the Reddit account you wish to authenticate with the bot, and go to preferences>apps and create a new **'SCRIPT'** app.
You can leave the 'about URL' blank. For the redirect URI, just give `http://localhost/reddit-oauth`. 

The client_id will be underneath your new app name, and the client_secret will be next to the `secret` field. [Client_ID Example](https://imgur.com/n3dKYcF)

Copy those and paste them on lines 14 & 15 in `settings.json`, then include your user/pass and the name of the subreddit the bot will be stickying to. 

### Usage
StickyBot will either sticky or unsticky a post. 

**To sticky,** you can either mention him with `@stickybot` or use `!sticky`. Either option needs to be done at the start of your message.

E.g. `!sticky https://www.reddit.com/r/GlobalOffensive/comments/6ai5j6/newbie_thursday_11th_of_may_2017_your_weekly/`

**To UN-sticky** you must not include an @ mention, but rather use the following format: `!unsticky <link_url>`. Including `@stickybot` before `!unsticky` won't work.

The bot will first make sure the message was sent from an approved user, then will proceed to validate the URL. If there aren't already 2 stickies on the 
subreddit, it will sticky the post and return a success message in chat. Otherwise, it will reject and say he's very sorry. If you screw up the link and StickyBot
can't validate it, however, he may not be so nice. 

For the purposes of r/GlobalOffensive, the bot will also make sure that if 1 sticky does already exist, the request to sticky a post isn't coming less than 6 
hours from the time that a weekly, scheduled sticky should go live.

For unstickying, it also validates the URL and makes sure it's already stickied, but will make sure the author of the post to be unstickied is listed in `unsticky_authors` from `settings.json`.
