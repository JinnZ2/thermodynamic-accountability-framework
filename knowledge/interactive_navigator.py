"""
interactive_navigator.py

Knowledge Liberation Module 4: Spatial navigation through the playground.

The pipeline isn't linear in practice. You pull an edge, it sparks a
question, you jump to another part of the study, you bring in outside
context, you come back and reframe. The navigator scaffolds THAT.

This is not a flowchart. It is a graph you can walk, skip, branch, and
return through without losing the thread.

Core primitives:
    Node     - any point in the analysis (scope item, edge, build,
               external context)
    Link     - connection between nodes (with reason/relationship type)
    Session  - your working state, what you've explored, what's open

License: CC0
Ported from github.com/JinnZ2/Logic-Ferret/knowledge/interactive_navigator.py
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Set
from enum import Enum
from datetime import datetime
import json


# ============================================================
# NODE TYPES
# ============================================================

class NodeType(Enum):
    """What kind of thinking-object is this?"""
    STUDY_CLAIM = "study_claim"
    SCOPE_ITEM = "scope_item"
    SILENCE = "silence"
    EDGE_QUESTION = "edge_question"
    EXTERNAL_CONTEXT = "external_context"
    REFRAME = "reframe"
    BUILD_CANDIDATE = "build_candidate"
    OPEN_QUESTION = "open_question"
    FIELD_OBSERVATION = "field_observation"
    HYPOTHESIS = "hypothesis"


class LinkType(Enum):
    """How are two nodes related?"""
    OPENS = "opens"                        # A -> B: A raises B
    CONTRADICTS = "contradicts"            # A conflicts with B
    SUPPORTS = "supports"                  # A reinforces B
    RECONTEXTUALIZES = "recontextualizes"  # B changes the meaning of A
    BUILDS_ON = "builds_on"                # B extends A
    PARALLEL_TO = "parallel_to"            # similar structure
    INVERTS = "inverts"                    # B is the sign-flip of A
    ANSWERS = "answers"                    # B addresses A
    BRANCHES_FROM = "branches_from"        # B is a new direction from A


# ============================================================
# NODES AND LINKS
# ============================================================

@dataclass
class Node:
    """A thinking-object in the analysis graph."""
    id: str
    node_type: NodeType
    content: str
    source: str = ""                           # study / field / prior analysis
    status: str = "open"                       # open / explored / resolved / parked
    tags: List[str] = field(default_factory=list)
    created: str = field(default_factory=lambda: datetime.now().isoformat())
    notes: List[str] = field(default_factory=list)

    def add_note(self, note: str) -> None:
        self.notes.append(f"[{datetime.now().strftime('%H:%M')}] {note}")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.node_type.value,
            "content": self.content,
            "source": self.source,
            "status": self.status,
            "tags": self.tags,
            "notes": self.notes,
        }


@dataclass
class Link:
    """A relationship between two nodes."""
    from_id: str
    to_id: str
    link_type: LinkType
    reason: str = ""                           # why is this link here?

    def to_dict(self) -> Dict[str, Any]:
        return {
            "from": self.from_id,
            "to": self.to_id,
            "type": self.link_type.value,
            "reason": self.reason,
        }


# ============================================================
# SESSION
# ============================================================

@dataclass
class Session:
    """
    Your working state across a thinking session.

    The session holds the full graph of what you've explored.
    You can walk it, branch from any node, inject external context,
    park threads, return later.
    """
    session_name: str
    nodes: Dict[str, Node] = field(default_factory=dict)
    links: List[Link] = field(default_factory=list)
    current_node_id: Optional[str] = None
    parked_threads: List[str] = field(default_factory=list)
    focus_stack: List[str] = field(default_factory=list)

    def add_node(self, node: Node) -> str:
        self.nodes[node.id] = node
        if self.current_node_id is None:
            self.current_node_id = node.id
        return node.id

    def link(self, from_id: str, to_id: str,
             link_type: LinkType, reason: str = "") -> None:
        if from_id not in self.nodes or to_id not in self.nodes:
            raise ValueError(
                f"Both nodes must exist. Have: {list(self.nodes.keys())}"
            )
        self.links.append(Link(from_id, to_id, link_type, reason))

    def focus(self, node_id: str) -> Node:
        """Move attention to a node. Push previous onto the stack."""
        if node_id not in self.nodes:
            raise ValueError(f"Node {node_id} not found")
        if self.current_node_id:
            self.focus_stack.append(self.current_node_id)
        self.current_node_id = node_id
        return self.nodes[node_id]

    def back(self) -> Optional[Node]:
        """Return to the previous focus."""
        if not self.focus_stack:
            return None
        prev_id = self.focus_stack.pop()
        self.current_node_id = prev_id
        return self.nodes.get(prev_id)

    def park(self, node_id: str, reason: str = "") -> None:
        """Save a thread for later. Don't lose it, just set it aside."""
        if node_id not in self.nodes:
            raise ValueError(f"Node {node_id} not found")
        self.nodes[node_id].status = "parked"
        if reason:
            self.nodes[node_id].add_note(f"PARKED: {reason}")
        if node_id not in self.parked_threads:
            self.parked_threads.append(node_id)

    def neighbors(self, node_id: str) -> List[tuple]:
        """What's connected to this node?"""
        result = []
        for link in self.links:
            if link.from_id == node_id:
                result.append(
                    ("->", link.to_id, link.link_type.value, link.reason))
            elif link.to_id == node_id:
                result.append(
                    ("<-", link.from_id, link.link_type.value, link.reason))
        return result

    def open_threads(self) -> List[Node]:
        """All nodes still in open status -- the live edges of your thinking."""
        return [n for n in self.nodes.values() if n.status == "open"]

    def by_type(self, node_type: NodeType) -> List[Node]:
        return [n for n in self.nodes.values() if n.node_type == node_type]

    def by_tag(self, tag: str) -> List[Node]:
        return [n for n in self.nodes.values() if tag in n.tags]

    def trace(self, node_id: str, max_depth: int = 3) -> List[List[str]]:
        """
        Walk backwards from a node to see its lineage.
        Returns paths of node IDs showing how we got here.
        """
        paths = [[node_id]]
        for _ in range(max_depth):
            new_paths = []
            for path in paths:
                head = path[0]
                predecessors = [l.from_id for l in self.links if l.to_id == head]
                if not predecessors:
                    new_paths.append(path)
                    continue
                for pred in predecessors:
                    if pred in path:  # avoid cycles
                        new_paths.append(path)
                        continue
                    new_paths.append([pred] + path)
            paths = new_paths
        return paths

    def snapshot(self) -> str:
        """Render the session as a spatial summary."""
        lines = [
            "=" * 70,
            f"SESSION: {self.session_name}",
            "=" * 70,
            f"Total nodes: {len(self.nodes)}",
            f"Total links: {len(self.links)}",
            f"Current focus: {self.current_node_id}",
            f"Open threads: {len(self.open_threads())}",
            f"Parked threads: {len(self.parked_threads)}",
            "",
        ]

        by_type = {}
        for n in self.nodes.values():
            by_type.setdefault(n.node_type.value, []).append(n)

        for type_name, nodes in by_type.items():
            lines.append(f"--- {type_name.upper()} ({len(nodes)}) ---")
            for n in nodes:
                marker = "*" if n.id == self.current_node_id else " "
                status_marker = {
                    "open": "o", "parked": "p",
                    "explored": "x", "resolved": "v"
                }.get(n.status, "?")
                content_preview = (
                    n.content[:60] + ("..." if len(n.content) > 60 else "")
                )
                lines.append(
                    f"  {marker}[{status_marker}] {n.id}: {content_preview}"
                )
            lines.append("")

        if self.current_node_id:
            lines.append(f"NEIGHBORS OF CURRENT ({self.current_node_id}):")
            for direction, other_id, link_type, reason in self.neighbors(
                self.current_node_id
            ):
                lines.append(
                    f"  {direction} {other_id} [{link_type}]: "
                    f"{reason or '(no reason given)'}"
                )
            lines.append("")

        if self.parked_threads:
            lines.append("PARKED THREADS (return when ready):")
            for pid in self.parked_threads:
                node = self.nodes.get(pid)
                if node:
                    lines.append(f"  ~ {pid}: {node.content[:60]}")
            lines.append("")

        lines.append("=" * 70)
        return "\n".join(lines)

    def export_graph(self) -> Dict[str, Any]:
        """Full graph export for external analysis or persistence."""
        return {
            "session_name": self.session_name,
            "nodes": [n.to_dict() for n in self.nodes.values()],
            "links": [l.to_dict() for l in self.links],
            "parked_threads": self.parked_threads,
            "current_focus": self.current_node_id,
        }


# ============================================================
# NAVIGATOR (sugar layer on top of Session)
# ============================================================

class Navigator:
    """
    Convenience methods for building sessions during exploration.
    Use when you want to quickly scaffold a graph from a pipeline run.
    """

    def __init__(self, session_name: str):
        self.session = Session(session_name=session_name)
        self._counter = 0

    def _next_id(self, prefix: str) -> str:
        self._counter += 1
        return f"{prefix}_{self._counter:03d}"

    def claim(self, content: str, source: str = "") -> str:
        """Add a study claim as the root."""
        node = Node(
            id=self._next_id("claim"),
            node_type=NodeType.STUDY_CLAIM,
            content=content,
            source=source,
        )
        return self.session.add_node(node)

    def silence(self, content: str, from_node: Optional[str] = None,
                tags: Optional[List[str]] = None) -> str:
        """Add a detected silence."""
        node = Node(
            id=self._next_id("silence"),
            node_type=NodeType.SILENCE,
            content=content,
            tags=tags or [],
        )
        node_id = self.session.add_node(node)
        if from_node:
            self.session.link(
                from_node, node_id, LinkType.OPENS,
                "scope boundary identified"
            )
        return node_id

    def edge(self, question: str, from_node: Optional[str] = None,
             tags: Optional[List[str]] = None) -> str:
        """Add an edge question."""
        node = Node(
            id=self._next_id("edge"),
            node_type=NodeType.EDGE_QUESTION,
            content=question,
            tags=tags or [],
        )
        node_id = self.session.add_node(node)
        if from_node:
            self.session.link(
                from_node, node_id, LinkType.OPENS,
                "edge question generated"
            )
        return node_id

    def context(self, observation: str, from_node: Optional[str] = None,
                source: str = "") -> str:
        """Inject external context (field observation, other study, lived experience)."""
        node = Node(
            id=self._next_id("ctx"),
            node_type=NodeType.EXTERNAL_CONTEXT,
            content=observation,
            source=source,
        )
        node_id = self.session.add_node(node)
        if from_node:
            self.session.link(
                from_node, node_id, LinkType.RECONTEXTUALIZES,
                "external context injected"
            )
        return node_id

    def reframe(self, new_framing: str, from_node: str, reason: str = "") -> str:
        """Reframe a previous node."""
        node = Node(
            id=self._next_id("reframe"),
            node_type=NodeType.REFRAME,
            content=new_framing,
        )
        node_id = self.session.add_node(node)
        self.session.link(from_node, node_id, LinkType.RECONTEXTUALIZES, reason)
        return node_id

    def build(self, what_to_build: str, from_node: str) -> str:
        """Add a build candidate."""
        node = Node(
            id=self._next_id("build"),
            node_type=NodeType.BUILD_CANDIDATE,
            content=what_to_build,
        )
        node_id = self.session.add_node(node)
        self.session.link(
            from_node, node_id, LinkType.BUILDS_ON, "buildable application"
        )
        return node_id

    def hypothesis(self, content: str, from_node: str) -> str:
        """Add a hypothesis."""
        node = Node(
            id=self._next_id("hyp"),
            node_type=NodeType.HYPOTHESIS,
            content=content,
        )
        node_id = self.session.add_node(node)
        self.session.link(from_node, node_id, LinkType.OPENS, "testable prediction")
        return node_id


# ============================================================
# EXAMPLE: THE CHILDHOOD-TRAUMA STUDY AS A WALKABLE GRAPH
# ============================================================

if __name__ == "__main__":
    nav = Navigator("PLOS_One_2024_childhood_trauma_suicide_risk")

    claim_id = nav.claim(
        content="Childhood trauma predicts suicide risk via stress appraisal",
        source="PLOS One 0326120, 2025, N=273 UK adults",
    )

    s1 = nav.silence(
        "Does NOT control for current environment threat level",
        from_node=claim_id,
        tags=["context-blind", "selection"],
    )
    s2 = nav.silence(
        "Does NOT distinguish accurate vs. false threat assessment",
        from_node=claim_id,
        tags=["ontological-collapse"],
    )
    s3 = nav.silence(
        "Does NOT measure people in acute crisis (sample is employed/stable)",
        from_node=claim_id,
        tags=["survival-selection"],
    )

    e1 = nav.edge(
        "Does the finding invert when current environment matches childhood calibration?",
        from_node=s1,
        tags=["sign-inversion", "adaptive-match"],
    )
    e2 = nav.edge(
        "For high-defeat participants, are their situations objectively escapable or not?",
        from_node=s2,
        tags=["ontology"],
    )
    e3 = nav.edge(
        "What would suicide risk look like measured in unhoused or incarcerated populations?",
        from_node=s3,
        tags=["invisible-population"],
    )

    ctx1 = nav.context(
        "August 2024 UK: housing crisis, cost-of-living pressure, precarious employment",
        from_node=e1,
        source="field observation / news context",
    )

    reframe1 = nav.reframe(
        "Study may be measuring accurate detection of institutional capture, "
        "not pathology -- entrapment scores may reflect reality",
        from_node=ctx1,
        reason="current environment actually IS high-threat for many participants",
    )

    hyp1 = nav.hypothesis(
        "Stratify by current economic precarity: trauma-calibrated "
        "participants in high-precarity will have LOWER suicide risk than "
        "low-trauma peers in same precarity (accurate detection is protective)",
        from_node=reframe1,
    )

    build1 = nav.build(
        "Intervention architecture that separates structural entrapment "
        "(needs resources/exit) from perceptual entrapment (needs recalibration)",
        from_node=reframe1,
    )

    nav.session.park(
        e3, reason="requires different sample, different protocol -- later"
    )

    print(nav.session.snapshot())

    print("\n\n--- TRACING HOW WE GOT TO hyp_001 ---\n")
    for path in nav.session.trace(hyp1):
        print(" -> ".join(path))
