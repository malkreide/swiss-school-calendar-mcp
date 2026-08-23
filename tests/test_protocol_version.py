"""ARCH-012: die beiden Spec-Revisionen, gegen die dieser Server geprueft ist.

`mcp` 2.x bedient ZWEI Protokoll-Aeren ueber denselben Server; die erste
Anfrage einer Verbindung entscheidet, welche gilt:

* die **Legacy-Aera** mit `initialize`-Handshake — was heutige Clients
  sprechen. Sie deckelt bei `LATEST_HANDSHAKE_VERSION`.
* die **Modern-Aera** mit Pro-Request-Envelope, die `LATEST_MODERN_VERSION`
  erreicht.

`MCP_PROTOCOL_VERSION` benennt die HANDSHAKE-Aera und wird aus
`LATEST_HANDSHAKE_VERSION` abgeleitet. Das ist eine bewusste Aenderung
gegenueber der vorigen Fassung, in der die Konstante die moderne Aera nannte:
`source_status` liefert sie als Feld `mcp_protocol_version` an Aufrufer aus,
und ein einzelnes Feld kann nicht beide Aeren nennen. Es nennt die, die ein
Aufrufer am ehesten ausgehandelt hat.

Abgeleitet statt hingeschrieben: ein Literal waere eine zweite Wahrheit neben
dem SDK, und zweite Wahrheiten driften. Diese hier stand zwei Revisionen lang
auf `2025-06-18`, waehrend jede `source_status`-Abfrage den Wert als Tatsache
ausgab.

Ohne gemessenen Teil: dieses Repo baut keine ASGI-App, durch die sich ein
`initialize` schicken liesse. Die Aushandlung steht in
`mcp/server/runner.py::_negotiate_initialize` und haengt an keinem Transport —
an neun Schwester-Servern gemessen, hier an den SDK-Konstanten gehalten. Das
ist die schwaechere Form, und sie steht hier benannt statt unausgesprochen.
"""

from __future__ import annotations

import pathlib
import re

from mcp.types.version import (
    LATEST_HANDSHAKE_VERSION,
    LATEST_MODERN_VERSION,
    LATEST_PROTOCOL_VERSION,
)

from swiss_holidays_mcp.constants import MCP_PROTOCOL_VERSION

REPO = pathlib.Path(__file__).resolve().parents[1]

# Datei und Ueberschrift, unter der die Revisionen dokumentiert stehen.
README_SECTIONS = (
    ("README.md", "## MCP Primitives & Protocol Version"),
    ("README.de.md", "## MCP-Primitive & Protokoll-Version"),
)

# Die beiden Revisionen, die die READMEs nennen. Sie stehen hier und nicht im
# `src/`: der Server setzt sie nicht, das SDK bestimmt sie.
DOCUMENTED_HANDSHAKE_VERSION = "2025-11-25"
DOCUMENTED_MODERN_VERSION = "2026-07-28"


def test_die_moderne_aera_steht_wo_die_readmes_sie_nennen() -> None:
    """Faellt das hier, ist die Loesung nicht, den Wert blind nachzuziehen: erst
    das Spec-Changelog zwischen den beiden Revisionen lesen, das
    Serververhalten pruefen, dann Konstanten, READMEs und `CHANGELOG.md` in
    einem Commit anheben.
    """
    assert LATEST_MODERN_VERSION == DOCUMENTED_MODERN_VERSION, (
        f"das SDK erreicht modern jetzt {LATEST_MODERN_VERSION}, "
        f"die READMEs sagen {DOCUMENTED_MODERN_VERSION}"
    )


def test_der_ausgelieferte_pin_nennt_die_handshake_obergrenze() -> None:
    """Die Aera, die bestehende Clients sprechen — und die `source_status` meldet.

    Ein Client, der ueber den `initialize`-Handshake nach der modernen Revision
    fragt, bekommt diese Obergrenze zurueck, nicht das, wonach er gefragt hat.
    Genau deshalb nennt das Feld sie und nicht die moderne Revision.
    """
    assert LATEST_HANDSHAKE_VERSION == DOCUMENTED_HANDSHAKE_VERSION, (
        f"das SDK deckelt den Handshake jetzt bei {LATEST_HANDSHAKE_VERSION}, "
        f"die READMEs sagen {DOCUMENTED_HANDSHAKE_VERSION}"
    )
    assert MCP_PROTOCOL_VERSION == LATEST_HANDSHAKE_VERSION, (
        f"die Konstante nennt {MCP_PROTOCOL_VERSION}, das SDK deckelt bei "
        f"{LATEST_HANDSHAKE_VERSION} — sie ist wieder ein Literal geworden"
    )


def test_latest_protocol_version_ist_der_alias_auf_die_moderne_aera() -> None:
    """Die Falle, gegen die dieses Repo abgesichert wird, benannt.

    Die urspruengliche Zusicherung lautete `PIN == LATEST_PROTOCOL_VERSION` und
    las sich vollstaendig. Sie war es nicht, und man sieht es dem Namen nicht
    an. Faellt dieser Test, hat das SDK die Bedeutung des Alias geaendert —
    dann ist die Aufteilung oben neu zu bewerten, nicht nur eine Zahl.
    """
    assert LATEST_PROTOCOL_VERSION == LATEST_MODERN_VERSION
    assert LATEST_PROTOCOL_VERSION != LATEST_HANDSHAKE_VERSION


def test_die_beiden_aeren_sind_verschieden() -> None:
    """Sagt, wann die Aufteilung oben wieder verschwinden darf: legt das SDK
    die Aeren eines Tages zusammen, ist sie redundant und gehoert zurueckgebaut.
    """
    assert LATEST_MODERN_VERSION > LATEST_HANDSHAKE_VERSION


def test_die_pins_sind_datierte_revisionen_und_keine_beweglichen_ziele() -> None:
    """«latest» oder eine Spanne waeren keine Festlegung."""
    for value in (MCP_PROTOCOL_VERSION, DOCUMENTED_HANDSHAKE_VERSION, DOCUMENTED_MODERN_VERSION):
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", value), value


def test_beide_readmes_nennen_beide_revisionen() -> None:
    """Ein Pin, den die Doku anders angibt, ist kein Pin.

    Jede Sprache einzeln geprueft: im Portfolio sind EN und DE desselben Repos
    schon dreimal auseinandergelaufen, weil nur eine Fassung nachgezogen wurde
    und niemand die andere daneben gelegt hat.
    """
    for name, anchor in README_SECTIONS:
        text = (REPO / name).read_text(encoding="utf-8")
        parts = text.split(anchor, 1)
        assert len(parts) > 1, f"{name} hat keinen Abschnitt «{anchor}»"
        body = parts[1][:2500]
        for value in (
            MCP_PROTOCOL_VERSION,
            DOCUMENTED_HANDSHAKE_VERSION,
            DOCUMENTED_MODERN_VERSION,
        ):
            assert value in body, f"{name} nennt {value} nicht im Abschnitt «{anchor}»"


async def test_source_status_liefert_genau_diesen_pin_aus() -> None:
    """Die Zusicherung, die den Unterschied zu einer Doku-Zeile macht.

    Die bisherige Fassung dieses Tests hiess so, pruefte aber nur, dass das
    Feld `mcp_protocol_version` im Modell EXISTIERT. Ein falscher Wert waere
    anstandslos durchgegangen — genau die Luecke, durch die hier schon einmal
    `2025-06-18` an Aufrufer ging. Jetzt wird der Tool-Aufruf gefahren und der
    ausgelieferte Wert verglichen.

    Warum die Handshake-Obergrenze und nicht die moderne Revision: ein
    einzelnes Feld kann nicht beide Aeren nennen, und ein Aufrufer, der diesen
    Server ueber den `initialize`-Handshake erreicht, hat genau diese
    ausgehandelt. Die READMEs sagen es dazu.
    """
    from mcp import Client

    from swiss_holidays_mcp.models import StatusResponse
    from swiss_holidays_mcp.server import mcp

    assert "mcp_protocol_version" in StatusResponse.model_fields, (
        "source_status traegt das Feld nicht mehr — dann gehoert dieser Test angepasst, "
        "nicht geloescht"
    )

    async with Client(mcp) as client:
        result = await client.call_tool("source_status", {})

    # Gegen das SDK, nicht gegen `MCP_PROTOCOL_VERSION`: ein Vergleich mit der
    # Konstante, aus der der Wert stammt, ist mit jedem Wert gruen — auch dann,
    # wenn jemand die Ableitung wieder durch ein Literal ersetzt. Genau so blieb
    # in `bag-epl-mcp` drei Revisionen lang unbemerkt, dass der Server
    # Aufrufern eine falsche Angabe meldete.
    assert result.structured_content["mcp_protocol_version"] == LATEST_HANDSHAKE_VERSION
