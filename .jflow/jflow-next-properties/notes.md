# jflow-next-properties notes

- Spec session ran on google (`gemini-4-neon`, high) instead of the configured anthropic seat (`claude-opus-5-5`, medium).

## Build
- One test, `test_next_properties.py`, 164 lines. Each run builds a real git repo with random receipts, reruns with and without code changes, `Checks allowed:` and `Yes:` lines, Maybes, `[edge]`/`[use]`/untagged and carried defects, and Accepted lines in five variants (right, wrong sha, committed before the receipt, prose that only mentions the item, none). The oracle works out the expected step from what the generator built, not from `jflow.py`'s parsing. It compares only the step or the kind of human stop (approach, cap, stuck, edge, gate, done), not the card text.
- Default seed is fixed at 1, so the default run is deterministic and the mutants below fail every time. Run i uses seed SEED+i, so a printed seed reruns alone with `JFLOW_PROP_RUNS=1`.
- `jflow.py` is unchanged: 2,800 generated runs across seeds 1–600, 1000–1400, 2000–2400 and 3000–3400 all agree with `next` at HEAD. One disagreement turned up along the way (seed 1551): the oracle followed carried lineage only one hop, while `next` follows it back to the check the defect started in. That was an oracle bug, and `next` matches SKILL.md ("carried verdicts included").
- Mutants I ran, each one string replaced in a copy of `jflow.py` (each failed): the 2f8aaa8 `- <?none\b` Maybe filter (seed 13); 38b1e04 prose acceptance (seed 6); f6fb039 with the commit-order condition dropped (seed 6); `counted = len(receipts)` (17); `yes()` matching any `Yes:` (10); `allowed[0]` (43); `elif stuck and not edge` (33); `or defects:` sending `[edge]`-only to fix (33); `accepted_late` returning False (4).
- Default run: about 4.6 s for 50 runs. 80 runs take about 7.9 s. unittest reports one test however many runs it covers.
