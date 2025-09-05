import cv2
import numpy as np
from typing import List, Tuple
from backend.models import Edge, Node, BoundingBox

def extract_lines_and_junctions(image_path: str) -> Tuple[List[Edge], List[Node]]:
    """
    Extracts straight lines and identifies junctions (intersections and endpoints).
    """
    img = cv2.imread(image_path)
    if img is None:
        return [], []

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150, apertureSize=3)

    # --- Line Detection ---
    lines = cv2.HoughLinesP(
        edges,
        rho=1,
        theta=np.pi / 180,
        threshold=50,
        minLineLength=50,
        maxLineGap=10
    )

    if lines is None:
        return [], []

    # Basic line segment merging could be added here, but we'll keep it simple.
    line_edges: List[Edge] = []
    for i, line in enumerate(lines):
        x1, y1, x2, y2 = line[0]
        line_edges.append(
            Edge(
                id=f"line_{i}",
                kind="process", # Assume process line for now
                polyline=[(x1, y1), (x2, y2)],
                endpoints=(None, None) # To be determined later
            )
        )

    # --- Junction Detection (simple intersection finding) ---
    # This is a naive approach. A better way would be to use a grid or skeletonization.
    # For now, we'll just create nodes at line endpoints.
    junction_nodes: List[Node] = []
    node_counter = 0
    for edge in line_edges:
        p1, p2 = edge.polyline
        # Create a small bounding box for the junction
        junction_nodes.append(Node(
            id=f"jct_{node_counter}",
            kind="junction",
            bbox=BoundingBox(x=p1[0]-2, y=p1[1]-2, w=4, h=4)
        ))
        node_counter += 1
        junction_nodes.append(Node(
            id=f"jct_{node_counter}",
            kind="junction",
            bbox=BoundingBox(x=p2[0]-2, y=p2[1]-2, w=4, h=4)
        ))
        node_counter += 1

    # Arrowhead detection is complex; a simple template match at line ends would go here.
    # For MVP, we'll skip robust arrowhead detection.

    return line_edges, junction_nodes
