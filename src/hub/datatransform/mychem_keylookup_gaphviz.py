#!/usr/bin/env python
# coding: utf-8

import sys
sys.path.append("../../")

import networkx as nx
import pydot

from keylookup import graph_mychem


graph = nx.drawing.nx_pydot.to_pydot(graph_mychem)
svg_file = graph.create_svg()

with open('mychem_graph.svg', 'wb') as svg:
    svg.write(svg_file)
