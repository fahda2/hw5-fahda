#!/usr/bin/env python3
"""
hijri_deadline_mapper.py

Converts a Gregorian deadline date to Hijri, computes Saudi business-day
offsets from today (or a custom start date), flags Saudi public holidays,
and prints a structured results table.

Usage:
    python hijri_deadline_mapper.py <DEADLINE_DATE> [START_DATE]

    DEADLINE_DATE : YYYY-MM-DD  (Gregorian)
    START_DATE    : YYYY-MM-DD  (Gregorian, defaults to today)

Exit codes:
    0  success
    1  bad arguments or date range out of supported holiday years
    2  dependency missing
"""

import sys
import warnings
from datetime import date, timedelta

# ---------------------------------------------------------------------------
# Dependency check
# ---------------------------------------------------------------------------
try:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        from hijri_converter import convert
except ImportError:
    print(
        "ERROR: 'hijri-converter' is not installed.\n"
        "Run:  pip install hijri-converter",
        file=sys.stderr,
    )
    sys.exit(2)

# ---------------------------------------------------------------------------
# Saudi public holidays (hardcoded through 2027)
# Key = Gregorian date, value = holiday name
# Sources: official Saudi announcements and approximate Hijri-to-Gregorian
# projections for moon-sighting-dependent holidays (marked with ~).
# ---------------------------------------------------------------------------
SAUDI_HOLIDAYS: dict[date, str] = {
    # --- 2025 ---
    date(2025, 2, 22): "Founding Day",
    date(2025, 2, 23): "Founding Day (observed)",
    date(2025, 3, 30): "Eid al-Fitr (eve)",       # ~
    date(2025, 3, 31): "Eid al-Fitr Day 1",        # ~
    date(2025, 4, 1):  "Eid al-Fitr Day 2",        # ~
    date(2025, 4, 2):  "Eid al-Fitr Day 3",        # ~
    date(2025, 6, 5):  "Arafat Day",               # ~
    date(2025, 6, 6):  "Eid al-Adha Day 1",        # ~
    date(2025, 6, 7):  "Eid al-Adha Day 2",        # ~
    date(2025, 6, 8):  "Eid al-Adha Day 3",        # ~
    date(2025, 9, 23): "Saudi National Day",
    # --- 2026 ---
    date(2026, 2, 22): "Founding Day",
    date(2026, 3, 20): "Eid al-Fitr (eve)",        # ~
    date(2026, 3, 21): "Eid al-Fitr Day 1",        # ~
    date(2026, 3, 22): "Eid al-Fitr Day 2",        # ~
    date(2026, 3, 23): "Eid al-Fitr Day 3",        # ~
    date(2026, 5, 26): "Arafat Day",               # ~
    date(2026, 5, 27): "Eid al-Adha Day 1",        # ~
    date(2026, 5, 28): "Eid al-Adha Day 2",        # ~
    date(2026, 5, 29): "Eid al-Adha Day 3",        # ~
    date(2026, 9, 23): "Saudi National Day",
    # --- 2027 ---
    date(2027, 2, 22): "Founding Day",
    date(2027, 3, 10): "Eid al-Fitr (eve)",        # ~
    date(2027, 3, 11): "Eid al-Fitr Day 1",        # ~
    date(2027, 3, 12): "Eid al-Fitr Day 2",        # ~
    date(2027, 3, 13): "Eid al-Fitr Day 3",        # ~
    date(2027, 5, 16): "Arafat Day",               # ~
    date(2027, 5, 17): "Eid al-Adha Day 1",        # ~
    date(2027, 5, 18): "Eid al-Adha Day 2",        # ~
    date(2027, 5, 19): "Eid al-Adha Day 3",        # ~
    date(2027, 9, 23): "Saudi National Day",
}

SUPPORTED_YEARS = range(2025, 2028)  # inclusive

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def is_saudi_weekend(d: date) -> bool:
    """Friday=4, Saturday=5 in Python's weekday() (Mon=0)."""
    return d.weekday() in (4, 5)


def is_saudi_holiday(d: date) -> str | None:
    """Return holiday name or None."""
    return SAUDI_HOLIDAYS.get(d)


def is_saudi_business_day(d: date) -> bool:
    return not is_saudi_weekend(d) and d not in SAUDI_HOLIDAYS


def count_business_days(start: date, end: date) -> int:
    """Count Saudi business days from start (exclusive) to end (inclusive)."""
    if end < start:
        return 0
    count = 0
    cursor = start + timedelta(days=1)
    while cursor <= end:
        if is_saudi_business_day(cursor):
            count += 1
        cursor += timedelta(days=1)
    return count


def gregorian_to_hijri(d: date) -> str:
    h = convert.Gregorian(d.year, d.month, d.day).to_hijri()
    return f"{h.year}/{h.month:02d}/{h.day:02d} AH"


def day_name(d: date) -> str:
    return d.strftime("%A")


def parse_date(s: str, label: str) -> date:
    try:
        return date.fromisoformat(s)
    except ValueError:
        print(f"ERROR: {label} '{s}' is not a valid YYYY-MM-DD date.", file=sys.stderr)
        sys.exit(1)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    args = sys.argv[1:]
    if not args or len(args) > 2:
        print(
            "Usage: python hijri_deadline_mapper.py <DEADLINE_DATE> [START_DATE]\n"
            "Example: python hijri_deadline_mapper.py 2026-05-27 2026-04-26",
            file=sys.stderr,
        )
        sys.exit(1)

    deadline = parse_date(args[0], "DEADLINE_DATE")
    start = parse_date(args[1], "START_DATE") if len(args) == 2 else date.today()

    # --- Year-range guard ---
    warn_years: list[str] = []
    for d in (deadline, start):
        if d.year not in SUPPORTED_YEARS:
            warn_years.append(str(d.year))

    # --- Compute ---
    deadline_hijri = gregorian_to_hijri(deadline)
    start_hijri = gregorian_to_hijri(start)
    biz_days = count_business_days(start, deadline)
    total_days = (deadline - start).days

    deadline_weekend = is_saudi_weekend(deadline)
    deadline_holiday = is_saudi_holiday(deadline)
    start_weekend = is_saudi_weekend(start)
    start_holiday = is_saudi_holiday(start)

    # --- Output ---
    W = 22  # column width

    def row(label: str, value: str) -> str:
        return f"  {label:<{W}} {value}"

    sep = "  " + "-" * (W + 35)

    print()
    print("=" * 60)
    print("  HIJRI DEADLINE MAPPER — Saudi Business Day Report")
    print("=" * 60)

    print("\n  [ Start Date ]")
    print(row("Gregorian:", f"{start}  ({day_name(start)})"))
    print(row("Hijri:", start_hijri))
    if start_weekend:
        print(row("Note:", "⚠  Start date is a Saudi weekend day"))
    if start_holiday:
        print(row("Note:", f"⚠  Start date is '{start_holiday}'"))

    print("\n  [ Deadline ]")
    print(row("Gregorian:", f"{deadline}  ({day_name(deadline)})"))
    print(row("Hijri:", deadline_hijri))
    print(row("Saudi Business Day?", "YES" if not deadline_weekend and not deadline_holiday else "NO"))
    if deadline_weekend:
        print(row("Note:", "⚠  Deadline falls on a Saudi weekend (Fri/Sat)"))
    if deadline_holiday:
        print(row("Note:", f"⚠  Deadline falls on '{deadline_holiday}'"))

    print(sep)
    print(row("Calendar days remaining:", str(total_days)))
    print(row("Saudi business days:", str(biz_days)))
    print(sep)

    # --- Holiday scan between start and deadline ---
    holidays_in_range: list[tuple[date, str]] = []
    cursor = start + timedelta(days=1)
    while cursor <= deadline:
        h = is_saudi_holiday(cursor)
        if h:
            holidays_in_range.append((cursor, h))
        cursor += timedelta(days=1)

    if holidays_in_range:
        print(f"\n  [ Saudi Holidays between {start} and {deadline} ]")
        for hdate, hname in holidays_in_range:
            print(f"    • {hdate}  ({day_name(hdate)})  —  {hname}")
    else:
        print("\n  [ No Saudi public holidays in this range ]")

    # --- Warnings ---
    print()
    if warn_years:
        years_str = ", ".join(set(warn_years))
        print(
            f"  ⚠  WARNING: Holiday data is only hardcoded through 2027.\n"
            f"     Year(s) {years_str} may have missing holidays — treat results with caution."
        )
    if deadline_weekend or deadline_holiday:
        # Suggest next business day
        suggestion = deadline + timedelta(days=1)
        while not is_saudi_business_day(suggestion):
            suggestion += timedelta(days=1)
        print(
            f"  ⚠  SUGGESTION: Consider moving the deadline to the next\n"
            f"     Saudi business day: {suggestion}  ({day_name(suggestion)})"
        )
    if total_days < 0:
        print("  ⚠  The deadline is in the past relative to the start date.")

    print()


if __name__ == "__main__":
    main()
