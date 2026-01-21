"""
Prompts para el sistema de análisis SpotterSRS.
Versionados para control de cambios y A/B testing.
"""

from .prompt_spotter_v2 import (
    PROMPT_SPOTTER_V2,
    get_prompt_con_catalogo,
    PROMPT_VERSION,
)

__all__ = [
    "PROMPT_SPOTTER_V2",
    "get_prompt_con_catalogo",
    "PROMPT_VERSION",
]
