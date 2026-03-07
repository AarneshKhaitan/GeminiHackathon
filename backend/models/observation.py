"""
Evidence observation schema.

Defines the atomic unit of evidence collected during investigations.
Each observation is tagged against active hypotheses to enable principled
hypothesis elimination.
"""

from pydantic import BaseModel, Field
from typing import Literal


class Evidence(BaseModel):
    """
    Atomic evidence observation with hypothesis tagging.

    Tags (supports/contradicts/neutral) enable traceable elimination:
    when an observation contradicts a hypothesis, elimination is traceable
    to the specific atom that killed it.
    """

    observation_id: str = Field(
        ...,
        description="Unique atom identifier (e.g., 'S01' for structural, 'E01' for empirical)"
    )

    content: str = Field(
        ...,
        description="Full text content of the observation"
    )

    source: str = Field(
        ...,
        description="Origin of the evidence (e.g., 'FDIC Report', 'SEC 10-K', 'Bloomberg')"
    )

    type: Literal["structural", "market", "news", "filing"] = Field(
        ...,
        description="Category of evidence: structural (domain knowledge), market (data), news, filing"
    )

    supports: list[str] = Field(
        default_factory=list,
        description="List of hypothesis IDs this observation supports"
    )

    contradicts: list[str] = Field(
        default_factory=list,
        description="List of hypothesis IDs this observation contradicts"
    )

    neutral: list[str] = Field(
        default_factory=list,
        description="List of hypothesis IDs this observation is neutral toward"
    )

    date: str | None = Field(
        default=None,
        description="Date of observation (if applicable)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "observation_id": "S01",
                "content": "SVB held $91B of available-for-sale (AFS) and held-to-maturity (HTM) securities with significant unrealized losses.",
                "source": "FDIC Report",
                "type": "structural",
                "supports": ["H01", "H02"],
                "contradicts": ["H05"],
                "neutral": ["H03"],
                "date": "2023-03-10"
            }
        }
