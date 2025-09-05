from typing import List, Tuple
from backend.models import Graph, Node, Edge, Text, BoundingBox
import numpy as np

def get_bbox_center(bbox: BoundingBox) -> Tuple[float, float]:
    return bbox.x + bbox.w / 2, bbox.y + bbox.h / 2

def calculate_distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def assemble_graph(
    symbols: List[Node],
    lines: List[Edge],
    junctions: List[Node],
    texts: List[Text]
) -> Graph:
    """
    Assembles the final process graph by associating text with symbols/lines
    and connecting lines to nodes.
    """
    graph = Graph(nodes=symbols + junctions, edges=lines, texts=texts)

    # --- Associate Text with Nodes and Edges ---
    unassigned_texts = list(texts)
    
    # 1. Assign to nodes (symbols and junctions)
    for node in graph.nodes:
        node_center = get_bbox_center(node.bbox)
        closest_text = None
        min_dist = float('inf')

        for text in unassigned_texts:
            text_center = get_bbox_center(text.bbox)
            dist = calculate_distance(node_center, text_center)
            
            # A simple threshold for association
            if dist < 100 and dist < min_dist:
                min_dist = dist
                closest_text = text
        
        if closest_text:
            node.tag = closest_text.content
            unassigned_texts.remove(closest_text)

    # 2. Assign remaining text to edges (lines)
    for edge in graph.edges:
        # Find text closest to the midpoint of the line
        p1, p2 = edge.polyline
        midpoint = ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)
        closest_text = None
        min_dist = float('inf')

        for text in unassigned_texts:
            text_center = get_bbox_center(text.bbox)
            dist = calculate_distance(midpoint, text_center)
            if dist < 50 and dist < min_dist:
                min_dist = dist
                closest_text = text
        
        if closest_text:
            edge.label = closest_text.content
            unassigned_texts.remove(closest_text)

    # --- Connect Edges to Nodes ---
    all_nodes = graph.nodes
    for edge in graph.edges:
        start_point, end_point = edge.polyline[0], edge.polyline[-1]
        
        closest_start_node, closest_end_node = None, None
        min_dist_start, min_dist_end = float('inf'), float('inf')

        for node in all_nodes:
            node_center = get_bbox_center(node.bbox)
            
            dist_start = calculate_distance(start_point, node_center)
            if dist_start < min_dist_start:
                min_dist_start = dist_start
                closest_start_node = node
            
            dist_end = calculate_distance(end_point, node_center)
            if dist_end < min_dist_end:
                min_dist_end = dist_end
                closest_end_node = node
        
        # Connect if within a reasonable threshold
        if min_dist_start < 50 and closest_start_node:
            edge.endpoints = (closest_start_node.id, edge.endpoints[1])
        
        if min_dist_end < 50 and closest_end_node:
            edge.endpoints = (edge.endpoints[0], closest_end_node.id)

    return graph
