#!/usr/bin/env python3
"""Batch-generate Agent-World demo videos from JSON conversation files."""
import os, sys, json, re
sys.path.insert(0, os.path.dirname(__file__))
from generate_video import generate_video_for

DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(DIR, "data")

DEMOS = [
    {"json": "flight.json",     "title": "Flight Refund Evaluation",  "file": "demo_flight.mp4",
     "l1": "Travel & Transportation", "l2": "Booking & Hospitality", "l3": "Flight and Stay Search Server"},
    {"json": "ecomm.json",      "title": "Ecomm Return Processing",   "file": "demo_ecomm.mp4",
     "l1": "Search & Information Retrieval", "l2": "API Gateway & Aggregation", "l3": "Ecomm MCP Server"},
    {"json": "notion.json",     "title": "Note Consistency Check",    "file": "demo_notion.mp4",
     "l1": "Document & Design", "l2": "Office & Text Processing", "l3": "Notion MCP Server"},
    {"json": "slack.json",      "title": "Compliance Inspection",     "file": "demo_slack.mp4",
     "l1": "Social Media & Community", "l2": "Social Network Integration", "l3": "Slack Workspace Automation Server"},
    {"json": "population.json", "title": "City Influence Index",      "file": "demo_population.mp4",
     "l1": "Search & Information Retrieval", "l2": "API Gateway & Aggregation", "l3": "Population Data Server"},
    {"json": "telecom.json",    "title": "Mobile Network Diagnosis",  "file": "demo_telecom.mp4",
     "l1": "Communication & General Utilities", "l2": "Messaging & Notification", "l3": "Telecom API MCP Server"},
    {"json": "twitter.json",    "title": "Engagement Value Audit",    "file": "demo_twitter.mp4",
     "l1": "Social Media & Community", "l2": "Social Network Integration", "l3": "Twitter MCP Server"},
    {"json": "gitHub.json",     "title": "Repository Management",    "file": "demo_github.mp4",
     "l1": "System & Cloud Infrastructure", "l2": "Cloud Platform Services", "l3": "GitHub"},
    {"json": "document.json",   "title": "Database Governance",       "file": "demo_document.mp4",
     "l1": "Document & Design", "l2": "Office & Text Processing", "l3": "Document Operations Server"},
]


def _strip_system_prompt(content):
    """Remove system prompt embedded in first user message (before --- separator)."""
    if "\n---\n" in content:
        before, after = content.split("\n---\n", 1)
        if "AVAILABLE TOOLS" in before or "You are an agent" in before:
            return after.strip()
    return content


def _format_fn_calls(raw):
    """Format function call JSON into readable fn(args) strings."""
    try:
        parsed = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return raw.strip() or None
    if isinstance(parsed, dict):
        parsed = [parsed]
    if not isinstance(parsed, list) or not parsed:
        return None
    parts = []
    for c in parsed:
        name = c.get("name", "?")
        params = c.get("parameters") or c.get("arguments") or {}
        args = ", ".join(
            f'{k}="{v}"' if isinstance(v, str) else f"{k}={v}"
            for k, v in params.items()
        )
        parts.append(f"{name}({args})")
    return "\n".join(parts)


def _clean_tool_output(content):
    """Strip infrastructure wrappers (<tool_response>, Cell execution) from tool output."""
    text = content

    if "<tool_response>" in text:
        idx_o = text.find("output=")
        idx_m = text.find(" meta=")
        if idx_o >= 0 and idx_m > idx_o:
            val = text[idx_o + 7 : idx_m].strip()
            if (val.startswith('"') and val.endswith('"')) or \
               (val.startswith("'") and val.endswith("'")):
                val = val[1:-1]
            while val.endswith("\\n"):
                val = val[:-2]
            return val.strip()
        return re.sub(r"</?tool_response>", "", text).strip()

    if text.lstrip().startswith("Cell execution finished"):
        m = re.search(r"stdout:\s*(.*?)(?:\nstderr:|\Z)", text, re.DOTALL)
        stdout_val = m.group(1).strip() if m else ""
        if stdout_val:
            return stdout_val
        m = re.search(r"'text/plain':\s*['\"](.+)['\"]}\]", text, re.DOTALL)
        if m:
            val = m.group(1).replace("\\'", "'")
            return val.strip()

    return text


def parse_conversation(filepath):
    """Parse a JSON conversation file into (role, content) video steps."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    messages = data.get("messages", [])
    steps = []
    prev_had_fn = False
    first_user = True

    for msg in messages:
        role, content = msg["role"], msg["content"]

        if role == "system":
            continue

        if role == "user":
            if prev_had_fn:
                steps.append(("tool", _clean_tool_output(content)))
            else:
                if first_user:
                    content = _strip_system_prompt(content)
                    first_user = False
                steps.append(("user", content))
            prev_had_fn = False
            continue

        # role == "assistant"
        prev_had_fn = False
        think_m = re.search(r"<think>(.*?)</think>", content, re.DOTALL)
        fn_m = re.search(
            r"<\|FunctionCallBegin\|>(.*?)<\|FunctionCallEnd\|>", content, re.DOTALL
        )
        tc_m = re.search(r"<tool_call>\s*(.*?)\s*</tool_call>", content, re.DOTALL)

        rest = content
        for m in (think_m, fn_m, tc_m):
            if m:
                rest = rest.replace(m.group(0), "", 1)
        rest = rest.strip()

        if think_m:
            t = think_m.group(1).strip()
            if t:
                steps.append(("think", t))

        fn_raw = None
        if fn_m:
            fn_raw = fn_m.group(1).strip()
        elif tc_m:
            fn_raw = tc_m.group(1).strip()

        if fn_raw is not None:
            formatted = _format_fn_calls(fn_raw)
            if formatted:
                steps.append(("fn", formatted))
            prev_had_fn = True

        if rest:
            steps.append(("answer", rest))

    return steps


if __name__ == "__main__":
    total = len(DEMOS)
    for i, demo in enumerate(DEMOS, 1):
        src = os.path.join(DATA_DIR, demo["json"])
        out = os.path.join(DIR, demo["file"])
        print(f"\n{'='*60}")
        print(f"[{i}/{total}] {demo['title']}  ->  {demo['file']}")
        print(f"  Source: {demo['json']}")
        print(f"{'='*60}")
        steps = parse_conversation(src)
        print(f"  Parsed {len(steps)} steps")
        generate_video_for(
            demo["title"], steps, out,
            l1=demo.get("l1", ""),
            l2=demo.get("l2", ""),
            l3=demo.get("l3", ""),
        )
    print(f"\n All {total} videos generated!")
