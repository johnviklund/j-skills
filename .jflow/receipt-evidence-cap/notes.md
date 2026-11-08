# Builder notes

- GPT-6.1 Sol · high builds this run, instead of the configured Opus 5.5 · high seat.
  Check therefore uses Opus 5.5 · high in a fresh session.
- Numbered defect bullets keep the parser's bullet format and give BROKEN rows a short reference.
  The 240-character defect cap covers everything after `Evidence:`, including run or traced.
- The change is text only, as Proof row 6 requires. Proof checks use temporary fixtures;
  no script or test changes are committed. Trial results and the skill-impact entry wait for done.
- The next three trial runs still need the human checks for evidence length and receipt size.
- All six Proof rows pass in builder checks. Rows 1–3 fail against Base; rows 4–6 stay green.
  The template fixture parses PROVED, BROKEN and BLOCKED once each, one defect, zero maybes and its sha.
- Baseline and final suites each pass: workflow 137 tests, checkup 41, jflow 8, all OK.
  Skill validation passes; Copilot lists jflow as enabled.
