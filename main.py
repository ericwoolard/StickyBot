# System imports
import time
# Third party imports
from slackclient import SlackClient
# Project imports
import reddit
from config import cfg

settings = cfg.readJson('settings.json')

# Bot constants
BOT_NAME = 'stickybot'
BOT_ID = settings['stickybot']['bot_id']
BOT_CALL = '<@{}>'.format(BOT_ID)
BOT_CMD = '!sticky'

slack_client = SlackClient(settings['stickybot']['token'])
SOCKET_READ_DELAY = 1

# Setup the reddit object for StickyBot
sticky_bot = reddit.Reddit()
sticky_bot.get_praw_instance()


def firehose():
    if slack_client.rtm_connect():
        print('StickyBot has begun. Total word domination will begin soon...')
        while True:
            cmd, channel, user = parser(slack_client.rtm_read())
            if cmd and channel and user:
                handle(cmd, channel, user)
            time.sleep(SOCKET_READ_DELAY)
    else:
        print('Could not connect to slack..make sure your bot token is correct.')


def parser(rtm_out):
    """
        This function returns null unless a message is found that either calls
        the bot directly, or uses the !sticky command.
    """
    rtm_list = rtm_out
    if rtm_list and len(rtm_list) > 0:
        for data in rtm_list:
            if data and 'text' in data and 'user' in data:
                if BOT_CALL in data['text']:
                    # split text after the @ mention
                    msg = data['text'].split(BOT_CALL)[1].strip().lower()
                    return msg, data['channel'], data['user']
                elif data['text'].startswith(BOT_CMD):
                    msg = data['text'].split(BOT_CMD)[1].strip().lower()
                    return msg, data['channel'], data['user']
    return None, None, None


def handle(command, channel, user):
    """
        If the parser function finds a correct bot call or !sticky command,
        firehose() will pass the link and channel ID to this function, where
        the link will be validated and then stickied if it passes the check.
    """
    success = 'Roger that! I\'ve stickied your post successfully :)'
    unknown = 'Uh oh...something went wrong. You\'ll need to alert my master!'
    not_safe = 'Whoops...Looks like there\'s already two stickies up, or you\'re less than 6 hours from a scheduled sticky going live :('
    val_failed = 'Look, dammit. I can\'t sticky something if you fuck up the URL. Get it right and then come talk to me.'
    default = 'Uhh...who tf is this guy?'

    if user != settings['users']['YOUR_USERID']:
        slack_client.api_call("chat.postMessage", channel=channel, text=default, as_user=True)
    elif user == settings['users']['YOUR_USERID']:
        link = command.strip('<>')
        post_id = sticky_bot.validate(link)
        if post_id:
            if sticky_bot.is_sticky_safe():
                if sticky_bot.sticky(post_id):
                    print('Stickied!')
                    slack_client.api_call("chat.postMessage", channel=channel, text=success, as_user=True)
                    return
                else:
                    print('Sticky failed!')
                    slack_client.api_call("chat.postMessage", channel=channel, text=unknown, as_user=True)
                    return
            else:
                print('Not safe to sticky.')
                slack_client.api_call("chat.postMessage", channel=channel, text=not_safe, as_user=True)
                return
        else:
            print('Validation failed.')
            slack_client.api_call("chat.postMessage", channel=channel, text=val_failed, as_user=True)
            return


if __name__ == "__main__":
    firehose()

