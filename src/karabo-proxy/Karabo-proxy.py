#############################################################################
# Author: degon
#
# Created on June 25, 2024, 04:34 PM
# from template 'minimal middlelayer' of Karabo 2.20.1.dev26+gb8be1dc2c.d20240620
#
# This file is intended to be used together with Karabo:
#
# http://www.karabo.eu
#
# IF YOU REQUIRE ANY LICENSING AND COPYRIGHT TERMS, PLEASE ADD THEM HERE.
# Karabo itself is licensed under the terms of the MPL 2.0 license.
#############################################################################

from karabo.middlelayer import Device, Slot, String

from ._version import version as deviceVersion


class Karabo-proxy(Device):
    __version__ = deviceVersion

    greeting = String()

    @Slot()
    async def hello(self):
        self.greeting = "Hello world!"

    def __init__(self, configuration):
        super().__init__(configuration)

    async def onInitialization(self):
        """ This method will be called when the device starts.

            Define your actions to be executed after instantiation.
        """
