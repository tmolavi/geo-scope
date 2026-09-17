"""
AnswerPath GEO Connector for GEO-Scope.
Bridges AnswerPath question mining, intent classification, and clustering engine
into GEO-Scope's question source and provenance tracking pipeline.
"""
from __future__ import annotations
import csv
import json
import re
import zipfile
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional
from difflib import SequenceMatcher

from geo_scope.questions.models import DiscoveredQuestion, QuestionCluster, DiscoveryResult

INTENTS = {
    "learn": ["what", "چیست", "چیه", "چطور", "how", "guide", "learn", "آموزش", "توضیح"],
    "compare": ["compare", "مقایسه", "بهتر", "vs", "versus", "فرق", "تفاوت", "بررسی"],
    "buy": ["price", "قیمت", "خرید", "buy", "cost", "پکیج", "هزینه", "تعرفه", "اشتراک", "سفارش"],
    "solve": ["مناسب", "حل", "مشکل", "نرم افزار", "service", "خدمت", "حل کردن", "چگونه", "راهکار"],
    "trust": ["review", "نظرات", "اعتماد", "قابل اعتماد", "تجربه", "رضایت", "معتبر"],
}


def clean_text(value: Any) -> str:
    if isinstance(value, str):
        return re.sub(r"\s+", " ", value).strip()
    if isinstance(value, list):
        return clean_text(" ".join(clean_text(x.get("text", "") if isinstance(x, dict) else x) for x in value))
    if isinstance(value, dict):
        return clean_text(value.get("content", value.get("text", value.get("message", value.get("query", "")))))
    return ""


def extract_records(path: str | Path) -> List[Tuple[str, str]]:
    """
    Reads owned exports/logs (.json, .jsonl, .csv, or .zip); never accesses remote provider accounts.
    Returns a list of (query_text, source_identifier) tuples.
    """
    p = Path(path)
    if not p.exists():
        return []

    rows: List[Tuple[str, str]] = []
    if p.suffix.lower() == ".zip":
        with zipfile.ZipFile(p) as z:
            for n in z.namelist():
                if n.lower().endswith((".json", ".jsonl", ".csv", ".txt")):
                    rows.extend(_read_bytes(n, z.read(n), f"{p.name}:{n}"))
        return rows

    if p.is_dir():
        files = [x for x in p.rglob("*") if x.suffix.lower() in {".json", ".jsonl", ".csv", ".txt"}]
    else:
        files = [p]

    for f in files:
        try:
            rows.extend(_read_bytes(str(f), f.read_bytes(), str(f)))
        except Exception:
            continue
    return rows


def _read_bytes(name: str, data: bytes, source: str) -> List[Tuple[str, str]]:
    # 1. Try standard JSON or JSONL
    try:
        obj = json.loads(data)
        return _walk(obj, source)
    except Exception:
        pass

    try:
        lines = [x.strip() for x in data.decode("utf-8", errors="replace").splitlines() if x.strip()]
        obj = [json.loads(x) for x in lines if x.startswith("{") or x.startswith("[")]
        if obj:
            return _walk(obj, source)
    except Exception:
        pass

    # 2. Try CSV
    try:
        lines = data.decode("utf-8", errors="replace").splitlines()
        reader = csv.DictReader(lines)
        out = []
        if reader.fieldnames:
            for row in reader:
                role = str(row.get("role", row.get("speaker", row.get("author", "")))).lower()
                text = clean_text(row.get("content", row.get("text", row.get("query", row.get("question", "")))))
                if text and (not role or role in {"user", "human", "customer", "client"}):
                    out.append((text, source))
            if out:
                return out
    except Exception:
        pass

    # 3. Fallback to Plain Text (1 question per line)
    out = []
    for line in data.decode("utf-8", errors="replace").splitlines():
        t = clean_text(line)
        if len(t) >= 4 and not t.startswith("#"):
            out.append((t, source))
    return out


def _walk(obj: Any, source: str) -> List[Tuple[str, str]]:
    out: List[Tuple[str, str]] = []
    if isinstance(obj, dict):
        role = str(obj.get("role", obj.get("author", obj.get("speaker", "")))).lower()
        if role in {"user", "human", "customer", "client"} or "query" in obj or "question" in obj:
            t = clean_text(obj.get("content", obj.get("text", obj.get("message", obj.get("query", obj.get("question", ""))))))
            if t:
                out.append((t, source))
        for v in obj.values():
            out.extend(_walk(v, source))
    elif isinstance(obj, list):
        for v in obj:
            out.extend(_walk(v, source))
    return out


def classify_intent(text: str) -> str:
    """Classifies user query intent using AnswerPath intent hierarchy."""
    low = text.lower()
    for intent in ("buy", "compare", "trust", "solve", "learn"):
        words = INTENTS[intent]
        if any(w in low for w in words):
            return intent
    return "discover"


def resolve_stage(intent: str) -> str:
    """Maps intent to buyer journey stage."""
    return {
        "learn": "awareness",
        "discover": "awareness",
        "compare": "consideration",
        "trust": "consideration",
        "buy": "decision",
        "solve": "decision",
    }.get(intent, "awareness")


def generate_research_prompts(topic: str) -> List[str]:
    """Generates standard AnswerPath research exploration prompts for a given topic."""
    return [
        f"What is the best {topic} for a small business?",
        f"How do I choose a reliable {topic} provider?",
        f"What should I compare before buying {topic}?",
        f"How much does {topic} cost and what is included?",
        f"Which {topic} is suitable for my needs?",
        f"What are the common problems with {topic} and how are they solved?",
        f"Are there trustworthy reviews or examples for {topic}?",
        f"Compare the leading {topic} options for quality and price.",
        f"Top rated {topic} alternatives and competitors",
        f"Is {topic} worth the investment for high-growth teams?",
    ]


class AnswerPathConnector:
    """
    AnswerPath question discovery connector for GEO-Scope.
    Performs question extraction, intent classification, template generation,
    and sequence-matcher clustering while preserving strict observed vs generated provenance.
    """

    def __init__(self, threshold: float = 0.88):
        self.threshold = threshold

    def mine_questions(
        self,
        topic: str,
        inputs: Optional[List[Tuple[str, str]]] = None,
        include_generated: bool = True,
        category: str = "GEO",
        entities: Optional[List[str]] = None,
    ) -> DiscoveryResult:
        raw_inputs = inputs or []
        discovered: List[DiscoveredQuestion] = []
        observed_count = 0
        generated_count = 0

        # 1. Process observed questions
        for idx, (text, source) in enumerate(raw_inputs, 1):
            t = clean_text(text)
            if len(t) < 4 or len(t) > 1000:
                continue
            intent = classify_intent(t)
            stage = resolve_stage(intent)
            p_id = f"PRM-OBS-{idx:04d}"
            discovered.append(
                DiscoveredQuestion(
                    prompt_id=p_id,
                    question=t,
                    source=source,
                    source_type="observed",
                    source_reference="answerpath:observed",
                    intent=intent,
                    stage=stage,
                    category=category,
                    entities=entities or [],
                    confidence=0.95,
                )
            )
            observed_count += 1

        # 2. Process generated research prompts if enabled
        if include_generated:
            gen_prompts = generate_research_prompts(topic)
            for idx, t in enumerate(gen_prompts, 1):
                intent = classify_intent(t)
                stage = resolve_stage(intent)
                p_id = f"PRM-GEN-{idx:04d}"
                discovered.append(
                    DiscoveredQuestion(
                        prompt_id=p_id,
                        question=t,
                        source="answerpath:template",
                        source_type="generated",
                        source_reference="answerpath:template",
                        intent=intent,
                        stage=stage,
                        category=category,
                        entities=entities or [],
                        confidence=0.85,
                    )
                )
                generated_count += 1

        # 3. Cluster by text similarity
        cluster_groups: List[DiscoveredQuestion] = []
        cluster_map: Dict[int, List[DiscoveredQuestion]] = {}

        for q in discovered:
            match = None
            for existing in cluster_groups:
                ratio = SequenceMatcher(None, q.question.lower(), existing.question.lower()).ratio()
                if ratio >= self.threshold:
                    match = existing
                    break

            if match is not None:
                match.frequency += 1
                q.cluster = match.cluster
                cluster_map.setdefault(match.cluster, []).append(q)
            else:
                c_id = len(cluster_groups)
                q.cluster = c_id
                cluster_groups.append(q)
                cluster_map[c_id] = [q]

        # 4. Construct QuestionCluster representations
        clusters: List[QuestionCluster] = []
        for c_id, group in cluster_map.items():
            rep = group[0]
            stypes = list({item.source_type for item in group})
            clusters.append(
                QuestionCluster(
                    cluster_id=c_id,
                    representative_question=rep.question,
                    size=len(group),
                    intent=rep.intent,
                    source_types=stypes,
                    questions=group,
                )
            )

        # 5. Intent distribution
        intent_dist: Dict[str, int] = {}
        for q in discovered:
            intent_dist[q.intent] = intent_dist.get(q.intent, 0) + 1

        # 6. Recommended benchmark prompts (cluster representatives)
        recommended = [
            c.questions[0].to_prompt_record_dict(
                target_brand=(entities[0] if entities else ""),
                competitors=(entities[1:] if entities and len(entities) > 1 else []),
                niche=category,
            )
            for c in clusters
        ]

        return DiscoveryResult(
            topic=topic,
            total_discovered=len(discovered),
            observed_count=observed_count,
            generated_count=generated_count,
            clusters_count=len(clusters),
            intent_distribution=intent_dist,
            questions=discovered,
            clusters=clusters,
            recommended_prompts=recommended,
        )
