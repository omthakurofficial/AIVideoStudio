# Map rules (distilled from production failures + remotion-maps technique notes)

Source inspiration: remotion-dev/skills `remotion-maps` (time-based reveal model: each country/marker triggers on
its own clock with constant durations — border 2.5 s, fill 1.0 s, label 0.7 s — instead of a slice of one global
reveal; long borders otherwise "flash by").

## Failures we have shipped before — never repeat
1. **Pile-up in the centre:** five icons all defaulted to Kathmandu coordinates. Fix: every place has explicit
   `lat`/`lon`; every non-place icon has `x`/`y` in a free column.
2. **Wrong geography:** New Delhi drawn east of Nepal because it was missing from the coordinate table. Fix: always
   pass coordinates in props; the renderer prefers props over its lookup table.
3. **Everything visible from frame 0:** viewers with sound off could not tell what was being said. Fix: entrance at
   the spoken word (renderer re-aligns to TTS word timestamps with a 100 ms lead).
4. **Stock photo covering callouts:** the PiP card sat on top of the "1950 Treaty" badge. Fix: reserve the stock slot.
5. **Placeholder subtitles:** "TIMELINE MARKER", "1,770 km Visa-Free Movement" under unrelated cards. Fix: always
   write a real `subtitle` prop or leave it empty.

## Column plan for 16:9
| zone | x range | use |
|---|---|---|
| left rail | 0.04–0.22 | callouts / stat cards, stacked top→bottom with ≥0.16 y spacing |
| map body | 0.22–0.78 | only regions, markers, routes |
| right rail | 0.78–0.96 | callouts; top-right reserved for stock PiP when present |

## Column plan for 9:16
Top band y 0.10–0.22 for headline, map body y 0.22–0.70, bottom card band y 0.70–0.80, captions below 0.82.
