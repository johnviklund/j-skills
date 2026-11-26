"""Seats for jflow.py: the merged config, the locked rules and the secret check. Standard library, Python 3.9+."""
import json
import os
import re
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
FLOW = json.loads((SKILL / "flow.json").read_text("utf-8"))
STEPS = tuple(FLOW["steps"])
RULES = dict.fromkeys(("public_paid_needs_human", "checker_read_only", "no_secrets"), True)


def secret(v):
    if isinstance(v, dict):
        return any(secret(k) or secret(x) for k, x in v.items())
    if isinstance(v, (list, tuple)):
        return any(secret(x) for x in v)
    return isinstance(v, str) and bool(re.search(
        r"(?<![\w-])(?:sk-ant-|sk-(?=[\w-]*\d|\w+(?![\w-]))[A-Za-z0-9_-]{20,}|gh[pousr]_|AKIA)|[A-Za-z0-9_+/=]{40,}", v))


def record_value(v):
    if secret(v):
        raise SystemExit("secret-like argument refused")
    return v


def seats(repo, explicit):
    def bad(c, m):
        if c:
            raise ValueError(m)

    cfg, ext = {}, explicit or os.environ.get("JFLOW_CONFIG")
    for p in [SKILL / "config.json", repo / ".jflow/config.json"] + ([Path(ext)] if ext else []):
        if p == repo / ".jflow/config.json" and not p.exists():
            continue
        try:
            d = json.loads(p.read_text("utf-8"))
            bad(secret(d), "secret-like value refused")
            bad(not isinstance(d, dict) or type(d.get("schema_version")) is not int or d["schema_version"] != 1, "schema_version must be 1")
            bad(set(d) - {"schema_version", "seats", "rules", "different_vendors", "other_vendor", "mode"}, "unknown config field")
            rules = d.get("rules", {})
            bad(not isinstance(rules, dict), "rules must be an object")
            for r, on in rules.items():
                bad(r not in RULES or on is not True, "locked rule " + (r if r in RULES else "unknown"))
            bad("different_vendors" in d and type(d["different_vendors"]) is not bool, "different_vendors must be boolean")
            entries = d.get("seats", {})
            bad(not isinstance(entries, dict) or set(entries) - set(STEPS), "seats must name flow steps")
            for e in list(entries.values()) + ([d["other_vendor"]] if "other_vendor" in d else []):
                pend = [e]
                while pend:
                    s = pend.pop()
                    bad(not isinstance(s, dict) or set(s) != {"model", "vendor", "effort", "fallback"}, "each seat needs model, vendor, effort and fallback")
                    bad(any(not (isinstance(s[k], str) and s[k].strip()) for k in ("model", "vendor", "effort")), "seat model, vendor and effort must be nonempty strings")
                    if s["fallback"] is not None:
                        pend.append(s["fallback"])
            cfg.setdefault("seats", {}).update(entries)
            cfg.update({k: v for k, v in d.items() if k != "seats"})
        except (OSError, ValueError, RecursionError) as err:
            raise SystemExit(f"{p}: {err if type(err) is ValueError else 'cannot read valid config JSON'}")
    return cfg


def seat_for(repo, step, a):
    cfg, meta = seats(repo, a.config), FLOW["steps"][step]
    chosen = cfg["seats"].get(step, cfg["seats"][meta["seat"]])
    builder = a.builder_vendor or cfg["seats"]["build"]["vendor"]
    if step == "check" and cfg["different_vendors"] and chosen["vendor"] == builder:
        chosen = cfg["other_vendor"]
        if chosen["vendor"] == builder:
            raise SystemExit("other_vendor must differ from the builder vendor")
    return dict(chosen, **meta, step=step, rules=RULES)
