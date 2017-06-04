# System imports
import time
# Third party imports
from slackclient import SlackClient
# Project imports
import reddit
import call_home
from config import cfg

settings = cfg.readJson('settings.json')

# Bot constants
BOT_NAME = 'stickybot'
BOT_ID = settings['stickybot']['bot_id']
BOT_CALL = '<@{}>'.format(BOT_ID)
BOT_CMD = '!sticky'
BOT_CMD_UNSTICKY = '!unsticky'

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
                elif data['text'].startswith(BOT_CMD_UNSTICKY):
                    msg = data['text'].lower()
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
    unstickied = 'You got it! The post has been unstickied.'
    unsticky_val_failed = 'Hmm...I couldn\'t find a current sticky matching the link you gave me.'
    unsticky_failed = 'For some reason, I just...couldn\'t figure out how to unsticky this post...please forgive me? :\'('

    if user == settings['users']['John'] or user == settings['users']['Jane']:
        if command.startswith(BOT_CMD_UNSTICKY):
            link = command.split(BOT_CMD_UNSTICKY)[1].strip().lower()
            url = link.strip('<>')
            unsticky_id = sticky_bot.validate_unsticky(url)
            if unsticky_id:
                if sticky_bot.unsticky(unsticky_id):
                    print('Unstickied!')
                    slack_client.api_call("chat.postMessage", channel=channel, text=unstickied, as_user=False, icon_emoji=':stickybot:', username='stickybot')
                    return
                else:
                    print('Un-sticky failed!')
                    slack_client.api_call("chat.postMessage", channel=channel, text=unsticky_failed, as_user=False, icon_emoji=':stickybot:', username='stickybot')
                    return
            else:
                print('Un-sticky validation failed!')
                slack_client.api_call("chat.postMessage", channel=channel, text=unsticky_val_failed, as_user=False, icon_emoji=':stickybot:', username='stickybot')
                return

        link = command.strip('<>')
        post_id = sticky_bot.validate(link)
        if post_id:
            if sticky_bot.is_sticky_safe():
                if sticky_bot.sticky(post_id):
                    print('Stickied!')
                    slack_client.api_call("chat.postMessage", channel=channel, text=success, as_user=False, icon_emoji=':stickybot:', username='stickybot')
                    if settings['call_home']:
                        call_home.sendAlert(link)
                    return
                else:
                    print('Sticky failed!')
                    slack_client.api_call("chat.postMessage", channel=channel, text=unknown, as_user=False, icon_emoji=':stickybot:', username='stickybot')
                    return
            else:
                print('Not safe to sticky.')
                slack_client.api_call("chat.postMessage", channel=channel, text=not_safe, as_user=False, icon_emoji=':stickybot:', username='stickybot')
                return
        else:
            print('Validation failed.')
            slack_client.api_call("chat.postMessage", channel=channel, text=val_failed, as_user=False, icon_emoji=':stickybot:', username='stickybot')
            return
    else:
        slack_client.api_call("chat.postMessage", channel=channel, text=default, as_user=False, icon_emoji=':stickybot:', username='stickybot')
        return

if __name__ == "__main__":
    firehose()

