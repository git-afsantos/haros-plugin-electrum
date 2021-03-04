# -*- coding: utf-8 -*-

# SPDX-License-Identifier: MIT
# Copyright © 2021 André Santos

###############################################################################
# Imports
###############################################################################

from __future__ import unicode_literals


################################################################################
# Plugin Entry Point
################################################################################

def configuration_analysis(iface, config):
    if (not config.launch_commands or len(config.nodes.enabled) < 2
            or not config.hpl_properties):
        return
    settings = config.user_attributes.get('haros_plugin_electrum', {})
    try:
        _validate_settings(iface, settings)
    except PluginSettingsError as e:
        iface.log_error(e.message)

def _validate_settings(iface, settings):
    jar = settings.get('jar')
    if not jar:
        raise PluginSettingsError.missing_jar()
    if not isinstance(jar, dict):
        raise PluginSettingsError.jar_not_dict()
    if not 'path' in jar and not 'env' in jar:
        raise PluginSettingsError.missing_jar_path()


################################################################################
# Data Structures
################################################################################

class PluginSettingsError(Exception):
    @classmethod
    def missing_jar(cls):
        return cls('missing `jar` field in plugin settings')

    @classmethod
    def jar_not_dict(cls):
        return cls('expected a dictionary under the `jar` setting')

    @classmethod
    def missing_jar_path(cls):
        return cls('missing .jar path; expected one of `jar:path` or `jar:env`')
