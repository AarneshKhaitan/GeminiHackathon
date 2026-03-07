"""
Corpus loader — reads evidence markdown files from evidence/{entity}/ directories.

Evidence is organized as:
  evidence/{entity_slug}/structural/*.md   — permanent domain knowledge
  evidence/{entity_slug}/empirical/*.md    — time-stamped market/news/filing data

Returns dicts matching the Evidence model schema with empty tag lists
(tags are added by the packager via a Gemini call).
"""

from pathlib import Path
from typing import Literal

CORPUS_DIR = Path(__file__).parent.parent / "corpus"  # backend/corpus/

ENTITY_SLUG: dict[str, str] = {
    "Silicon Valley Bank": "svb",
    "Credit Suisse": "credit-suisse",
    "First Republic Bank": "ftx",
}

# Extensions that can be read as text
_TEXT_EXTENSIONS = {".md", ".txt"}


def _entity_dir(entity: str, corpus_type: Literal["structural", "empirical"]) -> Path:
    """
    Get evidence directory for corpus type.

    All evidence is in backend/corpus/{structural|empirical}/
    """
    return CORPUS_DIR / corpus_type


def _extract_date(filename: str) -> str | None:
    """Extract date from filenames like 20230315_..."""
    name = Path(filename).stem
    if len(name) >= 8 and name[:8].isdigit():
        d = name[:8]
        return f"{d[:4]}-{d[4:6]}-{d[6:8]}"
    return None


def _infer_empirical_type(filename: str) -> str:
    """Infer market / news / filing from filename keywords."""
    name = filename.lower()
    if any(k in name for k in ("filing", "sec", "fdic", "earnings", "prospectus", "20f", "annual")):
        return "filing"
    if any(k in name for k in ("news", "press", "tweet", "interview", "statement", "speech",
                                "ceo", "chairman", "analyst", "article", "coindesk", "sequoia",
                                "fortune", "bloomberg")):
        return "news"
    return "market"


def _load_md_file(path: Path) -> str:
    """Read a markdown file, return up to 3000 chars of content."""
    try:
        return path.read_text(encoding="utf-8", errors="replace")[:3000]
    except Exception:
        return ""


def load_all_corpus(entity: str, corpus_type: Literal["structural", "empirical"]) -> list[dict]:
    """
    Load all markdown evidence files for an entity/type.

    Args:
        entity: Full entity name e.g. "Credit Suisse"
        corpus_type: "structural" or "empirical"

    Returns:
        List of observation dicts with empty supports/contradicts/neutral
    """
    dir_path = _entity_dir(entity, corpus_type)
    if not dir_path.exists():
        return []

    results = []
    counter = 0
    prefix = "S" if corpus_type == "structural" else "E"

    for md_file in sorted(dir_path.glob("*.md")):
        content = _load_md_file(md_file)
        if not content.strip():
            continue

        counter += 1
        obs_id = f"{prefix}{counter:02d}"
        obs_type = "structural" if corpus_type == "structural" else _infer_empirical_type(md_file.name)

        results.append({
            "observation_id": obs_id,
            "content": content,
            "source": md_file.stem.replace("_", " ").title(),
            "type": obs_type,
            "date": _extract_date(md_file.name),
            "supports": [],
            "contradicts": [],
            "neutral": [],
        })

    return results


def search_corpus(
    query: str,
    entity: str,
    corpus_type: Literal["structural", "empirical"],
    limit: int = 5,
) -> list[dict]:
    """
    Keyword search across markdown files for an entity/type.

    Splits query into terms; returns files where ANY term appears.

    Args:
        query: Search terms from an evidence request description
        entity: Full entity name
        corpus_type: "structural" or "empirical"
        limit: Max results to return

    Returns:
        List of matching observation dicts (untagged)
    """
    dir_path = _entity_dir(entity, corpus_type)
    if not dir_path.exists():
        return []

    query_terms = [t for t in query.lower().split() if len(t) > 2]
    if not query_terms:
        return []

    results = []
    counter = 0
    prefix = "S" if corpus_type == "structural" else "E"

    for md_file in sorted(dir_path.glob("*.md")):
        counter += 1
        content = _load_md_file(md_file)
        if not content.strip():
            continue

        content_lower = content.lower()
        if not any(term in content_lower for term in query_terms):
            continue

        obs_id = f"{prefix}{counter:02d}"
        obs_type = "structural" if corpus_type == "structural" else _infer_empirical_type(md_file.name)

        results.append({
            "observation_id": obs_id,
            "content": content,
            "source": md_file.stem.replace("_", " ").title(),
            "type": obs_type,
            "date": _extract_date(md_file.name),
            "supports": [],
            "contradicts": [],
            "neutral": [],
        })

        if len(results) >= limit:
            break

    return results


def list_corpus_files(entity: str, corpus_type: Literal["structural", "empirical"]) -> list[str]:
    """Return sorted list of markdown filenames for an entity/type."""
    dir_path = _entity_dir(entity, corpus_type)
    if not dir_path.exists():
        return []
    return [f.name for f in sorted(dir_path.glob("*.md"))]
