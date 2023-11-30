from api import Media
from api import DataType

import datetime

class Logger(object):
    log_file = None

    def __init__(self, log_filename: str):
        self.log_file = open(log_filename, 'a')

    def log_action(self, action: str):
        self.log_file.write(f"{datetime.datetime.now()} - {action}" + '\n')
        self.log_file.flush()

    def log_failed_action(self, action: str):
        self.log_file.write(f"{datetime.datetime.now()} - failed to {action}" + '\n')
        self.log_file.flush()

    def log_extracted(self, extracted_type: DataType, username):
        self.log_file.write(f"{datetime.datetime.now()} - extracted {extracted_type} from user {username}" + '\n')
        self.log_file.flush()

    def log_like(self, media: Media):
        self.log_file.write(f"{datetime.datetime.now()} - liked media {media.media_id}" + '\n')
        self.log_file.flush()

    def log_comment(self, media: Media, comment: str):
        self.log_file.write(f"{datetime.datetime.now()} - commented {comment} on media {media.media_id}" + '\n')
        self.log_file.flush()

    def log_follow(self, username: str):
        self.log_file.write(f"{datetime.datetime.now()} - followed user {username}" + '\n')
        self.log_file.flush()

    def log_unfollow(self, username: str):
        self.log_file.write(f"{datetime.datetime.now()} - unfollowed user {username}" + '\n')
        self.log_file.flush()