"""
SQLite database setup and helpers for the Electronic Component Comparison app.
Creates the schema and seeds sample ECE components on first run.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "components.db"
SCHEMA_VERSION = 2

CATEGORIES = (
    "Resistor",
    "Capacitor",
    "Diode",
    "LED",
    "Transistor",
    "Inductor",
    "IC",
)

# Categories shown as icon quick-links on the home page (poster layout)
HOME_CATEGORIES = (
    "Resistor",
    "Capacitor",
    "Diode",
    "LED",
    "Transistor",
    "IC",
)

SORT_OPTIONS = {
    "name_asc": ("name ASC", "Name A–Z"),
    "name_desc": ("name DESC", "Name Z–A"),
    "category": ("category ASC, name ASC", "Category"),
    "manufacturer": ("manufacturer ASC, name ASC", "Manufacturer"),
}


def _specs(*pairs: tuple[str, str]) -> str:
    return json.dumps([{"label": label, "value": value} for label, value in pairs])


SAMPLE_COMPONENTS: list[dict[str, Any]] = [
    {
        "name": "Carbon Film Resistor 220Ω",
        "category": "Resistor",
        "component_type": "Passive",
        "part_number": "CFR-25JB-52-220R",
        "manufacturer": "Yageo",
        "image_slug": "resistor",
        "description": (
            "A general-purpose 220 Ω carbon film resistor rated at 0.25 W, "
            "ideal for LED current limiting and basic voltage dividers."
        ),
        "key_specs": _specs(
            ("Type", "Passive"),
            ("Resistance", "220 Ω"),
            ("Power Rating", "0.25 W"),
            ("Tolerance", "±5%"),
            ("Applications", "Current limiting, voltage divider"),
        ),
        "specifications": (
            "Resistance: 220 Ω ±5%\n"
            "Power rating: 0.25 W\n"
            "Tolerance: ±5%\n"
            "Max working voltage: 250 V\n"
            "Temperature coefficient: ±350 ppm/°C\n"
            "Operating temperature: -55°C to +155°C"
        ),
        "applications": "Current limiting for LEDs, voltage dividers, pull-up/pull-down networks.",
        "advantages": "Low cost, widely available, perfect for student kits and breadboards.",
        "disadvantages": "Higher noise than metal film; not ideal for precision measurement.",
        "common_uses": "LED series resistors, Arduino GPIO protection, simple dividers.",
        "suggestion": "Choose 220 Ω when driving a standard red/green LED from 5 V at ~15–20 mA.",
    },
    {
        "name": "Metal Film Resistor 10kΩ 1%",
        "category": "Resistor",
        "component_type": "Passive",
        "part_number": "MFR-25FBF52-10K",
        "manufacturer": "Yageo",
        "image_slug": "resistor",
        "description": "Precision 10 kΩ metal film resistor with 1% tolerance for stable analog circuits.",
        "key_specs": _specs(
            ("Type", "Passive"),
            ("Resistance", "10 kΩ"),
            ("Power Rating", "0.25 W"),
            ("Tolerance", "±1%"),
            ("Applications", "Feedback networks, dividers"),
        ),
        "specifications": (
            "Resistance: 10 kΩ ±1%\nPower rating: 0.25 W\nTolerance: ±1%\n"
            "Max working voltage: 250 V\nTemperature coefficient: ±100 ppm/°C"
        ),
        "applications": "Op-amp feedback, ADC reference dividers, precision filters.",
        "advantages": "Low noise, tight tolerance, good long-term stability.",
        "disadvantages": "Slightly higher cost than carbon film.",
        "common_uses": "Audio preamps, sensor signal chains, lab experiments.",
        "suggestion": "Prefer metal film 1% parts for measurement and op-amp feedback accuracy.",
    },
    {
        "name": "Electrolytic Capacitor 10µF 25V",
        "category": "Capacitor",
        "component_type": "Passive",
        "part_number": "EEU-FR1E100",
        "manufacturer": "Panasonic",
        "image_slug": "capacitor",
        "description": (
            "10 µF aluminum electrolytic capacitor for coupling, decoupling, "
            "and low-frequency filtering in power and audio circuits."
        ),
        "key_specs": _specs(
            ("Type", "Passive"),
            ("Capacitance", "10 µF"),
            ("Voltage Rating", "25 V"),
            ("Tolerance", "±20%"),
            ("Applications", "Filtering, coupling"),
        ),
        "specifications": (
            "Capacitance: 10 µF\nVoltage rating: 25 V\nTolerance: ±20%\n"
            "Polarized: yes\nTypical use: coupling / bulk decoupling"
        ),
        "applications": "Filtering, AC coupling, local bulk storage on low-current rails.",
        "advantages": "Useful capacitance in a small, inexpensive package.",
        "disadvantages": "Polarized; higher ESR than ceramics; finite lifetime.",
        "common_uses": "Audio coupling, regulator output support, sensor boards.",
        "suggestion": "Use 10 µF electrolytics for audio coupling or light bulk filtering under 25 V.",
    },
    {
        "name": "Ceramic Capacitor 100nF 50V",
        "category": "Capacitor",
        "component_type": "Passive",
        "part_number": "C0805C104K5RACTU",
        "manufacturer": "KEMET",
        "image_slug": "capacitor",
        "description": "100 nF MLCC used for high-frequency decoupling near IC power pins.",
        "key_specs": _specs(
            ("Type", "Passive"),
            ("Capacitance", "100 nF"),
            ("Voltage Rating", "50 V"),
            ("Dielectric", "X7R"),
            ("Applications", "Decoupling, bypass"),
        ),
        "specifications": (
            "Capacitance: 100 nF (0.1 µF)\nVoltage rating: 50 V\nDielectric: X7R\n"
            "Tolerance: ±10%\nPackage: 0805"
        ),
        "applications": "Power-rail decoupling, EMI filtering, digital bypass.",
        "advantages": "Tiny, low ESR, excellent HF response.",
        "disadvantages": "Capacitance shifts with DC bias and temperature.",
        "common_uses": "MCU Vcc pins, crystal support, SMPS filtering.",
        "suggestion": "Place a 100 nF ceramic next to every digital IC supply pin.",
    },
    {
        "name": "Electrolytic Capacitor 1000µF 25V",
        "category": "Capacitor",
        "component_type": "Passive",
        "part_number": "EEU-FR1E102",
        "manufacturer": "Panasonic",
        "image_slug": "capacitor",
        "description": "Large bulk electrolytic for power-supply energy storage and ripple reduction.",
        "key_specs": _specs(
            ("Type", "Passive"),
            ("Capacitance", "1000 µF"),
            ("Voltage Rating", "25 V"),
            ("Polarized", "Yes"),
            ("Applications", "Power supply filtering"),
        ),
        "specifications": (
            "Capacitance: 1000 µF\nVoltage rating: 25 V\nTolerance: ±20%\n"
            "Ripple current: ~1.5 A (typ.)\nPolarized: yes"
        ),
        "applications": "SMPS/linear output filtering, amplifier rails, rectifier reservoirs.",
        "advantages": "High capacitance per cost for bulk filtering.",
        "disadvantages": "Bulky, polarized, higher ESR than ceramics.",
        "common_uses": "Bench supplies, amplifier boards, motor-driver bulk caps.",
        "suggestion": "Use large electrolytics after rectifiers; always observe polarity.",
    },
    {
        "name": "1N4148 Switching Diode",
        "category": "Diode",
        "component_type": "Diode",
        "part_number": "1N4148",
        "manufacturer": "ON Semiconductor",
        "image_slug": "diode",
        "description": "Fast small-signal switching diode for logic, protection, and light rectification.",
        "key_specs": _specs(
            ("Type", "Switching diode"),
            ("VR max", "100 V"),
            ("IF avg", "200 mA"),
            ("VF", "~0.7 V"),
            ("Applications", "Clipping, protection"),
        ),
        "specifications": (
            "Max reverse voltage: 100 V\nAvg forward current: 200 mA\n"
            "Forward voltage: ~0.7 V @ 10 mA\nReverse recovery: ~4 ns"
        ),
        "applications": "Signal clipping, steering, small inductive snubbers.",
        "advantages": "Very fast, cheap, and ubiquitous.",
        "disadvantages": "Not for high-power rectification.",
        "common_uses": "Input protection, clamp networks, logic shaping.",
        "suggestion": "Pick 1N4148 for fast signal tasks; use 1N4007 for mains/power rectification.",
    },
    {
        "name": "1N4007 Rectifier Diode",
        "category": "Diode",
        "component_type": "Diode",
        "part_number": "1N4007",
        "manufacturer": "Vishay",
        "image_slug": "diode",
        "description": "1 A / 1000 V general-purpose rectifier for AC-to-DC conversion.",
        "key_specs": _specs(
            ("Type", "Rectifier"),
            ("VR max", "1000 V"),
            ("IF avg", "1 A"),
            ("VF", "~0.7–1.1 V"),
            ("Applications", "Power rectification"),
        ),
        "specifications": (
            "Max reverse voltage: 1000 V\nAvg forward current: 1 A\n"
            "Surge current: ~30 A\nPackage: DO-41"
        ),
        "applications": "Bridge rectifiers, reverse-polarity protection, freewheel diodes.",
        "advantages": "High voltage rating and robust for low-power supplies.",
        "disadvantages": "Slow recovery; not for high-frequency SMPS.",
        "common_uses": "Adapters, chargers, transformer secondaries.",
        "suggestion": "Use 1N4007 in 50/60 Hz rectifier bridges up to about 1 A.",
    },
    {
        "name": "5mm Red LED",
        "category": "LED",
        "component_type": "Diode",
        "part_number": "L-53SRD",
        "manufacturer": "Kingbright",
        "image_slug": "led",
        "description": "Standard 5 mm red LED for indicators and status lights in student projects.",
        "key_specs": _specs(
            ("Type", "Diode"),
            ("Forward Voltage", "2.0 V"),
            ("Current Rating", "20 mA"),
            ("Wavelength", "650 nm (Red)"),
            ("Applications", "Indicators, displays"),
        ),
        "specifications": (
            "Color: red (~650 nm)\nForward voltage: 1.8–2.2 V\n"
            "Forward current: 20 mA typical\nPackage: 5 mm T-1¾"
        ),
        "applications": "Power-on indicators, status displays, panel lamps.",
        "advantages": "Cheap, long life, easy to drive with a series resistor.",
        "disadvantages": "Needs current limiting; brightness depends on current.",
        "common_uses": "Breadboard demos, appliance panels, MCU indicators.",
        "suggestion": "From 5 V, pair with ~150–220 Ω for a bright, safe red LED.",
    },
    {
        "name": "5mm Blue LED",
        "category": "LED",
        "component_type": "Diode",
        "part_number": "C503B-BAN",
        "manufacturer": "Cree",
        "image_slug": "led",
        "description": "Bright blue 5 mm LED for high-visibility indicators and decorative lighting.",
        "key_specs": _specs(
            ("Type", "Diode"),
            ("Forward Voltage", "3.2 V"),
            ("Current Rating", "20 mA"),
            ("Color", "Blue"),
            ("Applications", "Indicators, lighting"),
        ),
        "specifications": (
            "Color: blue (~470 nm)\nForward voltage: 3.0–3.4 V\n"
            "Forward current: 20 mA typical\nPackage: 5 mm"
        ),
        "applications": "Status indicators, decorative lighting, RGB building blocks.",
        "advantages": "High visibility and modern appearance.",
        "disadvantages": "Higher VF than red/green; can be overly bright.",
        "common_uses": "Project enclosures, lab benches, RGB kits.",
        "suggestion": "From 5 V use ~100 Ω; from 3.3 V use a small resistor or constant-current drive.",
    },
    {
        "name": "2N2222A NPN Transistor",
        "category": "Transistor",
        "component_type": "Active",
        "part_number": "2N2222A",
        "manufacturer": "ON Semiconductor",
        "image_slug": "transistor",
        "description": "General-purpose NPN BJT for low-power switching and amplification.",
        "key_specs": _specs(
            ("Type", "NPN BJT"),
            ("VCEO", "40 V"),
            ("IC max", "800 mA"),
            ("hFE", "100–300"),
            ("Applications", "Switching, amplification"),
        ),
        "specifications": (
            "VCEO: 40 V\nIC: 800 mA max\nhFE: 100–300\n"
            "Power: 500 mW (TO-92)\nfT: ~300 MHz"
        ),
        "applications": "Relay/LED drivers, small-signal amplifiers, digital switching.",
        "advantages": "Easy to bias and well documented for teaching labs.",
        "disadvantages": "Needs base current; limited vs power MOSFETs.",
        "common_uses": "Arduino relay boards, load switching, audio pre-stages.",
        "suggestion": "Use 2N2222A for loads under a few hundred mA; use a MOSFET for higher current.",
    },
    {
        "name": "BC547 NPN Transistor",
        "category": "Transistor",
        "component_type": "Active",
        "part_number": "BC547B",
        "manufacturer": "Nexperia",
        "image_slug": "transistor",
        "description": "Low-noise NPN transistor popular for small-signal amplification up to ~100 mA.",
        "key_specs": _specs(
            ("Type", "NPN BJT"),
            ("VCEO", "45 V"),
            ("IC max", "100 mA"),
            ("Noise", "Low"),
            ("Applications", "Audio, sensing"),
        ),
        "specifications": (
            "VCEO: 45 V\nIC: 100 mA max\nhFE: 110–800 (group dependent)\nPower: 500 mW"
        ),
        "applications": "Audio preamps, sensor interfaces, small LED drivers.",
        "advantages": "Low cost and low noise for audio experiments.",
        "disadvantages": "Lower current than 2N2222A.",
        "common_uses": "Microphone preamps, classroom amplifier kits.",
        "suggestion": "Choose BC547 for low-noise audio; choose 2N2222A for stronger switching.",
    },
    {
        "name": "IRFZ44N N-Channel MOSFET",
        "category": "Transistor",
        "component_type": "Active",
        "part_number": "IRFZ44N",
        "manufacturer": "Infineon",
        "image_slug": "transistor",
        "description": "Power MOSFET for efficient high-current switching of motors and LED strips.",
        "key_specs": _specs(
            ("Type", "N-MOSFET"),
            ("VDS", "55 V"),
            ("ID", "~49 A"),
            ("RDS(on)", "~17.5 mΩ"),
            ("Applications", "Motor / PWM switching"),
        ),
        "specifications": (
            "VDS: 55 V\nID: ~49 A (with heatsink)\nRDS(on): ~17.5 mΩ @ 10 V\n"
            "Package: TO-220"
        ),
        "applications": "DC motor drivers, PWM dimming, battery switches.",
        "advantages": "Very low on-resistance and high current capability.",
        "disadvantages": "May not fully enhance at 3.3 V logic without a driver.",
        "common_uses": "Robotics, LED strip controllers, power switching.",
        "suggestion": "Drive gate near 10 V for full enhancement; add a gate resistor and pulldown.",
    },
    {
        "name": "Axial Inductor 100µH",
        "category": "Inductor",
        "component_type": "Passive",
        "part_number": "AIUR-06-101K",
        "manufacturer": "Abracon",
        "image_slug": "inductor",
        "description": "100 µH axial inductor for energy storage and filtering in DC-DC converters.",
        "key_specs": _specs(
            ("Type", "Passive"),
            ("Inductance", "100 µH"),
            ("Tolerance", "±10%"),
            ("Core", "Ferrite"),
            ("Applications", "Buck/boost filtering"),
        ),
        "specifications": (
            "Inductance: 100 µH ±10%\nDCR: ~0.3–0.8 Ω\n"
            "Saturation current: ~0.5–1.5 A\nMounting: axial"
        ),
        "applications": "Buck/boost converters, LC filters, rail chokes.",
        "advantages": "Essential magnetic energy storage for switching regulators.",
        "disadvantages": "Can saturate; radiates EMI if poorly placed.",
        "common_uses": "LM2596-style modules, lab SMPS trainers.",
        "suggestion": "Match inductance and saturation current to your converter design current.",
    },
    {
        "name": "Ferrite Bead 600Ω @ 100MHz",
        "category": "Inductor",
        "component_type": "Passive",
        "part_number": "BLM21PG600SN1",
        "manufacturer": "Murata",
        "image_slug": "inductor",
        "description": "Chip ferrite bead that suppresses RF noise on power and signal lines.",
        "key_specs": _specs(
            ("Type", "EMI bead"),
            ("Impedance", "600 Ω @ 100 MHz"),
            ("Package", "0805"),
            ("Rated current", "~1–2 A"),
            ("Applications", "EMI suppression"),
        ),
        "specifications": (
            "Impedance: 600 Ω @ 100 MHz\nDCR: ~0.1–0.3 Ω\n"
            "Rated current: ~1–2 A\nPackage: 0805"
        ),
        "applications": "MCU/RF module Vcc filtering, USB power lines.",
        "advantages": "Tiny footprint with effective HF attenuation.",
        "disadvantages": "Not a precision resonant inductor.",
        "common_uses": "Wi-Fi modules, mixed-signal boards, chargers.",
        "suggestion": "Add a ferrite bead on noisy digital or RF module power pins.",
    },
    {
        "name": "NE555 Timer IC",
        "category": "IC",
        "component_type": "Active",
        "part_number": "NE555P",
        "manufacturer": "Texas Instruments",
        "image_slug": "ic",
        "description": "Classic timer IC for delays, oscillators, PWM, and pulse generation.",
        "key_specs": _specs(
            ("Type", "Timer IC"),
            ("Supply", "4.5–16 V"),
            ("Output", "±200 mA"),
            ("Package", "DIP-8"),
            ("Applications", "Oscillators, timers"),
        ),
        "specifications": (
            "Supply: 4.5–16 V\nOutput current: ±200 mA\n"
            "Modes: monostable, astable\nPackage: DIP-8"
        ),
        "applications": "Clock generators, LED flashers, basic PWM.",
        "advantages": "Extremely well documented and flexible with RC timing.",
        "disadvantages": "Higher supply current than CMOS 7555 variants.",
        "common_uses": "Student labs, square-wave sources, toy circuits.",
        "suggestion": "Start with NE555 + two resistors and a capacitor for an astable clock.",
    },
    {
        "name": "LM358 Dual Op-Amp",
        "category": "IC",
        "component_type": "Active",
        "part_number": "LM358N",
        "manufacturer": "Texas Instruments",
        "image_slug": "ic",
        "description": "Dual single-supply op-amp for sensor amplification and signal conditioning.",
        "key_specs": _specs(
            ("Type", "Op-amp"),
            ("Channels", "2"),
            ("Supply", "3–32 V"),
            ("GBW", "~1 MHz"),
            ("Applications", "Amplifiers, filters"),
        ),
        "specifications": (
            "Channels: 2\nSupply: 3–32 V single\nInput offset: ~2–7 mV\n"
            "Gain-bandwidth: ~1 MHz\nSlew rate: ~0.3 V/µs"
        ),
        "applications": "Sensor amps, active filters, transducer front-ends.",
        "advantages": "Single-supply friendly and low cost.",
        "disadvantages": "Modest bandwidth; classic part is not rail-to-rail.",
        "common_uses": "Temperature/light sensor conditioners, entry audio preamps.",
        "suggestion": "Use LM358 for DC/slow sensor gain; pick a faster op-amp for audio fidelity.",
    },
    {
        "name": "ATmega328P Microcontroller",
        "category": "IC",
        "component_type": "Active",
        "part_number": "ATMEGA328P-PU",
        "manufacturer": "Microchip",
        "image_slug": "ic",
        "description": "8-bit AVR MCU used in Arduino Uno-class boards for embedded control projects.",
        "key_specs": _specs(
            ("Type", "MCU"),
            ("Flash", "32 KB"),
            ("SRAM", "2 KB"),
            ("Clock", "up to 20 MHz"),
            ("Applications", "Embedded control"),
        ),
        "specifications": (
            "Architecture: 8-bit AVR\nFlash: 32 KB\nSRAM: 2 KB\nEEPROM: 1 KB\n"
            "I/O: 23 lines\nPackage: DIP-28"
        ),
        "applications": "Embedded control, robotics, academic MCU labs.",
        "advantages": "Huge community, DIP-friendly, rich peripherals.",
        "disadvantages": "Limited vs modern 32-bit MCUs for heavy apps.",
        "common_uses": "Arduino Uno clones, custom controllers, Capstone boards.",
        "suggestion": "Ideal learning MCU; move to 32-bit parts when you need more RAM/speed.",
    },
    {
        "name": "LM7805 Voltage Regulator",
        "category": "IC",
        "component_type": "Active",
        "part_number": "LM7805CT",
        "manufacturer": "STMicroelectronics",
        "image_slug": "ic",
        "description": "Fixed +5 V linear regulator for simple protected digital/analog rails.",
        "key_specs": _specs(
            ("Type", "Regulator"),
            ("Output", "5 V"),
            ("Current", "up to 1 A"),
            ("Dropout", "~2 V"),
            ("Applications", "5 V power rails"),
        ),
        "specifications": (
            "Output: 5 V\nInput: ~7–25 V practical\nOutput current: up to 1 A\n"
            "Protection: thermal + short-circuit\nPackage: TO-220"
        ),
        "applications": "On-board 5 V from 9–12 V adapters, breadboard supplies.",
        "advantages": "Simple three-pin use with built-in protections.",
        "disadvantages": "Inefficient; needs heatsink at higher current.",
        "common_uses": "Arduino external supplies, sensor hubs, teaching PSU modules.",
        "suggestion": "Use LM7805 for quiet 5 V labs; prefer a buck converter for battery efficiency.",
    },
]


def get_connection(db_path: Path | str | None = None) -> sqlite3.Connection:
    """Return a SQLite connection with Row factory enabled."""
    path = Path(db_path) if db_path else DATABASE_PATH
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _table_columns(conn: sqlite3.Connection) -> set[str]:
    rows = conn.execute("PRAGMA table_info(components)").fetchall()
    return {row["name"] if isinstance(row, sqlite3.Row) else row[1] for row in rows}


def init_db(db_path: Path | str | None = None, seed: bool = True) -> None:
    """Create tables and insert sample components when empty or outdated."""
    path = Path(db_path) if db_path else DATABASE_PATH
    conn = get_connection(path)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS meta (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS components (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                component_type TEXT NOT NULL DEFAULT '',
                part_number TEXT NOT NULL,
                manufacturer TEXT NOT NULL,
                image_slug TEXT NOT NULL DEFAULT 'ic',
                description TEXT NOT NULL,
                key_specs TEXT NOT NULL DEFAULT '[]',
                specifications TEXT NOT NULL,
                applications TEXT NOT NULL,
                advantages TEXT NOT NULL,
                disadvantages TEXT NOT NULL,
                common_uses TEXT NOT NULL,
                suggestion TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """
        )

        columns = _table_columns(conn)
        required = {
            "component_type",
            "image_slug",
            "key_specs",
            "suggestion",
        }
        needs_upgrade = not required.issubset(columns)

        version_row = conn.execute(
            "SELECT value FROM meta WHERE key = 'schema_version'"
        ).fetchone()
        current_version = int(version_row["value"]) if version_row else 1

        if needs_upgrade or current_version < SCHEMA_VERSION:
            conn.execute("DROP TABLE IF EXISTS components")
            conn.execute(
                """
                CREATE TABLE components (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    component_type TEXT NOT NULL DEFAULT '',
                    part_number TEXT NOT NULL,
                    manufacturer TEXT NOT NULL,
                    image_slug TEXT NOT NULL DEFAULT 'ic',
                    description TEXT NOT NULL,
                    key_specs TEXT NOT NULL DEFAULT '[]',
                    specifications TEXT NOT NULL,
                    applications TEXT NOT NULL,
                    advantages TEXT NOT NULL,
                    disadvantages TEXT NOT NULL,
                    common_uses TEXT NOT NULL,
                    suggestion TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL DEFAULT (datetime('now'))
                )
                """
            )
            conn.execute(
                "INSERT OR REPLACE INTO meta(key, value) VALUES ('schema_version', ?)",
                (str(SCHEMA_VERSION),),
            )
            conn.commit()
            if seed:
                _seed_components(conn)
        else:
            conn.execute(
                "INSERT OR REPLACE INTO meta(key, value) VALUES ('schema_version', ?)",
                (str(SCHEMA_VERSION),),
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_components_category ON components(category)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_components_name ON components(name)"
            )
            conn.commit()
            if seed:
                count = conn.execute("SELECT COUNT(*) FROM components").fetchone()[0]
                if count == 0:
                    _seed_components(conn)
    finally:
        conn.close()


def _seed_components(conn: sqlite3.Connection) -> None:
    """Insert the built-in sample catalog."""
    sql = """
        INSERT INTO components (
            name, category, component_type, part_number, manufacturer, image_slug,
            description, key_specs, specifications, applications, advantages,
            disadvantages, common_uses, suggestion
        ) VALUES (
            :name, :category, :component_type, :part_number, :manufacturer, :image_slug,
            :description, :key_specs, :specifications, :applications, :advantages,
            :disadvantages, :common_uses, :suggestion
        )
    """
    conn.executemany(sql, SAMPLE_COMPONENTS)
    conn.commit()


def parse_key_specs(raw: str | None) -> list[dict[str, str]]:
    """Parse key_specs JSON into a list of {label, value} dicts."""
    if not raw:
        return []
    try:
        data = json.loads(raw)
        if not isinstance(data, list):
            return []
        result = []
        for item in data:
            if isinstance(item, dict) and "label" in item and "value" in item:
                result.append(
                    {"label": str(item["label"]), "value": str(item["value"])}
                )
        return result
    except json.JSONDecodeError:
        return []


def enrich_component(row: sqlite3.Row | dict[str, Any] | None) -> dict[str, Any] | None:
    """Convert a DB row into a template-friendly dict with parsed key specs."""
    if row is None:
        return None
    data = dict(row)
    data["key_spec_list"] = parse_key_specs(data.get("key_specs"))
    data["image_file"] = f"img/{data.get('image_slug', 'ic')}.svg"
    return data


def get_all_components(
    db_path: Path | str | None = None,
    category: str | None = None,
    search: str | None = None,
    sort: str | None = "category",
) -> list[sqlite3.Row]:
    """Return components filtered by optional category/search and sorted."""
    conn = get_connection(db_path)
    try:
        query = "SELECT * FROM components WHERE 1=1"
        params: list[Any] = []

        if category and category.strip() and category.strip().lower() != "all":
            query += " AND category = ?"
            params.append(category.strip())

        if search and search.strip():
            term = f"%{search.strip()}%"
            query += (
                " AND (name LIKE ? OR part_number LIKE ? OR manufacturer LIKE ?"
                " OR description LIKE ? OR category LIKE ? OR applications LIKE ?"
                " OR suggestion LIKE ?)"
            )
            params.extend([term, term, term, term, term, term, term])

        order_sql = SORT_OPTIONS.get(sort or "category", SORT_OPTIONS["category"])[0]
        query += f" ORDER BY {order_sql}"
        return list(conn.execute(query, params).fetchall())
    finally:
        conn.close()


def get_component_by_id(
    component_id: int, db_path: Path | str | None = None
) -> sqlite3.Row | None:
    """Fetch a single component by primary key."""
    conn = get_connection(db_path)
    try:
        return conn.execute(
            "SELECT * FROM components WHERE id = ?", (component_id,)
        ).fetchone()
    finally:
        conn.close()


def get_components_by_ids(
    ids: list[int], db_path: Path | str | None = None
) -> list[sqlite3.Row]:
    """Fetch multiple components preserving the requested id order."""
    if not ids:
        return []
    conn = get_connection(db_path)
    try:
        placeholders = ",".join("?" for _ in ids)
        rows = conn.execute(
            f"SELECT * FROM components WHERE id IN ({placeholders})", ids
        ).fetchall()
        by_id = {row["id"]: row for row in rows}
        return [by_id[i] for i in ids if i in by_id]
    finally:
        conn.close()


def get_category_counts(db_path: Path | str | None = None) -> list[sqlite3.Row]:
    """Return category names with component counts for the dashboard."""
    conn = get_connection(db_path)
    try:
        return list(
            conn.execute(
                """
                SELECT category, COUNT(*) AS count
                FROM components
                GROUP BY category
                ORDER BY category ASC
                """
            ).fetchall()
        )
    finally:
        conn.close()


def get_component_count(db_path: Path | str | None = None) -> int:
    """Return total number of components."""
    conn = get_connection(db_path)
    try:
        return int(conn.execute("SELECT COUNT(*) FROM components").fetchone()[0])
    finally:
        conn.close()


def get_showcase_components(db_path: Path | str | None = None) -> list[sqlite3.Row]:
    """Return poster-style showcase parts (resistor, capacitor, LED) when present."""
    preferred = (
        "Carbon Film Resistor 220Ω",
        "Electrolytic Capacitor 10µF 25V",
        "5mm Red LED",
    )
    conn = get_connection(db_path)
    try:
        rows = []
        for name in preferred:
            row = conn.execute(
                "SELECT * FROM components WHERE name = ?", (name,)
            ).fetchone()
            if row:
                rows.append(row)
        if len(rows) >= 2:
            return rows
        return list(
            conn.execute(
                "SELECT * FROM components ORDER BY category ASC, name ASC LIMIT 3"
            ).fetchall()
        )
    finally:
        conn.close()


def row_to_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    """Convert a sqlite3.Row to a plain dict with parsed helpers."""
    return enrich_component(row)
