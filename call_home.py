import requests
import traceback
from slackclient import SlackClient
from datetime import datetime
from config import cfg


settings = cfg.readJson('settings.json')
slack_client = SlackClient(settings['stickybot']['token'])

def sendAlert(url):
    message = '<!here> *HEYO!* Someone just used me to sticky a post on r/{}. I hope it was okay... Will you check for me? :sadsmiley: \n{}'.format(settings['reddit']['subreddit'], url)
    try:
        slack_client.api_call("chat.postMessage", channel=settings['call_home_channel'], text=message, as_user=False, icon_emoji=':stickybot:', username='stickybot')
    except:
        req_error = traceback.format_exc()
        now = str(datetime.now())
        print(now + ' - Error:\n' + req_error + '\n\n\n')
