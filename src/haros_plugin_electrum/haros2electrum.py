# -*- coding: utf-8 -*-

# SPDX-License-Identifier: MIT
# Copyright © 2021 André Santos

###############################################################################
# Imports
###############################################################################

from __future__ import unicode_literals
from builtins import str
from collections import namedtuple


###############################################################################
# Module Functions
###############################################################################

def config2model(config):
    i = 1
    topics = []
    topics_by_name = {}
    for topic in config.topics.enabled:
        if topic.rosname.is_unresolved:
            continue
        sig = _topic2sig(i, topic)
        topics.append(sig)
        topics_by_name[topic.rosname.full] = sig
        i += 1

    i = 1
    nodes = []
    for node in config.nodes.enabled:
        if node.rosname.is_unresolved:
            continue
        sig = _node2sig(i, node, topics_by_name)
        nodes.append(sig)
        i += 1

    return Model(nodes, topics, [])


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


###############################################################################
# Helper Functions
###############################################################################

def _topic2sig(i, topic):
    name = 'Topic' + str(i)
    rosname = topic.rosname.full
    return SigTopic(i, name, rosname)

def _node2sig(i, node, topics_by_name):
    name = 'Node' + str(i)
    rosname = node.rosname.full
    pubs = _get_node_topic_links(node.publishers, topics_by_name)
    subs = _get_node_topic_links(node.subscribers, topics_by_name)
    facts = _get_node_behaviour(node, topics_by_name)
    return SigNode(i, name, rosname, pubs, subs, facts)

def _get_node_topic_links(links, topics_by_name):
    sigs = []
    for link in links:
        if link.topic.rosname.is_unresolved:
            continue
        topic = topics_by_name[link.topic.rosname.full]
        sigs.append(topic.name)
    return sigs

def _get_node_behaviour(node, topics_by_name):
    return []
