# System imports
import datetime
# Third-party imports
import praw, prawcore, praw.exceptions
from prawcore import exceptions
# Project import
from config import cfg

settings = cfg.readJson('settings.json')


class Reddit(object):
    def __init__(self):
        """
        Instantiates a Reddit object for StickyBot with default credentials.
        Override these if needed for derived classes.
        """
        # Default credentials for StickyBot's reddit object. Override if
        # needed for derived classes or multiple instances.
        self.user_agent = 'StickyBot - a slack bot implementation to sticky Reddit posts by u/zebradolphin5'
        self.client_id = settings['reddit']['client_id']
        self.client_secret = settings['reddit']['client_secret']
        self.username = settings['reddit']['username']
        self.password = settings['reddit']['password']
        self.r = self.get_praw_instance()
        self.subreddit = self.r.subreddit(settings['reddit']['subreddit'])

    def get_praw_instance(self):
        r = praw.Reddit(user_agent=self.user_agent,
                        client_id=self.client_id,
                        client_secret=self.client_secret,
                        username=self.username,
                        password=self.password)
        return r

    def validate(self, post_url):
        """
        Make sure the URL given to StickyBot actually exists and
        that it was submitted to our subreddit.
        :param post_url: URL for the post to be stickied
        :return: submission.id or None if not found
        """
        try:
            submission = self.r.submission(id=None, url=post_url)
            if submission.subreddit.display_name.lower() == self.subreddit:
                return submission.id
        except praw.exceptions.ClientException as e:
            print('Error during validate: {}'.format(e))
            return None
        except prawcore.exceptions.NotFound as e:
            print('Error during validate: {}'.format(e))
            return None

    def validate_unsticky(self, post_url):
        """
        Make sure the URL given to StickyBot to UN-sticky actually
        exists and is currently stickied.
        :param post_url: URL for the post to be UN-stickied
        :return: submission.id or None if not found
        """
        try:
            un_sticky_submission = self.r.submission(id=None, url=post_url)
            if un_sticky_submission.subreddit.display_name.lower() == self.subreddit and un_sticky_submission.stickied:
                return un_sticky_submission.id
        except praw.exceptions.ClientException as e:
            print('Error during validate: {}'.format(e))
        except prawcore.exceptions.NotFound as e:
            print('Error during validate: {}'.format(e))

        return None

    def is_sticky_safe(self):
        """
        Checks that two stickies don't already exist and that the
        requested post to sticky isn't less than 6 hours from a weekly
        scheduled sticky post.

        :return: True if safe
        """
        num = 0
        while num < 2:
            try:
                url = self.subreddit.sticky(num + 1).url
                num += 1
            except exceptions.NotFound as e:
                print('Sticky slot available for position {}'.format(num+1))
                break
        if num == 0:
            return True
        if num == 1:
            current_hour = datetime.datetime.today().hour
            current_day = datetime.datetime.today().weekday()
            if current_day == 1 and current_hour > 9:
                return False
            elif current_day == 2 or current_day == 5:
                if current_hour > 17:
                    return False
            return True
        return False

    def sticky(self, post_id):
        post = self.r.submission(post_id)
        try:
            post.mod.sticky(state=True, bottom=True)
        except:
            print('Sticky failed')
            return False
        return True

    def unsticky(self, post_id):
        post = self.r.submission(post_id)
        if post.author in settings['unsticky_authors']:
            try:
                post.mod.sticky(state=False)
                return True
            except:
                print('Unsticky failed!')

        return False
