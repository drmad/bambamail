import os, tempfile, time, re
from typing import TextIO
from pathlib import Path

class NewMailMessage:
    ''' Creates a new mail message file.

    First, creates a new file in `tmp`, then moves it to `new`.
    Also, a hardlink for the message is created in `eml`. '''

    # Maildir path
    maildir_path: str

    # Maildir headers,
    message_headers: dict[str, str]

    # New message file name
    filename: str

    # File object to a new message being created
    fileobject: TextIO

    def __init__(self, maildir_path: str, message_headers: dict[str, str]):
        self.maildir_path = maildir_path
        self.message_headers = message_headers

        fd, filename = tempfile.mkstemp(
            prefix = str(time.time()) + '.',
            dir = Path(self.maildir_path, 'tmp')
        )

        self.filename = filename
        self.fileobject = os.fdopen(fd, 'w')

    def write(self, line):
        ''' Adds a line to the mail message file '''
        self.fileobject.write(line + '\n')

    def close(self):
        ''' Closes the file, moves to `new`, creates a hardlink to an .EML file '''
        self.fileobject.close()

        target_path = Path(self.maildir_path, 'new', os.path.basename(self.filename))
        os.rename(
            self.filename,
            target_path
        )

        # Generamos el nombre del fichero a partir de 'to' y 'subject's.
        to = re.sub(r'\W+', '_', self.message_headers['to'])
        subject = re.sub(r'\W+', '_', self.message_headers['subject'])
        eml_filename = str(time.time()) + '-' + to + '-' + subject + '.eml'

        os.link(target_path, Path(self.maildir_path, 'eml', eml_filename))
