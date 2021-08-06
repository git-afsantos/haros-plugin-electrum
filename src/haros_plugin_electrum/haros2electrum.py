# -*- coding: utf-8 -*-

# SPDX-License-Identifier: MIT
# Copyright © 2021 André Santos

###############################################################################
# Imports
###############################################################################

from __future__ import unicode_literals
from builtins import object, str
from collections import namedtuple


###############################################################################
# Module Functions
###############################################################################

def config2model(config):
    builder = ModelBuilder()
    return builder.build_from_config(config)


def render_model(jinja, model, strip=True):
    template = jinja.get_template('model.ele.jinja')
    ele_src = template.render(model=model).encode('utf-8')
    if strip:
        ele_src = ele_src.strip()
    return ele_src


###############################################################################
# Data Structures
###############################################################################

Model = namedtuple('Model',
    ('nodes', 'topics', 'asserts'))

SigNode = namedtuple('SigNode',
    ('i', 'name', 'rosname', 'pubs', 'subs', 'facts'))

SigTopic = namedtuple('SigTopic',
    ('i', 'name', 'rosname'))


Operator = namedtuple('Operator', ('op', 'args'))

def Always(arg):
    return Operator('always', (arg,))

def Eventually(arg):
    return Operator('eventually', (arg,))

def Historically(arg):
    return Operator('historically', (arg,))

def Once(arg):
    return Operator('once', (arg,))


###############################################################################
# Model Builder
###############################################################################

class ModelBuilder(object):
    def __init__(self):
        self.topics = []
        self.nodes = []
        self._topic_map = {}
        self._predicates = {}

    def build_from_config(self, config):
        self.build_topics(config.topics.enabled)
        self.build_nodes(config.nodes.enabled)
        return Model(nodes, topics, [])

    def build_topics(self, topics):
        i = 1
        for topic in topics:
            if topic.rosname.is_unresolved:
                continue
            sig = self._topic2sig(i, topic)
            self.topics.append(sig)
            self._topic_map[topic.rosname.full] = sig
            i += 1
        return self.topics

    def build_nodes(self, nodes):
        i = 1
        for node in nodes:
            if node.rosname.is_unresolved:
                continue
            sig = self._node2sig(i, node)
            self.nodes.append(sig)
            i += 1
        return self.nodes

    def _topic2sig(self, i, topic):
        name = 'Topic' + str(i)
        rosname = topic.rosname.full
        return SigTopic(i, name, rosname)

    def _node2sig(self, i, node):
        name = 'Node' + str(i)
        rosname = node.rosname.full
        pubs = self._get_node_topic_links(node.publishers)
        subs = self._get_node_topic_links(node.subscribers)
        facts = self._get_node_behaviour(node)
        return SigNode(i, name, rosname, pubs, subs, facts)

    def _get_node_topic_links(self, links):
        sigs = []
        for link in links:
            if link.topic.rosname.is_unresolved:
                continue
            topic = self._topic_map[link.topic.rosname.full]
            sigs.append(topic.name)
        return sigs

    def _get_node_behaviour(self, node):
        axioms = []
        for hpl_property in node.node.hpl_properties:
            f = FormulaBuilder(hpl_property)
            axioms.append(f.formula)
        return axioms


###############################################################################
# Formula Builder
###############################################################################

class FormulaBuilder(object):
    def __init__(self, hpl_property):
        self.vars = {}
        self._var_msg_i = 0
        self._var_node_i = 0
        self._var_topic_i = 0
        self._var_value_i = 0
        self.formula = self._build(hpl_property)

    def _build(self, hpl_property):
        return self._build_scope(hpl_property.scope)

    def _build_scope(self, scope):
        if scope.is_global:
            pass
        elif scope.is_after:
            p = hpl.scope.activator
            f = Implies()
            f = Always()
        elif scope.is_until:
            q = hpl.scope.terminator
        elif scope.is_after_until:
            p = hpl.scope.activator
            q = hpl.scope.terminator
        else:
            raise ValueError('unknown scope: ' + str(scope))

    def _scope_after(self, p, pattern):
        # all x: Message | always {
        #   (p[x] and before
        #       ((no y: Message | p[y]) back-to (some y: Message | q[y])))
        #   implies pattern
        # }
        xs = [self._var_msg()]
        pre = self._event(p, x)
        post = self._pattern(pattern, x)
        f = Implies(pre, post)
        f = Always(f)
        return f

    def _enter_scope(self, p, q, xs):
        f_p = self._event(p, xs)
        f_nq = Not(Exists())

    def _hpl_pattern(self, pattern):
        return

    def _event(event, **kwargs):
        # TODO if disjunction

    def _var_msg(self):
        self._var_msg_i += 1
        return 'm' + str(self._var_msg_i)

    def _var_node(self):
        self._var_node_i += 1
        return 'n' + str(self._var_node_i)

    def _var_topic(self):
        self._var_topic_i += 1
        return 't' + str(self._var_topic_i)

    def _var_value(self):
        self._var_value_i += 1
        return 'v' + str(self._var_value_i)
