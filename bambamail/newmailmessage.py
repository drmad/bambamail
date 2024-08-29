import os, tempfile, time
from typing import TextIO
from pathlib import Path

class NewMailMessage:
    ''' Creates a new mail message file in maildir/tmp, then moves to maildir/new '''

    # Maildir path
    maildir_path: str

    # New message file name
    filename: str

    # File object to a new message being created
    fileobject: TextIO

    def __init__(self, maildir_path):
        self.maildir_path = maildir_path

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
        ''' Closes the file, and moves to maildir/new '''
        self.fileobject.close()

        os.rename(
            self.filename,
            Path(self.maildir_path, 'new', os.path.basename(self.filename))
        )
