# -*- coding: utf-8 -*-

# SPDX-License-Identifier: MIT
# Copyright © 2021 André Santos

###############################################################################
# Imports
###############################################################################

from __future__ import unicode_literals
import os

from jinja2 import Environment, PackageLoader

from .analyzer import model_check
from .electrum2haros import parse_output, render_result
from .haros2electrum import config2model, render_model


###############################################################################
# Plugin Entry Point
###############################################################################

PLUGIN = 'haros_plugin_electrum'

def configuration_analysis(iface, config):
    if (not config.launch_commands or len(config.nodes.enabled) < 2
            or not config.hpl_properties):
        return
    settings = config.user_attributes.get(PLUGIN, {})
    try:
        _validate_settings(settings)
    except PluginSettingsError as e:
        iface.log_error(e.message)
    jar_path = _get_jar_path(settings)
    scopes = _get_scopes(settings)
    jinja = Jinja()
    try:
        model = config2model(config)
        ele_src = render_model(jinja, model)
        filename = 'model_{}.ele'.format('_'.join(config.name.split()))
        with open(filename, 'w') as f:
            f.write(ele_src)
            f.write('\n')
        iface.export_file(filename)
        output = model_check(jar_path, ele_src, scopes)
        result = parse_output(output, config)
        html = render_result(jinja, result)
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
    scopes = settings.get('scope')
    if scopes:
        for key in ('time', 'msgs', 'values'):
            n = scopes.get(key)
            if n is not None and (not isinstance(n, int) or n < 0):
                raise PluginSettingsError.invalid_scope(key, n)

def _get_jar_path(settings):
    jar = settings['jar']
    path = jar.get('path')
    if path is None:
        env_var = jar['env']
        path = os.environ[env_var]
    return path

def _get_scopes(settings):
    scopes = settings.get('scope', {})
    if not 'time' in scopes:
        scopes['time'] = 10
    if not 'msgs' in scopes:
        scopes['msgs'] = 9
    if not 'values' in scopes:
        scopes['values'] = 4
    return scopes


###############################################################################
# Data Structures
###############################################################################

def Jinja():
    return Environment(
        loader=PackageLoader(PLUGIN, 'templates'),
        line_statement_prefix=None,
        line_comment_prefix=None,
        trim_blocks=True,
        lstrip_blocks=True,
        autoescape=False
    )

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

    @classmethod
    def invalid_scope(cls, key, n):
        return cls("invalid scope value for '{}': {}".format(key, n))
