"""Validate this skill pack without Git or a machine-specific skill installation.

Scope: skills/*/SKILL.md, skills/*/references/**/*.md, root *.md,
validation/**/*.md, and validation/behavior-cases.json (fingerprint only).
Markdown support is deliberately limited to inline links with simple destinations
(including <angle-bracket paths> and optional titles), plus backticked references/
paths inside skills only. Fenced code is ignored. Reference-style links, HTML, balanced parentheses,
anchors and external URL availability are not validated. This is not a CommonMark
parser, behavioral evaluation, or client-import test.
"""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import re
import sys
from urllib.parse import unquote, urlsplit

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is required; install requirements-dev.txt with this Python interpreter.")


VERSION = "1.0.0"
SCHEMA_VERSION = 1
# Skill manifest format limits; not deployment or user-specific configuration.
NAME_LIMIT = 64
DESCRIPTION_LIMIT = 1024
ALLOWED_FIELDS = {"name", "description", "license", "compatibility", "allowed-tools", "metadata"}
INLINE_LINK = re.compile(r"!?\[[^\]\n]*\]\(\s*(?:<([^>\n]+)>|([^\s()]+))(?:\s+[\"'][^\n]*?[\"'])?\s*\)")
REFERENCE_PATH = re.compile(r"`(references/[^`\n]+)`")


class UniqueLoader(yaml.SafeLoader):
    """Keep SafeLoader semantics while rejecting ambiguous duplicate keys."""


def unique_mapping(loader, node, deep=False):
    mapping = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        try:
            if key in mapping:
                raise yaml.constructor.ConstructorError(
                    None, None, "duplicate mapping key", key_node.start_mark)
            mapping[key] = loader.construct_object(value_node, deep=deep)
        except TypeError as exc:
            raise yaml.constructor.ConstructorError(
                None, None, "unhashable mapping key", key_node.start_mark) from exc
    return mapping


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def check_manifest(text, directory, errors):
    lines = text.splitlines()
    if not lines or lines[0] != "---" or "---" not in lines[1:]:
        errors.append("missing or unclosed YAML frontmatter")
        return
    end = lines.index("---", 1)
    try:
        data = yaml.load("\n".join(lines[1:end]), Loader=UniqueLoader)
    except yaml.YAMLError as exc:
        errors.append("invalid YAML: " + (getattr(exc, "problem", None) or type(exc).__name__))
        return
    if not isinstance(data, dict):
        errors.append("frontmatter must be a mapping")
        return
    if any(key not in ALLOWED_FIELDS for key in data):
        errors.append("unexpected frontmatter field")
    for field, limit in [("name", NAME_LIMIT), ("description", DESCRIPTION_LIMIT)]:
        value = data.get(field)
        if not isinstance(value, str) or not value.strip() or len(value) > limit:
            errors.append(f"{field} must be a nonempty string of at most {limit} characters")
    name = data.get("name")
    if isinstance(name, str):
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
            errors.append("name must use lowercase letters, digits and single hyphens")
        if name != directory:
            errors.append("name must match its skill directory")
    for field in ("license", "compatibility", "allowed-tools"):
        if field in data and (not isinstance(data[field], str) or not data[field].strip()):
            errors.append(f"{field} must be a nonempty string")
    if "metadata" in data:
        metadata = data["metadata"]
        if not isinstance(metadata, dict) or any(
            not isinstance(key, str) or not key.strip() or not isinstance(value, str)
            or not value.strip() for key, value in metadata.items()
        ):
            errors.append("metadata keys and values must be nonempty strings")
    if not "\n".join(lines[end + 1:]).strip():
        errors.append("skill body must not be empty")


def link_destinations(text, include_references):
    """Skip fenced examples rather than treating their sample links as live."""
    fence = None
    for line in text.splitlines():
        marker = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        if marker:
            token = marker[1]
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
            continue
        if fence:
            continue
        for match in INLINE_LINK.finditer(line):
            yield match[1] or match[2]
        if include_references:
            yield from REFERENCE_PATH.findall(line)


def check_links(text, source, boundary, errors, include_references=False):
    count = 0
    for destination in set(link_destinations(text, include_references)):
        normalized = unquote(destination).replace("\\", "/")
        if normalized.startswith("/") or re.match(r"^[a-zA-Z]:", normalized) or normalized.lower().startswith("file:"):
            errors.append(f"absolute filesystem link is not portable: {destination}")
            continue
        parsed = urlsplit(destination)
        if parsed.scheme or parsed.netloc or not parsed.path:
            continue
        count += 1
        path = unquote(parsed.path).replace("\\", "/")
        target = (source.parent / path).resolve()
        if Path(path).is_absolute() or not target.is_relative_to(boundary):
            errors.append(f"link escapes allowed directory: {destination}")
        elif not target.exists():
            errors.append(f"missing local link: {destination}")
    return count


def validate(root):
    root = root.resolve()
    report = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "validator": {"version": VERSION, "sha256": sha256(Path(__file__).read_bytes())},
        "runtime": {"python": platform.python_version(), "pyyaml": yaml.__version__},
        "files": {}, "skill_count": 0, "link_count": 0, "errors": [],
        "limitations": __doc__.strip(),
    }
    errors = report["errors"]
    skills = root / "skills"
    directories = sorted(skills.iterdir()) if skills.is_dir() else []
    directories = [path for path in directories if path.is_dir() and not path.name.startswith(".")]
    if not directories:
        errors.append("skills: missing or empty skill collection")
    inputs = {}
    for directory in directories:
        entry = directory / "SKILL.md"
        if not directory.resolve().is_relative_to(root):
            errors.append(f"skills/{directory.name}: directory escapes repository")
            continue
        if not entry.is_file():
            errors.append(f"skills/{directory.name}/SKILL.md: missing skill entrypoint")
            continue
        report["skill_count"] += 1
        inputs[entry] = directory.resolve()
        for reference in (directory / "references").rglob("*.md"):
            inputs[reference] = directory.resolve()
    for document in [*root.glob("*.md"), *(root / "validation").rglob("*.md")]:
        inputs[document] = root
    cases = root / "validation" / "behavior-cases.json"
    if cases.exists():
        inputs[cases] = root
    for path, boundary in sorted(inputs.items()):
        name = path.relative_to(root).as_posix()
        local_errors = []
        if not path.resolve().is_relative_to(boundary):
            errors.append(f"{name}: file escapes allowed directory")
            continue
        try:
            raw = path.read_bytes()
            report["files"][name] = sha256(raw)
            text = raw.decode("utf-8-sig")
            if path.name == "SKILL.md":
                check_manifest(text, path.parent.name, local_errors)
            if path.suffix.lower() == ".md":
                report["link_count"] += check_links(
                    text, path, boundary, local_errors, include_references=boundary != root)
        except (OSError, UnicodeError, ValueError) as exc:
            local_errors.append(f"cannot validate file: {type(exc).__name__}")
        errors.extend(f"{name}: {message}" for message in local_errors)
    manifest = json.dumps(report["files"], sort_keys=True, ensure_ascii=False).encode("utf-8")
    report["fingerprint"] = sha256(manifest)
    report["ok"] = not errors
    return report


def check_snapshot(report, snapshot):
    try:
        previous = json.loads(snapshot.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError):
        report["errors"].append("snapshot: cannot read valid JSON")
        return
    keys = ("schema_version", "validator", "runtime", "files", "fingerprint")
    if not isinstance(previous, dict) or previous.get("ok") is not True:
        report["errors"].append("snapshot: not a successful validation report")
    elif any(previous.get(key) != report[key] for key in keys):
        report["errors"].append("snapshot: stale (inputs, validator or runtime changed)")


def check_behavior(report, record_path, root):
    """Check saved record integrity, never infer whether an answer is correct."""
    print("Behavior record integrity/freshness only; not a behavioral retest or automatic grading.")
    errors = report["errors"]
    cases_name = "validation/behavior-cases.json"
    expected = {name: digest for name, digest in report["files"].items()
                if name.startswith("skills/") or name == cases_name}
    skill_names = {path.relative_to(root).as_posix() for path in (root / "skills").rglob("*.md")}
    if set(expected) != skill_names | {cases_name}:
        errors.append("behavior: missing fingerprint for a skill Markdown file or case definitions")
        return
    try:
        # Only fixed in-repository sources are read; record-provided paths are data.
        record = json.loads(record_path.read_text(encoding="utf-8"))
        definitions = json.loads((root / cases_name).read_text(encoding="utf-8"))
        if not isinstance(record, dict) or not isinstance(definitions, dict):
            raise ValueError("records must be objects")
        if record.get("schema_version") != SCHEMA_VERSION or definitions.get("schema_version") != SCHEMA_VERSION:
            raise ValueError("unsupported schema version")
        if record.get("source_files") != expected:
            errors.append("behavior: stale source hashes or source file set")
        cases, results = definitions.get("cases"), record.get("results")
        if not isinstance(cases, list) or not cases or not isinstance(results, list):
            raise ValueError("cases and results must be lists; cases must not be empty")
        expected_turns = {}
        for case in cases:
            if not isinstance(case, dict) or not isinstance(case.get("id"), str) or not case["id"]:
                raise ValueError("invalid case id")
            turns = case.get("user_turns")
            if case["id"] in expected_turns or not isinstance(turns, list) or not turns or any(
                not isinstance(turn, str) or not turn.strip() for turn in turns
            ):
                raise ValueError("duplicate case id or invalid user turns")
            expected_turns[case["id"]] = len(turns)
        seen, total = set(), 0
        for result in results:
            if not isinstance(result, dict) or not isinstance(result.get("case_id"), str):
                raise ValueError("invalid result case id")
            case_id, turns = result["case_id"], result.get("assistant_turns")
            if case_id in seen or case_id not in expected_turns:
                raise ValueError("duplicate or unexpected result case id")
            seen.add(case_id)
            if not isinstance(turns, list) or len(turns) != expected_turns[case_id] or any(
                not isinstance(turn, str) or not turn.strip() for turn in turns
            ):
                raise ValueError("assistant turns do not match user turns")
            total += len(turns)
            verdict = result.get("verdict")
            if verdict not in ("pass", "fail", "not_run"):
                raise ValueError("unknown verdict")
            if verdict != "pass":
                errors.append(f"behavior: {case_id} has recorded verdict {verdict}")
        if seen != set(expected_turns):
            raise ValueError("missing case results")
        for field, count in (("case_count", len(cases)), ("assistant_turn_count", total)):
            if type(record.get(field)) is not int or record[field] != count:
                raise ValueError(f"incorrect {field}")
    except (OSError, UnicodeError, ValueError) as exc:
        errors.append(f"behavior: invalid record or definitions ({type(exc).__name__}: {exc})")


def write_report(report, output, root, force):
    output = output.resolve()
    if output.exists() and not force:
        raise ValueError("output already exists; use --force to refresh a report")
    protected = {Path(__file__).resolve(), *(root / name for name in report["files"])}
    relative = output.relative_to(root) if output.is_relative_to(root) else None
    if output in protected or output.suffix.lower() != ".json" or (
        relative is not None and relative.parts[0] in {"skills", "scripts", "tests"}
    ):
        raise ValueError("output must be a JSON report, not an input or source file")
    if output.exists():
        try:
            old = json.loads(output.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, ValueError) as exc:
            raise ValueError("--force can only replace an existing validator report") from exc
        if not isinstance(old, dict) or not {"validator", "schema_version", "files"} <= old.keys():
            raise ValueError("--force can only replace an existing validator report")
    with output.open("w" if force else "x", encoding="utf-8", newline="\n") as stream:
        json.dump(report, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, help="Explicit JSON report path; parent must exist")
    parser.add_argument("--force", action="store_true", help="Refresh an existing validator report")
    parser.add_argument("--check-snapshot", type=Path, help="Fail if saved provenance differs")
    parser.add_argument("--check-behavior", type=Path, help="Check saved record integrity, not behavior")
    args = parser.parse_args()
    if args.force and not args.output:
        parser.error("--force requires --output")
    try:
        report = validate(args.root)
        if args.check_snapshot:
            check_snapshot(report, args.check_snapshot)
        if args.check_behavior:
            check_behavior(report, args.check_behavior, args.root.resolve())
        report["ok"] = not report["errors"]
        if args.output:
            write_report(report, args.output, args.root.resolve(), args.force)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    for error in report["errors"]:
        print(f"ERROR: {error}")
    status = "PASS" if report["ok"] else "FAIL"
    print(f"{status}: {report['skill_count']} skills, {report['link_count']} local links, "
          f"{len(report['files'])} fingerprinted files")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
