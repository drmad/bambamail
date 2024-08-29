from .config import config
from bambamail.bambaserver import BambaServer, ReusableTCPServer
from typing import Optional


def run():

    server_addr = config.host, config.port

    with ReusableTCPServer(server_addr, BambaServer) as server:
        server.serve_forever()
