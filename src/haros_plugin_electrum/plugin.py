# -*- coding: utf-8 -*-

# SPDX-License-Identifier: MIT
# Copyright © 2021 André Santos

###############################################################################
# Imports
###############################################################################

from __future__ import unicode_literals
import os

from .analyzer import model_check
from .electrum2haros import parse_output, render_result
from .haros2electrum import config2model, render_model


################################################################################
# Plugin Entry Point
################################################################################

def configuration_analysis(iface, config):
    if (not config.launch_commands or len(config.nodes.enabled) < 2
            or not config.hpl_properties):
        return
    settings = config.user_attributes.get('haros_plugin_electrum', {})
    try:
        _validate_settings(settings)
    except PluginSettingsError as e:
        iface.log_error(e.message)
    jar_path = _get_jar_path(settings)
    try:
        model = config2model(config)
        ele_src = render_model(model)
        output = model_check(jar_path, ele_src)
        result = parse_output(output, config)
        html = render_result(result)
        iface.report_runtime_violation('counterexample', html, result.resources)
    except Exception as e:
        iface.log_error(e.message)


def _validate_settings(settings):
    jar = settings.get('jar')
    if not jar:
        raise PluginSettingsError.missing_jar()
    if not isinstance(jar, dict):
        raise PluginSettingsError.jar_not_dict()
    if not 'path' in jar and not 'env' in jar:
        raise PluginSettingsError.missing_jar_path()
    if 'env' in jar and not os.environ.get(jar['env']):
        raise PluginSettingsError.missing_env_var(jar['env'])

def _get_jar_path(settings):
    jar = settings['jar']
    path = jar.get('path')
    if path is None:
        env_var = jar['env']
        path = os.environ[env_var]
    return path


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

    @classmethod
    def missing_env_var(cls, var):
        return cls("missing '{}' env. variable with .jar path".format(var))
