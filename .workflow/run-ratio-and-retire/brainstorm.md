Command: workflow brainstorm run-ratio-and-retire
Created: 2026-10-23 · Claude Opus 5.5
Base:    43e006b
Inputs:  none
Status:  drafting

## Problem
Test suites in workflow repos grow a little every run and almost never shrink: cx-intelligence has 64.2k test lines against 83.6k code lines. The per-ticket ratio rule fires falsely (7 of 16 hits in the trial) and was absorbed by 13 waivers since 2026-10-17, while nothing at the end of a run removes tests that are no longer needed.

## Decisions
- D1 — The run-level gate compares tests net with code added, floor 100 — flags 1 of 26 recent runs; the net-code variant flags refactors (prototype: P1)

Docs read: none in scope (workflow skill only)
