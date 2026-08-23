"""Constants, attribution strings and Swiss-specific lookup tables.

Findings from the live probe (2026-07-19) that shaped this module are marked
with `FINDING:` so that they survive future refactorings.
"""

from __future__ import annotations

from mcp.types.version import LATEST_HANDSHAKE_VERSION

from ._version import __version__

OPENHOLIDAYS_BASE = "https://openholidaysapi.org"
NAGER_BASE = "https://date.nager.at/api/v3"

# SEC-021 / SEC-004: code-layer egress allow-list. Immutable (frozenset), not
# config-mutable. Every outbound request is checked against this set before the
# socket is opened (see guard.assert_host_allowed). Extending it is a code change
# + review, documented in docs/network-egress.md.
ALLOWED_HOSTS = frozenset({"openholidaysapi.org", "date.nager.at"})

# ARCH-012: the protocol revision `source_status` reports to callers.
#
# `mcp` 2.x serves two protocol eras over the same server: the `initialize`
# handshake, which caps at `LATEST_HANDSHAKE_VERSION`, and the per-request
# envelope, which reaches `LATEST_MODERN_VERSION`. A single string field cannot
# name both, so it names the one the caller most likely negotiated — the
# handshake ceiling. Measured, not inferred from a constant name: a client that
# asks the handshake for the modern revision gets `2025-11-25` back.
#
# Derived, not written down. A literal here is a second truth beside the SDK,
# and second truths drift: this constant stood at "2025-06-18" for two
# revisions while every `source_status` call reported it to the caller as fact.
# Nothing caught it, because nothing compared it to anything.
# `tests/test_protocol_version.py` holds both eras against the SDK and checks
# the delivered field against `LATEST_HANDSHAKE_VERSION` rather than against
# this constant — a comparison with the value's own source is green for any
# value.
MCP_PROTOCOL_VERSION = LATEST_HANDSHAKE_VERSION

# SEC-018: bounds for numeric tool inputs (no unbounded ranges).
MIN_YEAR = 1970
MAX_YEAR = 2100

USER_AGENT = f"swiss-holidays-mcp/{__version__} (+https://github.com/malkreide/swiss-holidays-mcp)"

ATTRIBUTION_OPENHOLIDAYS = (
    "Data: OpenHolidays API (openholidaysapi.org) — CC BY 4.0. "
    "Unofficial aggregation; the cantonal authority remains the authoritative source."
)
ATTRIBUTION_NAGER = (
    "Data: Nager.Date (date.nager.at) — MIT. "
    "Unofficial aggregation; the cantonal authority remains the authoritative source."
)

# FINDING (live probe 2026-07-19): OpenHolidays returns apparent duplicates for
# Zurich school holidays. They are NOT duplicates — they are differentiated by
# `groups[].code`, which encodes the *Schulart*:
#   CH-ZH-VS = Volksschulen      <- Schulamt Stadt Zuerich remit
#   CH-ZH-MS = Mittelschulen
#   CH-ZH-BS = Berufsfachschulen
# Naive de-duplication would destroy exactly the distinction that matters.
SCHOOL_TYPE_SUFFIX = {
    "VS": "Volksschulen",
    "MS": "Mittelschulen",
    "BS": "Berufsfachschulen",
    "EO": "Obligatorische Schulen",
}

# FINDING: only 11 Schulart groups exist nationwide. Most cantons publish a
# single undifferentiated holiday set, i.e. `groups` is absent there.
CANTONS_WITH_SCHOOL_TYPES = ("AI", "AR", "BE", "GR", "SO", "ZH")

DEFAULT_LANGUAGE = "DE"
SUPPORTED_LANGUAGES = ("DE", "FR", "IT", "EN")

# FINDING: /Subdivisions?countryIsoCode=CH returns 26 top-level cantons, but
# holiday records may carry sub-cantonal codes (e.g. CH-AI-AP, CH-BE-TH-BL).
# Always match on the CH-XX prefix, never on string equality.
CANTON_CODES = (
    "CH-AG",
    "CH-AI",
    "CH-AR",
    "CH-BE",
    "CH-BL",
    "CH-BS",
    "CH-FR",
    "CH-GE",
    "CH-GL",
    "CH-GR",
    "CH-JU",
    "CH-LU",
    "CH-NE",
    "CH-NW",
    "CH-OW",
    "CH-SG",
    "CH-SH",
    "CH-SO",
    "CH-SZ",
    "CH-TG",
    "CH-TI",
    "CH-UR",
    "CH-VD",
    "CH-VS",
    "CH-ZG",
    "CH-ZH",
)
