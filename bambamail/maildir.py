import os, tempfile, time
from pathlib import Path
from .newmailmessage import NewMailMessage
from .config import config

class Maildir:
    ''' Maildir++ manager '''

    @staticmethod
    def create_maildir():
        # Creamos los directorios del maildir, por si acaso
        for path in "new", "cur", "tmp", "eml":
            os.makedirs(Path(config.maildir_path, path), exist_ok = True)

    def new_message(self, message_headers: dict[str, str]) -> NewMailMessage:
        ''' Creates a new mail message file '''
        return NewMailMessage(config.maildir_path, message_headers)
