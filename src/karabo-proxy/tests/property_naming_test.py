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
import karabo-proxy


def test_property_code_guideline():
    """Test that all properties and slots follow common code style"""
    from karabo.middlelayer.testing import check_device_package_properties
    keys = check_device_package_properties(karabo-proxy)
    msg = ("The key naming does not comply with our coding guidelines. "
           f"Please have a look at (class: paths): {keys}")
    assert not keys, msg
