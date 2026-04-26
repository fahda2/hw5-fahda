---
name: hijri-deadline-mapper
description: >
  Converts a Gregorian deadline to its Hijri (Islamic calendar) equivalent,
  counts Saudi business days remaining (Friday–Saturday weekend, official
  Saudi public holidays included), flags any holiday conflicts, and produces
  a structured summary table. Use when the user asks how many Saudi working
  days remain until a deadline, wants a Gregorian-to-Hijri date conversion,
  or needs to know whether a target date collides with a Saudi holiday.
---

## When to use this skill

- The user mentions a deadline and asks how many Saudi working days remain.
- The user wants to convert a Gregorian date to Hijri (or vice versa).
- The user asks whether a specific date is a Saudi public holiday or a
  business day in Saudi Arabia.
- The user needs to plan around Eid al-Fitr, Eid al-Adha, Saudi National Day,
  or Founding Day.

## When NOT to use this skill

- The user is asking about a non-Saudi regional calendar (e.g., UAE, Kuwait,
  or a different Friday-only weekend).
- The user wants a full year-long project calendar or Gantt chart — this skill
  covers point-in-time deadline analysis, not multi-milestone planning.
- The user's date falls outside 2025–2027 and they need guaranteed accuracy
  for moon-sighting-dependent holidays (Eid dates). The script will warn them,
  but the model should reinforce the caution.

## Expected inputs

- **DEADLINE_DATE** (required): the target deadline in `YYYY-MM-DD` format.
- **START_DATE** (optional): the date to count from, in `YYYY-MM-DD` format.
  Defaults to today if omitted.

The user may provide these in natural language ("my deadline is March 15").
Extract the dates, convert them to `YYYY-MM-DD`, and pass them to the script.

## Step-by-step instructions

1. **Identify the dates** from the user's message.
   - Resolve relative references ("next Monday", "end of Q2") to explicit
     calendar dates before calling the script.
   - If no start date is given, omit it (the script defaults to today).

2. **Run the script**:
   ```
   python .agents/skills/hijri-deadline-mapper/scripts/hijri_deadline_mapper.py \
       <DEADLINE_DATE> [START_DATE]
   ```
   Example:
   ```
   python .agents/skills/hijri-deadline-mapper/scripts/hijri_deadline_mapper.py \
       2026-05-27 2026-04-26
   ```

3. **Capture the output**. The script prints:
   - Start-date block: Gregorian, Hijri, weekend/holiday flag.
   - Deadline block: Gregorian, Hijri, business-day status, holiday conflict.
   - Summary line: calendar days and Saudi business days remaining.
   - Holiday list: every Saudi public holiday that falls in the range.
   - Warnings: out-of-range year alerts and suggested adjusted deadline.

4. **Narrate the results** for the user:
   - Restate the deadline in both calendars.
   - Highlight the business-day count prominently.
   - If the deadline hits a holiday or weekend, recommend the next Saudi
     business day (the script computes this automatically).
   - If the year is outside 2025–2027, warn that Eid dates are approximate.

5. **Handle the cautious / decline case**:
   - If the date range spans years outside the hardcoded holiday table
     (before 2025 or after 2027), acknowledge this limitation clearly and
     tell the user the business-day count excludes holidays for those years.
   - Do not fabricate holiday dates. If uncertain, say so.

## Expected output format

The script produces a plain-text table. Present it verbatim inside a code
block, then follow with a one- or two-sentence plain-English summary and any
risk flags.

Example summary after the table:

> You have **18 Saudi business days** until your May 27 deadline (Eid al-Adha
> Day 1, 1447 AH). **Warning:** that date is an official Saudi holiday — the
> next Saudi business day is June 1, 2026 (Monday).

## Limitations

- Eid al-Fitr and Eid al-Adha dates are moon-sighting-dependent and may shift
  by ±1 day from the projected dates in the script.
- Holiday data is hardcoded through 2027. For 2028 and beyond the script will
  warn but still run; treat those results as approximate.
- This skill does not account for unexpected royal decrees extending holidays.
- Hijri conversion is performed by the `hijri-converter` Python library; the
  library must be installed (`pip install hijri-converter`).
