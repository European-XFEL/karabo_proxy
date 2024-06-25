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


def test_import_sub_modules():
    """Check the device package for forbidden subimports"""
    from karabo.common.api import has_sub_imports
    from karabo.middlelayer.testing import get_ast_objects
    ignore = ["karabo.middlelayer.testing"]
    ast_objects = get_ast_objects(karabo-proxy)
    for ast_obj in ast_objects:
        assert not len(has_sub_imports(ast_obj, "karabo.middlelayer", ignore))
