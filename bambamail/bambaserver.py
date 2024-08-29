import socketserver, subprocess, re, quopri, base64
from typing import Optional, TextIO
from .maildir import Maildir
from .config import config
from .newmailmessage import NewMailMessage

class BambaServer(socketserver.StreamRequestHandler):
    new_message: Optional[NewMailMessage] = None
    ''' After DATA, this will have a NewMailMessage object'''

    reading_message_header: bool = False
    ''' True while data received are header lines. Should turn false after a blank line '''

    message_headers: dict[str, str] = {}
    ''' Mail headers from last message '''

    def write(self, data: str) -> None:
        data += "\n"
        self.wfile.write(data.encode())

    def helo(self, payload) -> str:
        return f"250 Hello there, {payload}"

    def mail(self, payload) -> str:
        return f'250 Ferpecto mi estimado'

    def rcpt(self, payload) -> str:
        return f'250 Teh ferpection'

    def data(self, payload) -> str:
        self.new_message = Maildir().new_message()
        self.reading_message_header = True
        return f'354 Ferpetto, mein Kumpel. Manda correo noma'

    def quit(self, payload) -> str:
        if config.execute_on_receive:
            pattern = re.compile(r'%(.+?)%')
            command = []
            for part in config.execute_on_receive:
                for m in pattern.finditer(part):
                    if m.group(1) in self.message_headers:
                        part = part.replace(m.group(0), self.message_headers[m.group(1)])

                command.append(part)

            subprocess.run(command)
        return f'221 Chaufa!'

    def decode_value(self, value) -> str:
        ''' Decode MIME-encoded 'words' if needed '''

        if match := re.match(r'=\?(.+?)\?(.)\?(.+?)\?=', value):
            charset = match.group(1).lower()
            encoding = match.group(2).lower()
            text = match.group(3)

            match(encoding):
                case 'b':
                    text = base64.b64decode(text).decode(charset)
                case 'q':
                    text = quopri.decodestring(text, header = True).decode(charset)

            value = text

        return value

    def handle(self):

        # Saludamos
        self.write("220 The SMTP")

        while True:
            data = self.rfile.readline().rstrip().decode()

            if self.new_message:
                if data == '.':
                    self.new_message.close()
                    self.write("250 Ferpekt, saved as " + self.new_message.filename)
                    self.new_message = None
                    continue

                self.new_message.write(data)

                # La primera línea en blanco
                if data == '':
                    self.reading_message_header = False

                if self.reading_message_header:
                    if data[0] == " ":
                        # name aun debe contener el último... name
                        self.message_headers[name] += data[1:]
                    else:
                        name, value = data.split(':', 1)
                        name = name.lower().strip()
                        self.message_headers[name] = self.decode_value(value.strip())

                continue

            command: str = data
            payload: Optional[str] = None

            # La primera palabra es el comando
            if ' ' in data:
                command, payload = data.split(' ', 1)

            # Debe existir en este objeto
            método = getattr(self, command.lower(), None)

            if not método or not callable(método):
                self.write(f'500 Command "{command}" not supported')
                continue

            self.write(método(payload))

            # Hack. El comando quit sale del bucle
            if command.lower() == 'quit':
                break

class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True
