from ..models import Graph, DexpiExport, DexpiEquipment, DexpiInstrument, DexpiLine, DexpiConnection
import json
import pandas as pd

def to_dexpi_lite_json(graph: Graph) -> str:
    """
    Converts the internal graph representation to a DEXPI-lite JSON format.
    """
    export_data = DexpiExport()

    node_map = {node.id: node for node in graph.nodes}

    for node in graph.nodes:
        if node.kind == "equipment":
            export_data.equipment.append(DexpiEquipment(
                id=node.id,
                classRef=f"placeholder/{node.type}", # Placeholder mapping
                bbox=node.bbox,
                tag=node.tag
            ))
        elif node.kind == "instrument":
            export_data.instruments.append(DexpiInstrument(
                id=node.id,
                classRef=f"placeholder/{node.type}",
                bbox=node.bbox,
                tag=node.tag
            ))

    for edge in graph.edges:
        export_data.lines.append(DexpiLine(
            id=edge.id,
            classRef=f"placeholder/{edge.kind}_line",
            polyline=edge.polyline
        ))
        
        # Create connections
        start_node_id, end_node_id = edge.endpoints
        if start_node_id and end_node_id:
            export_data.connections.append(DexpiConnection(
                from_node=start_node_id,
                to_node=end_node_id,
                line_id=edge.id
            ))

    export_data.issues = graph.issues

    return export_data.model_dump_json(indent=2)


def to_csv(graph: Graph) -> dict:
    """
    Converts the graph nodes and edges into separate CSV strings.
    """
    # Nodes CSV
    node_data = []
    for node in graph.nodes:
        node_data.append({
            "id": node.id,
            "kind": node.kind,
            "type": node.type,
            "tag": node.tag,
            "confidence": node.confidence,
            "bbox_x": node.bbox.x,
            "bbox_y": node.bbox.y,
            "bbox_w": node.bbox.w,
            "bbox_h": node.bbox.h,
        })
    nodes_df = pd.DataFrame(node_data)
    
    # Edges CSV
    edge_data = []
    for edge in graph.edges:
        edge_data.append({
            "id": edge.id,
            "kind": edge.kind,
            "label": edge.label,
            "direction": edge.direction,
            "from_node": edge.endpoints[0],
            "to_node": edge.endpoints[1],
        })
    edges_df = pd.DataFrame(edge_data)

    return {
        "nodes": nodes_df.to_csv(index=False),
        "edges": edges_df.to_csv(index=False)
    }
    