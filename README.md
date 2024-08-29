# BambaMail

BambaMail is a simple and portable fake SMTP server. You can use it when developing an app which requires to send emails, but you don't want to setup a complete one, or use one in the cloud.

BambaMail saves any email received in a [Maildir](https://en.wikipedia.org/wiki/Maildir) directory (default `.Maildir`). 

## Installation and usage

Install BambaMail using  [`pipx`](https://github.com/pypa/pipx):

```bash
pipx install bambamail
```

