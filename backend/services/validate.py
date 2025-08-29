from typing import List
from ..models import Graph, Issue

def validate_graph(graph: Graph) -> List[Issue]:
    """
    Validates the graph and generates a list of issues.
    """
    issues: List[Issue] = []
    issue_counter = 0

    # Rule 1: Find lines with missing labels
    for edge in graph.edges:
        if not edge.label and edge.kind == "process":
            issues.append(Issue(
                id=f"issue_{issue_counter}",
                severity="warn",
                message="Process line is missing a label/tag.",
                targetId=edge.id
            ))
            issue_counter += 1

    # Rule 2: Find dangling line ends
    for edge in graph.edges:
        start_node, end_node = edge.endpoints
        if not start_node:
            issues.append(Issue(
                id=f"issue_{issue_counter}",
                severity="warn",
                message="Line has a dangling start point (not connected to any node).",
                targetId=edge.id
            ))
            issue_counter += 1
        if not end_node:
            issues.append(Issue(
                id=f"issue_{issue_counter}",
                severity="warn",
                message="Line has a dangling end point (not connected to any node).",
                targetId=edge.id
            ))
            issue_counter += 1

    # Rule 3: Flag low-confidence symbol matches
    for node in graph.nodes:
        if node.kind in ["equipment", "instrument"] and node.confidence is not None:
            if node.confidence < 0.75: # Example threshold
                issues.append(Issue(
                    id=f"issue_{issue_counter}",
                    severity="info",
                    message=f"Low confidence symbol match ({node.confidence:.2f}) for '{node.type}'.",
                    targetId=node.id
                ))
                issue_counter += 1

    # Rule 4: Check for unknown ISA tag combinations (requires tagging service integration)
    # This would be implemented after the tagging service is fully integrated.
    # For now, it's a placeholder.

    graph.issues = issues
    return issues
