# System imports
import logging
import time
import websocket
# Third party imports
from slackclient import SlackClient
# Project imports
import reddit
import call_home
from config import cfg

logging.basicConfig(filename='logging.log', level=logging.ERROR)
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
        logging.INFO('StickyBot has begun. Total word domination will begin soon...')
        while True:
            try:
                cmd, channel, user = parser(slack_client.rtm_read())
                if cmd and channel and user:
                    handle(cmd, channel, user)
                time.sleep(SOCKET_READ_DELAY)
            except (websocket.WebSocketConnectionClosedException, TimeoutError) as e:
                logging.ERROR('Error! {0}'.format(e))
                time.sleep(10)
                break

        firehose()
    else:
        logging.ERROR('Could not connect to slack..make sure your bot token is correct.')
        time.sleep(10)
        firehose()


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

    if user in settings['users'].values():
        if command.startswith(BOT_CMD_UNSTICKY):
            link = command.split(BOT_CMD_UNSTICKY)[1].strip().lower()
            url = link.strip('<>')
            unsticky_id = sticky_bot.validate_unsticky(url)
            if unsticky_id:
                if sticky_bot.unsticky(unsticky_id):
                    logging.INFO('Unstickied!')
                    post_message(channel, unstickied)
                    return
                else:
                    logging.WARNING('Un-sticky failed!')
                    post_message(channel, unsticky_failed)
                    return
            else:
                logging.WARNING('Un-sticky validation failed!')
                post_message(channel, unsticky_val_failed)
                return

        link = command.strip('<>')
        post_id = sticky_bot.validate(link)
        if post_id:
            if sticky_bot.is_sticky_safe():
                if sticky_bot.sticky(post_id):
                    logging.INFO('Stickied!')
                    post_message(channel, success)
                    if settings['call_home']:
                        call_home.sendAlert(link)
                    return
                else:
                    logging.WARNING('Sticky failed!')
                    post_message(channel, unknown)
                    return
            else:
                logging.WARNING('Not safe to sticky.')
                post_message(channel, not_safe)
                return
        else:
            logging.WARNING('Validation failed.')
            post_message(channel, val_failed)
            return
    else:
        post_message(channel, default)
        return


def post_message(channel, text, as_user=False, icon_emoji=':stickybot:', username='stickybot'):
    slack_client.api_call('chat.postMessage',
                          channel=channel,
                          text=text,
                          as_user=as_user,
                          icon_emoji=icon_emoji,
                          username=username)


if __name__ == "__main__":
    firehose()

