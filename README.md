# hw5-fahda — hijri-deadline-mapper

## What the skill does

**hijri-deadline-mapper** converts a Gregorian deadline date to its Hijri
(Islamic calendar) equivalent, counts the number of Saudi business days
remaining from today (or a custom start date), and flags any Saudi public
holidays that fall within the range. It outputs a structured plain-text
report that an agent can narrate to the user.

## Why I chose it

Deadline tracking in a Saudi work context is genuinely non-trivial:

- The Saudi weekend is **Friday–Saturday**, not Saturday–Sunday.
- Official holidays include moon-sighting-dependent Eid days that shift
  ~11 days earlier every Gregorian year.
- Dates must be expressed in both Gregorian and Hijri.

A plain prose prompt cannot reliably do any of this. The Hijri conversion
requires a proper library (`hijri-converter`), the business-day count must
skip the correct weekend days and an accurate holiday list, and the output
table must be deterministically formatted. This makes the script genuinely
load-bearing, not decorative.

## How to use it

### Prerequisites

```bash
pip install hijri-converter
```

### Running directly

```bash
python .agents/skills/hijri-deadline-mapper/scripts/hijri_deadline_mapper.py \
    <DEADLINE_DATE> [START_DATE]
```

Both dates must be `YYYY-MM-DD`. `START_DATE` defaults to today.

### Example

```bash
python .agents/skills/hijri-deadline-mapper/scripts/hijri_deadline_mapper.py \
    2026-04-30 2026-04-26
```

### Via the agent (Claude Code)

Invoke the skill by name or through a natural-language request:

> "Convert April 30, 2026 to Hijri and tell me how many Saudi business days
> I have from today."

The agent reads `SKILL.md`, extracts the dates, runs the script, and
narrates the output.

## What the script does

`scripts/hijri_deadline_mapper.py`:

1. Parses the two date arguments.
2. Converts both dates from Gregorian to Hijri using `hijri-converter`.
3. Walks every day in the range and counts days that are **not** a
   Friday, Saturday, or hardcoded Saudi public holiday.
4. Collects every holiday that falls in the range for the holiday list.
5. Checks whether the deadline itself is a weekend or holiday and, if so,
   computes the next Saudi business day.
6. Emits a structured plain-text report with a separator-delimited table
   and inline warnings.

## Skill folder structure

```
.agents/
└─ skills/
   └─ hijri-deadline-mapper/
      ├─ SKILL.md
      ├─ scripts/
      │  └─ hijri_deadline_mapper.py
      └─ references/
         └─ saudi_holidays_notes.md
```

## What worked well

- `hijri-converter` is accurate and lightweight — no API calls needed.
- The hardcoded holiday dictionary is easy to audit and extend.
- The script's exit codes let the agent detect missing dependencies cleanly.
- The "next business day" suggestion makes the output immediately actionable.

## Limitations

- Eid dates are moon-sighting-dependent; projected dates may be off by ±1 day.
- Holiday data is hardcoded through 2027. Years 2028+ will trigger a warning.
- The skill does not handle multi-region Saudi schedules (e.g., NEOM or
  special economic zones may follow different rules).
- Unexpected royal decrees extending holidays are not reflected.

## Video walkthrough

<!-- Add your video link here -->
[Video demo link](YOUR_VIDEO_LINK_HERE)
