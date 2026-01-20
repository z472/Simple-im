from unittest import TestCase
from sample.tornadoconn.tornadoserver import start_tserver


class TornadoServer(TestCase):
    async def setUp(self):
        start_tserver()