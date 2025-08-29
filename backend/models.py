from pydantic import BaseModel
from typing import List, Optional, Tuple, Dict, Any

class BoundingBox(BaseModel):
    x: int
    y: int
    w: int
    h: int

class Node(BaseModel):
    id: str
    kind: str  # "equipment", "instrument", "junction"
    type: Optional[str] = None
    bbox: BoundingBox
    tag: Optional[str] = None
    attributes: Dict[str, Any] = {}
    confidence: Optional[float] = None

class Edge(BaseModel):
    id: str
    kind: str  # "process", "signal"
    polyline: List[Tuple[int, int]]
    direction: str = "unknown"  # "unknown", "a->b", "b->a"
    endpoints: Tuple[Optional[str], Optional[str]] # (nodeIdA, nodeIdB)
    label: Optional[str] = None
    attributes: Dict[str, Any] = {}
    confidence: Optional[float] = None

class InstrumentTag(BaseModel):
    rawTag: str
    loopLetters: Optional[str] = None
    loopNo: Optional[int] = None
    modifiers: Optional[List[str]] = None
    isParsed: bool = False

class Issue(BaseModel):
    id: str
    severity: str  # "info", "warn", "error"
    message: str
    targetId: Optional[str] = None # ID of the node, edge, or text with the issue

class Text(BaseModel):
    id: str
    content: str
    bbox: BoundingBox

class Graph(BaseModel):
    nodes: List[Node] = []
    edges: List[Edge] = []
    issues: List[Issue] = []
    texts: List[Text] = []

# --- DEXPI-lite Export Schemas ---

class DexpiEquipment(BaseModel):
    id: str
    classRef: str # Placeholder for DEXPI/ISO 15926 mapping
    bbox: BoundingBox
    tag: Optional[str] = None

class DexpiInstrument(BaseModel):
    id: str
    classRef: str
    bbox: BoundingBox
    tag: Optional[str] = None

class DexpiLine(BaseModel):
    id: str
    classRef: str
    polyline: List[Tuple[int, int]]

class DexpiConnection(BaseModel):
    from_node: str
    to_node: str
    line_id: str

class DexpiExport(BaseModel):
    equipment: List[DexpiEquipment] = []
    instruments: List[DexpiInstrument] = []
    lines: List[DexpiLine] = []
    connections: List[DexpiConnection] = []
    issues: List[Issue] = []
