"""Isolated CLI regression tests; run with python -m unittest discover -s tests."""

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "validate_skills.py"
VALID = "---\nname: sample\ndescription: A useful skill.\nmetadata:\n  language: zh-CN\n---\n\n# Sample\n"


class ValidatorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.skill = self.root / "skills" / "sample" / "SKILL.md"
        self.skill.parent.mkdir(parents=True)
        self.skill.write_text(VALID, encoding="utf-8")

    def run_cli(self, *args, root=True, script=SCRIPT, cwd=None):
        command = [sys.executable, str(script)]
        if root:
            command += ["--root", str(self.root)]
        return subprocess.run(command + list(args), cwd=cwd or self.root,
                              text=True, encoding="utf-8", capture_output=True)

    def report(self):
        output = self.root / "result.json"
        result = self.run_cli("--output", str(output))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = json.loads(output.read_text(encoding="utf-8"))
        output.unlink()
        return report

    def assert_invalid(self, content, diagnostic):
        self.skill.write_text(content, encoding="utf-8")
        result = self.run_cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(diagnostic, result.stdout + result.stderr)
        self.assertNotIn("Traceback", result.stdout + result.stderr)

    def test_valid_zip_tree_and_report_provenance(self):
        report = self.report()
        self.assertTrue(report["ok"])
        self.assertEqual(report["schema_version"], 1)
        self.assertEqual(report["skill_count"], 1)
        self.assertIn("skills/sample/SKILL.md", report["files"])
        self.assertEqual(len(report["fingerprint"]), 64)
        self.assertEqual(len(report["validator"]["sha256"]), 64)
        self.assertIn("pyyaml", report["runtime"])
        self.assertTrue(report["generated_at"].endswith("+00:00"))

    def test_invalid_yaml_is_reported_without_traceback(self):
        self.assert_invalid("---\nname: [broken\n---\nBody", "YAML")

    def test_empty_or_wrong_type_required_fields(self):
        for field, value in [("name", "''"), ("description", "''"),
                             ("description", "[]"), ("description", "'   '")]:
            with self.subTest(field=field, value=value):
                other = "description: useful" if field == "name" else "name: sample"
                self.assert_invalid(f"---\n{field}: {value}\n{other}\n---\nBody", field)

    def test_duplicate_yaml_keys_at_any_depth(self):
        for content in [VALID.replace("name: sample", "name: sample\nname: sample"),
                        VALID.replace("  language: zh-CN", "  language: zh-CN\n  language: en")]:
            with self.subTest(content=content):
                self.assert_invalid(content, "duplicate")

    def test_name_must_match_directory_and_naming_rules(self):
        self.assert_invalid(VALID.replace("name: sample", "name: different"), "directory")
        self.assert_invalid(VALID.replace("name: sample", "name: Wrong_Name"), "name")

    def test_field_lengths_unknown_fields_and_metadata_strings(self):
        self.assert_invalid(VALID.replace("name: sample", "name: " + "a" * 65), "name")
        self.assert_invalid(VALID.replace("A useful skill.", "a" * 1025), "description")
        self.assert_invalid(VALID.replace("language: zh-CN", "language: 123"), "metadata")
        self.assert_invalid(VALID.replace("metadata:", "unexpected: value\nmetadata:"), "unexpected")

    def test_missing_frontmatter_and_body(self):
        self.assert_invalid("# No frontmatter", "frontmatter")
        self.assert_invalid(VALID.split("# Sample")[0], "body")

    def test_missing_or_empty_skill_collection(self):
        shutil.rmtree(self.root / "skills")
        self.assertNotEqual(self.run_cli().returncode, 0)
        (self.root / "skills").mkdir()
        self.assertNotEqual(self.run_cli().returncode, 0)
        (self.root / "skills" / "missing").mkdir()
        self.assertIn("SKILL.md", self.run_cli().stdout)

    def test_missing_and_escaping_references(self):
        self.assert_invalid(VALID + "Read `references/missing.md`.", "missing")
        (self.root / "outside.md").write_text("outside", encoding="utf-8")
        self.assert_invalid(VALID + "[outside](../../outside.md)", "escapes")
        self.assert_invalid(VALID + "Read `references/../../../outside.md`.", "escapes")

    def test_absolute_filesystem_links_are_rejected_cross_platform(self):
        for destination in ("C:/outside.md", "file:///outside.md", "//server/share", "/outside.md"):
            with self.subTest(destination=destination):
                self.assert_invalid(VALID + f"[outside]({destination})", "absolute")

    def test_local_doc_links_and_external_links(self):
        (self.root / "README.md").write_text(
            "[skill](skills/sample/SKILL.md#sample) [web](https://example.com)\n"
            "[mail](mailto:user@example.com) [anchor](#heading)", encoding="utf-8")
        self.assertEqual(self.report()["link_count"], 1)
        (self.root / "README.md").write_text("[missing](absent.md)", encoding="utf-8")
        self.assertNotEqual(self.run_cli().returncode, 0)

    def test_backticked_reference_paths_only_checked_inside_skills(self):
        (self.root / "README.md").write_text(
            "A skill may contain `references/example.md`.", encoding="utf-8")
        self.assertEqual(self.run_cli().returncode, 0)

    def test_reference_hashes_change_fingerprint(self):
        refs = self.skill.parent / "references"
        refs.mkdir()
        ref = refs / "guide.md"
        ref.write_text("First", encoding="utf-8")
        self.skill.write_text(VALID + "[guide](references/guide.md)", encoding="utf-8")
        first = self.report()
        ref.write_text("Second", encoding="utf-8")
        second = self.report()
        self.assertNotEqual(first["fingerprint"], second["fingerprint"])
        self.assertIn("skills/sample/references/guide.md", second["files"])

    def test_snapshot_current_then_stale_and_malformed(self):
        snapshot = self.root / "snapshot.json"
        self.assertEqual(self.run_cli("--output", str(snapshot)).returncode, 0)
        self.assertEqual(self.run_cli("--check-snapshot", str(snapshot)).returncode, 0)
        self.skill.write_text(VALID + "Changed", encoding="utf-8")
        result = self.run_cli("--check-snapshot", str(snapshot))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("stale", result.stdout)
        snapshot.write_text("[]", encoding="utf-8")
        self.assertNotEqual(self.run_cli("--check-snapshot", str(snapshot)).returncode, 0)

    def test_default_root_independent_of_cwd(self):
        scripts = self.root / "scripts"
        scripts.mkdir()
        copy = scripts / SCRIPT.name
        shutil.copyfile(SCRIPT, copy)
        result = self.run_cli(root=False, script=copy, cwd=self.skill.parent)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_output_never_overwrites_existing_file(self):
        result = self.run_cli("--output", str(self.skill))
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.skill.read_text(encoding="utf-8"), VALID)
        self.assertIn("exists", result.stdout + result.stderr)

    def test_force_does_not_replace_arbitrary_json(self):
        unrelated = self.root / "config.json"
        unrelated.write_text('{"setting": true}', encoding="utf-8")
        self.assertNotEqual(self.run_cli("--output", str(unrelated), "--force").returncode, 0)
        self.assertEqual(unrelated.read_text(encoding="utf-8"), '{"setting": true}')

    def test_snapshot_rejects_changed_validator_runtime_or_added_doc(self):
        snapshot = self.root / "snapshot.json"
        report = self.report()
        for field in ("validator", "runtime"):
            with self.subTest(field=field):
                changed = dict(report)
                changed[field] = {}
                snapshot.write_text(json.dumps(changed), encoding="utf-8")
                self.assertNotEqual(self.run_cli("--check-snapshot", str(snapshot)).returncode, 0)
        snapshot.write_text(json.dumps(report), encoding="utf-8")
        (self.root / "README.md").write_text("New document", encoding="utf-8")
        self.assertNotEqual(self.run_cli("--check-snapshot", str(snapshot)).returncode, 0)

    def test_explicit_force_refreshes_report_but_not_inputs(self):
        output = self.root / "report.json"
        self.assertEqual(self.run_cli("--output", str(output)).returncode, 0)
        self.assertEqual(self.run_cli("--output", str(output), "--force").returncode, 0)
        self.assertNotEqual(self.run_cli("--force").returncode, 0)
        self.assertNotEqual(self.run_cli("--output", str(self.skill), "--force").returncode, 0)
        self.assertEqual(self.skill.read_text(encoding="utf-8"), VALID)

    def test_behavior_cases_but_not_results_are_fingerprinted(self):
        validation = self.root / "validation"
        validation.mkdir()
        (validation / "behavior-cases.json").write_text("[]", encoding="utf-8")
        (validation / "behavior-results.json").write_text("{}", encoding="utf-8")
        files = self.report()["files"]
        self.assertIn("validation/behavior-cases.json", files)
        self.assertNotIn("validation/behavior-results.json", files)
        (validation / "behavior-cases.json").write_text('[{"id": "new"}]', encoding="utf-8")
        self.assertNotEqual(files["validation/behavior-cases.json"],
                            self.report()["files"]["validation/behavior-cases.json"])

    def behavior_fixture(self):
        validation = self.root / "validation"
        validation.mkdir(exist_ok=True)
        cases = {"schema_version": 1, "cases": [{"id": "sample-case", "user_turns": ["Question"]}]}
        (validation / "behavior-cases.json").write_text(json.dumps(cases), encoding="utf-8")
        reference = self.skill.parent / "references" / "guide.md"
        reference.parent.mkdir(exist_ok=True)
        reference.write_text("Guidance", encoding="utf-8")
        report = self.report()
        record = {"schema_version": 1, "execution": {"model_id": None, "model_version": None,
                  "model_note": "Unavailable"}, "source_files": report["files"],
                  "case_count": 1, "assistant_turn_count": 1,
                  "results": [{"case_id": "sample-case", "assistant_turns": ["Answer"], "verdict": "pass"}]}
        path = validation / "behavior-results.json"
        path.write_text(json.dumps(record), encoding="utf-8")
        return path, record

    def test_behavior_integrity_valid_record_and_disclaimer(self):
        path, _ = self.behavior_fixture()
        result = self.run_cli("--check-behavior", str(path))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("not a behavioral retest", result.stdout)

    def test_behavior_integrity_rejects_stale_skill_reference_and_cases(self):
        path, _ = self.behavior_fixture()
        for source in (self.skill, self.skill.parent / "references" / "guide.md",
                       self.root / "validation" / "behavior-cases.json"):
            with self.subTest(source=source):
                original = source.read_text(encoding="utf-8")
                source.write_text(original + "\n", encoding="utf-8")
                result = self.run_cli("--check-behavior", str(path))
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("stale", result.stdout)
                source.write_text(original, encoding="utf-8")

    def test_behavior_integrity_rejects_missing_cases_counts_and_verdicts(self):
        path, original = self.behavior_fixture()
        for change in ("missing", "case_count", "assistant_turn_count", "turns", "fail", "not_run", "unknown"):
            with self.subTest(change=change):
                record = json.loads(json.dumps(original))
                if change == "missing":
                    record["results"] = []
                elif change in ("case_count", "assistant_turn_count"):
                    record[change] = 2
                elif change == "turns":
                    record["results"][0]["assistant_turns"] = []
                else:
                    record["results"][0]["verdict"] = change
                path.write_text(json.dumps(record), encoding="utf-8")
                self.assertNotEqual(self.run_cli("--check-behavior", str(path)).returncode, 0)

    def test_behavior_integrity_rejects_corrupt_json_and_untrusted_source_paths(self):
        path, record = self.behavior_fixture()
        for invalid in ("broken{", "[]"):
            path.write_text(invalid, encoding="utf-8")
            self.assertNotEqual(self.run_cli("--check-behavior", str(path)).returncode, 0)
        record["source_files"]["../../outside-secret.md"] = "untrusted"
        path.write_text(json.dumps(record), encoding="utf-8")
        result = self.run_cli("--check-behavior", str(path))
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("Traceback", result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
