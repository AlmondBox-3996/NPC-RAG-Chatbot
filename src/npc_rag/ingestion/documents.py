import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SENTENCE_BOUNDARY_RE = re.compile(r"(?<=[.!?])\s+")


@dataclass(slots=True)
class LoreDocument:
    document_id: str
    source: str
    content: str
    metadata: dict[str, Any]


def _pipe_join(values: list[str]) -> str:
    return "|".join(values)


def _stable_hash(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:12]


def _build_metadata(document: dict[str, Any], source_name: str) -> dict[str, Any]:
    region_tags = [str(value) for value in document.get("region_tags", [])]
    quest_dependencies = [str(value) for value in document.get("quest_dependencies", [])]
    related_npcs = [str(value) for value in document.get("related_npcs", [])]
    related_items = [str(value) for value in document.get("related_items", [])]

    return {
        "source_file": source_name,
        "document_id": str(document["document_id"]),
        "title": str(document.get("title", document["document_id"])),
        "category": str(document.get("category", "lore")),
        "summary": str(document.get("summary", "")),
        "spoiler_level": int(document.get("spoiler_level", 0)),
        "region": region_tags[0] if region_tags else "",
        "region_tags": _pipe_join(region_tags),
        "region_count": len(region_tags),
        "quest": quest_dependencies[0] if quest_dependencies else "",
        "quest_dependencies": _pipe_join(quest_dependencies),
        "quest_dependency_count": len(quest_dependencies),
        "item": related_items[0] if related_items else "",
        "related_items": _pipe_join(related_items),
        "item_count": len(related_items),
        "npc_relevance": _pipe_join(related_npcs),
        "npc_relevance_count": len(related_npcs),
    }


def load_lore_documents(lore_path: Path) -> list[LoreDocument]:
    documents: list[LoreDocument] = []
    json_path = lore_path / "lore_documents.json"

    if json_path.exists():
        payload = json.loads(json_path.read_text(encoding="utf-8"))
        for entry in payload.get("documents", []):
            content = str(entry.get("content", "")).strip()
            if not content:
                continue

            documents.append(
                LoreDocument(
                    document_id=str(entry["document_id"]),
                    source=json_path.name,
                    content=content,
                    metadata=_build_metadata(entry, json_path.name),
                )
            )
        return documents

    for file_path in sorted(lore_path.glob("*.txt")):
        text = file_path.read_text(encoding="utf-8").strip()
        if not text:
            continue

        documents.append(
            LoreDocument(
                document_id=file_path.stem,
                source=file_path.name,
                content=text,
                metadata={
                    "source_file": file_path.name,
                    "document_id": file_path.stem,
                    "title": file_path.stem.replace("_", " ").title(),
                    "category": "legacy_lore",
                    "summary": "",
                    "spoiler_level": 0,
                    "region": "",
                    "region_tags": "",
                    "region_count": 0,
                    "quest": "",
                    "quest_dependencies": "",
                    "quest_dependency_count": 0,
                    "item": "",
                    "related_items": "",
                    "item_count": 0,
                    "npc_relevance": "",
                    "npc_relevance_count": 0,
                },
            )
        )

    return documents


def _split_paragraphs(text: str) -> list[str]:
    paragraphs = [paragraph.strip() for paragraph in re.split(r"\n\s*\n", text) if paragraph.strip()]
    return paragraphs or [text.strip()]


def _split_long_paragraph(paragraph: str, max_chars: int) -> list[str]:
    sentences = [sentence.strip() for sentence in SENTENCE_BOUNDARY_RE.split(paragraph) if sentence.strip()]
    if not sentences:
        return [paragraph.strip()]

    parts: list[str] = []
    current = ""
    for sentence in sentences:
        candidate = f"{current} {sentence}".strip()
        if current and len(candidate) > max_chars:
            parts.append(current)
            current = sentence
        else:
            current = candidate

    if current:
        parts.append(current)

    return parts


def chunk_document(
    document: LoreDocument,
    target_chars: int = 420,
    max_chars: int = 550,
    overlap_sentences: int = 1,
) -> list[LoreDocument]:
    paragraphs = _split_paragraphs(document.content)
    normalized_paragraphs: list[str] = []
    for paragraph in paragraphs:
        if len(paragraph) > max_chars:
            normalized_paragraphs.extend(_split_long_paragraph(paragraph, max_chars=max_chars))
        else:
            normalized_paragraphs.append(paragraph)

    chunks: list[str] = []
    current_parts: list[str] = []

    for paragraph in normalized_paragraphs:
        candidate = "\n\n".join(current_parts + [paragraph]).strip()
        if current_parts and len(candidate) > max_chars:
            chunks.append("\n\n".join(current_parts).strip())

            overlap_context = ""
            if overlap_sentences > 0:
                previous_sentences = [
                    sentence.strip()
                    for sentence in SENTENCE_BOUNDARY_RE.split(current_parts[-1])
                    if sentence.strip()
                ]
                overlap_context = " ".join(previous_sentences[-overlap_sentences:])

            current_parts = [part for part in [overlap_context, paragraph] if part]
        else:
            current_parts.append(paragraph)

        if len("\n\n".join(current_parts)) >= target_chars:
            chunks.append("\n\n".join(current_parts).strip())
            current_parts = []

    if current_parts:
        chunks.append("\n\n".join(current_parts).strip())

    chunked_documents: list[LoreDocument] = []
    for index, chunk_text in enumerate(chunk for chunk in chunks if chunk):
        chunk_id = f"{document.document_id}-chunk-{index}-{_stable_hash(chunk_text)}"
        chunk_metadata = {
            **document.metadata,
            "chunk_index": index,
            "chunk_hash": _stable_hash(chunk_text),
            "chunk_chars": len(chunk_text),
        }
        chunked_documents.append(
            LoreDocument(
                document_id=chunk_id,
                source=document.source,
                content=chunk_text,
                metadata=chunk_metadata,
            )
        )

    return chunked_documents
