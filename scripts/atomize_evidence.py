"""
Atomize evidence: convert markdown evidence files into structured JSON atoms.

Reads all .md files from each evidence category (structural, empirical, ground_truth)
and produces one JSON file per category per entity:
  evidence/{entity}/structural.json
  evidence/{entity}/empirical.json
  evidence/{entity}/ground_truth.json

Each atom has the shape expected by the Evidence Pydantic model in models/observation.py.

Existing .md files are NOT modified or removed.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

EVIDENCE_DIR = Path(__file__).parent.parent / "evidence"
ENTITIES = ["credit-suisse", "ftx"]
CATEGORIES = ["structural", "empirical", "ground_truth"]


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Extract YAML-style frontmatter and body from markdown text."""
    meta = {}
    body = text

    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            fm_block = parts[1].strip()
            body = parts[2].strip()
            for line in fm_block.splitlines():
                if ":" in line:
                    key, _, val = line.partition(":")
                    meta[key.strip()] = val.strip()

    return meta, body


def split_into_atoms(body: str) -> list[str]:
    """
    Split a markdown body into atomic sections by ## headers.

    If there's only one section (or no ## headers), return the whole body as one atom.
    Each atom includes its ## header for context.
    """
    # Split on ## headers (not ### or deeper)
    sections = re.split(r"(?=^## )", body, flags=re.MULTILINE)
    sections = [s.strip() for s in sections if s.strip()]

    # If splitting produced only 1 chunk, or the body is short enough, keep as single atom
    if len(sections) <= 1 or len(body) < 800:
        return [body]

    # Grab any preamble before the first ## header
    preamble = ""
    if not body.lstrip().startswith("## "):
        preamble = sections[0]
        sections = sections[1:]

    atoms = []
    for section in sections:
        # Prepend preamble context (title line) to each atom so it's self-contained
        title_line = preamble.split("\n")[0] if preamble else ""
        if title_line and not section.startswith(title_line):
            atom_text = f"{title_line}\n\n{section}"
        else:
            atom_text = section
        atoms.append(atom_text.strip())

    return atoms if atoms else [body]


def infer_date(filename: str, meta: dict) -> str | None:
    """Extract date from frontmatter or filename (YYYYMMDD prefix)."""
    if "date" in meta:
        raw = meta["date"]
        # Try to extract a clean YYYY-MM-DD from the date field
        m = re.match(r"(\d{4}-\d{2}-\d{2})", raw)
        if m:
            return m.group(1)
        # Try YYYYMMDD
        m = re.match(r"(\d{4})(\d{2})(\d{2})", raw)
        if m:
            return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
        return raw

    # Infer from filename
    stem = Path(filename).stem
    m = re.match(r"(\d{4})(\d{2})(\d{2})", stem)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"

    return None


def infer_type(filename: str, category: str) -> str:
    """Infer evidence type from filename keywords and category."""
    if category == "structural":
        return "structural"

    name = filename.lower()
    if any(k in name for k in ("news", "press", "tweet", "interview", "statement",
                                "reaction", "announcement", "video", "speech")):
        return "news"
    if any(k in name for k in ("filing", "sec", "fdic", "earnings", "prospectus",
                                "report", "annual", "20f", "10k", "10q")):
        return "filing"
    if any(k in name for k in ("price", "chart", "data", "cds", "stock", "spread",
                                "comparison", "onchain", "flow")):
        return "market"

    return "news" if category == "ground_truth" else "market"


def is_counter_evidence(body: str, filename: str) -> bool:
    """Detect if this is counter-evidence from content or naming patterns."""
    name = filename.lower()
    counter_keywords = ["counter", "defense", "reassurance", "stability",
                        "optimism", "relief", "rally", "fine", "calm"]
    return any(k in name for k in counter_keywords)


def atomize_file(filepath: Path, category: str, counter_start: int) -> list[dict]:
    """Convert a single .md file into one or more evidence atoms."""
    try:
        raw = filepath.read_text(encoding="utf-8")
    except Exception as e:
        print(f"  SKIP {filepath.name}: {e}")
        return []

    meta, body = parse_frontmatter(raw)
    atoms_text = split_into_atoms(body)
    date = infer_date(filepath.name, meta)
    ev_type = infer_type(filepath.name, category)
    source_url = meta.get("source_url", "")
    source_file = filepath.stem
    is_counter = is_counter_evidence(body, filepath.name)

    prefix = {"structural": "S", "empirical": "E", "ground_truth": "G"}[category]

    atoms = []
    for i, atom_text in enumerate(atoms_text):
        atom_id = f"{prefix}{counter_start + i:02d}"

        # Extract a short label from the first header or first line
        label_match = re.search(r"^#+ (.+)$", atom_text, re.MULTILINE)
        label = label_match.group(1).strip() if label_match else atom_text[:80].strip()

        atoms.append({
            "observation_id": atom_id,
            "label": label,
            "content": atom_text,
            "source": source_file,
            "source_url": source_url,
            "type": ev_type,
            "date": date,
            "is_counter_evidence": is_counter,
            "supports": [],
            "contradicts": [],
            "neutral": [],
        })

    return atoms


def atomize_category(entity_dir: Path, category: str) -> list[dict]:
    """Atomize all .md files in a category directory."""
    cat_dir = entity_dir / category
    if not cat_dir.exists():
        return []

    md_files = sorted(cat_dir.glob("*.md"))
    if not md_files:
        return []

    all_atoms = []
    counter = 1

    for md_file in md_files:
        atoms = atomize_file(md_file, category, counter)
        all_atoms.extend(atoms)
        counter += len(atoms)

    # Re-number sequentially after all splitting
    prefix = {"structural": "S", "empirical": "E", "ground_truth": "G"}[category]
    for i, atom in enumerate(all_atoms):
        atom["observation_id"] = f"{prefix}{i + 1:02d}"

    return all_atoms


def main():
    for entity in ENTITIES:
        entity_dir = EVIDENCE_DIR / entity
        if not entity_dir.exists():
            print(f"SKIP {entity}: directory not found")
            continue

        print(f"\n{'='*60}")
        print(f"  Atomizing: {entity}")
        print(f"{'='*60}")

        for category in CATEGORIES:
            atoms = atomize_category(entity_dir, category)

            if not atoms:
                print(f"  {category}: no .md files found")
                continue

            out_path = entity_dir / f"{category}.json"
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(atoms, f, indent=2, ensure_ascii=False)

            total_chars = sum(len(a["content"]) for a in atoms)
            print(f"  {category}: {len(atoms)} atoms → {out_path.name} ({total_chars:,} chars)")

    print(f"\nDone. Existing .md files unchanged.")


if __name__ == "__main__":
    main()
