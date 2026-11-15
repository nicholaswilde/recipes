#!/usr/bin/env python3

################################################################################
#
# test_sync_giscus_comments.py
# ----------------
# Unit tests for sync_giscus_comments.py Giscus triage and tag promotion
#
# @author nιcнolaѕ wιlde, 0x08b7d7a3
# @date 14 Nov 2026
# @version 0.1.0
#
################################################################################

import importlib.util
import os
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location(
    "sync_giscus_comments", "scripts/sync_giscus_comments.py"
)
sync_giscus = importlib.util.module_from_spec(spec)
sys.modules["sync_giscus_comments"] = sync_giscus
spec.loader.exec_module(sync_giscus)


class TestSyncGiscusComments(unittest.TestCase):
    """Tests for Giscus comment sync, note detection, and triage updates."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.docs_dir = os.path.join(self.test_dir, "docs")
        self.cook_dir = os.path.join(self.test_dir, "cook")
        self.state_file = os.path.join(self.test_dir, "state.json")
        os.makedirs(os.path.join(self.docs_dir, "breads"), exist_ok=True)
        os.makedirs(os.path.join(self.cook_dir, "breads"), exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def _make_discussion(self, number=1500, title="recipes/breads/test-loaf/", comments=None):
        return {
            "id": f"D_{number}",
            "number": number,
            "title": title,
            "url": f"https://github.com/nicholaswilde/recipes/discussions/{number}",
            "category": {"name": "Comments"},
            "comments": {"nodes": comments or []},
        }

    def test_clean_pathname_and_normalize_slug(self):
        self.assertEqual(
            sync_giscus.clean_pathname("recipes/breads/cranberry-orange-bread/"),
            "breads/cranberry-orange-bread",
        )
        self.assertEqual(
            sync_giscus.normalize_slug("Cook's Illustrated Snickerdoodles"),
            "cooks-illustrated-snickerdoodles",
        )
        self.assertEqual(
            sync_giscus.normalize_slug("Mimi's Café Buttermilk Spice Muffins"),
            "mimis-cafe-buttermilk-spice-muffins",
        )

    def test_find_cook_file_prefers_matching_category(self):
        c1 = os.path.join(self.cook_dir, "main", "Shared Dish.cook")
        c2 = os.path.join(self.cook_dir, "breads", "Shared Dish.cook")
        os.makedirs(os.path.dirname(c1), exist_ok=True)
        with open(c1, "w", encoding="utf-8") as f:
            f.write("Main\n")
        with open(c2, "w", encoding="utf-8") as f:
            f.write("Bread\n")

        cook_map = sync_giscus.build_cook_file_map(self.cook_dir)
        matched = sync_giscus.find_cook_file(
            "breads/shared-dish", cook_dir=self.cook_dir, cook_file_map=cook_map
        )
        self.assertEqual(matched, c2)

    def test_is_cooking_note_classification(self):
        self.assertEqual(
            sync_giscus.is_cooking_note({"author": "nicholaswilde", "body": "Add 1 tsp vanilla"}),
            (True, True),
        )
        self.assertEqual(
            sync_giscus.is_cooking_note({"author": "nicholaswilde", "body": "No problem!"}),
            (False, False),
        )
        self.assertEqual(
            sync_giscus.is_cooking_note({"author": "reader", "body": "Thanks for the recipy"}),
            (False, False),
        )
        self.assertEqual(
            sync_giscus.is_cooking_note({"author": "reader", "body": "Step 2: use 1/4 cup olive oil"}),
            (True, False),
        )
        self.assertEqual(
            sync_giscus.is_cooking_note({"author": "dependabot[bot]", "body": "Add 1 cup"}),
            (False, False),
        )

    def test_promote_tags_in_markdown_block_and_inline(self):
        md_block = os.path.join(self.docs_dir, "breads", "test-loaf.md")
        with open(md_block, "w", encoding="utf-8") as f:
            f.write("---\ncomments: true\ntags:\n  - bread\n  - must-try\n---\n\n# Loaf\n")

        self.assertTrue(sync_giscus.promote_tags_in_markdown(md_block))
        with open(md_block, "r", encoding="utf-8") as f:
            updated = f.read()
        self.assertIn("  - favorite\n", updated)
        self.assertNotIn("must-try", updated)
        self.assertFalse(sync_giscus.promote_tags_in_markdown(md_block))

        md_inline = os.path.join(self.docs_dir, "breads", "inline.md")
        with open(md_inline, "w", encoding="utf-8") as f:
            f.write("---\ntags: [bread, must-try, favorite]\n---\n\n# Inline\n")
        self.assertTrue(sync_giscus.promote_tags_in_markdown(md_inline))
        with open(md_inline, "r", encoding="utf-8") as f:
            inline_updated = f.read()
        self.assertIn("tags: [bread, favorite]", inline_updated)

    def test_update_cook_file_yaml_and_legacy_and_idempotency(self):
        cook_yaml = os.path.join(self.cook_dir, "breads", "Test Loaf.cook")
        with open(cook_yaml, "w", encoding="utf-8") as f:
            f.write("---\ntitle: Test Loaf\ntags:\n  - bread\n  - must-try\n---\n\nMix @flour{1%cup}.\n")

        notes = [
            {
                "id": "DC_123",
                "author": "nicholaswilde",
                "createdAt": "2026-11-14T10:00:00Z",
                "body": "Bake 5 minutes longer --] check crust",
            }
        ]
        res = sync_giscus.update_cook_file(cook_yaml, notes, promote_favorite=True)
        self.assertTrue(res["changed"])
        self.assertTrue(res["promoted"])
        self.assertEqual(res["notes_added"], 1)

        with open(cook_yaml, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("  - favorite", content)
        self.assertNotIn("must-try", content)
        self.assertIn("[-- Giscus cooking note (@nicholaswilde, 2026-11-14, DC_123):", content)
        self.assertIn("- -]", content)

        # Idempotent second run
        res2 = sync_giscus.update_cook_file(cook_yaml, notes, promote_favorite=True)
        self.assertFalse(res2["changed"])
        self.assertEqual(res2["notes_added"], 0)

        # Legacy >> metadata without tags yet
        cook_legacy = os.path.join(self.cook_dir, "breads", "Legacy Loaf.cook")
        with open(cook_legacy, "w", encoding="utf-8") as f:
            f.write(">> source: https://example.com\n>> tags: bread\n\nMix @water{1%cup}.\n")
        res_legacy = sync_giscus.update_cook_file(cook_legacy, notes, promote_favorite=True)
        self.assertTrue(res_legacy["promoted"])
        with open(cook_legacy, "r", encoding="utf-8") as f:
            legacy_text = f.read()
        self.assertIn(">> tags: bread, favorite", legacy_text)

    def test_extract_comments_includes_replies_chronologically(self):
        disc = self._make_discussion(
            comments=[
                {
                    "id": "DC_1",
                    "url": "https://example.com/1",
                    "author": {"login": "nicholaswilde"},
                    "body": "First note",
                    "createdAt": "2026-11-14T08:00:00Z",
                    "replies": {
                        "nodes": [
                            {
                                "id": "DC_2",
                                "url": "https://example.com/2",
                                "author": {"login": "nicholaswilde"},
                                "body": "Follow-up reply",
                                "createdAt": "2026-11-14T09:00:00Z",
                            }
                        ]
                    },
                }
            ]
        )
        extracted = sync_giscus.extract_comments_from_discussion(disc)
        self.assertEqual([c["id"] for c in extracted], ["DC_1", "DC_2"])
        self.assertFalse(extracted[0]["is_reply"])
        self.assertTrue(extracted[1]["is_reply"])

    @patch.object(sync_giscus, "fetch_existing_triage_comment_ids", return_value=set())
    @patch.object(sync_giscus, "open_triage_pr", return_value="https://github.com/o/r/pull/99")
    @patch.object(sync_giscus, "open_triage_issue")
    @patch.object(sync_giscus, "_run_git")
    def test_triage_discussions_auto_opens_pr_and_skips_processed(
        self, mock_git, mock_issue, mock_pr, _mock_existing
    ):
        mock_git.return_value = type("R", (), {"returncode": 0, "stdout": "", "stderr": ""})()

        md_path = os.path.join(self.docs_dir, "breads", "test-loaf.md")
        cook_path = os.path.join(self.cook_dir, "breads", "Test Loaf.cook")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("---\ntags:\n  - bread\n  - must-try\n---\n\n# Test Loaf\n")
        with open(cook_path, "w", encoding="utf-8") as f:
            f.write("---\ntitle: Test Loaf\ntags:\n  - bread\n  - must-try\n---\n\nMix @flour{1%cup}.\n")

        sync_giscus.save_state(self.state_file, ["DC_OLD"])
        disc = self._make_discussion(
            number=1501,
            comments=[
                {
                    "id": "DC_OLD",
                    "url": "https://example.com/old",
                    "author": {"login": "nicholaswilde"},
                    "body": "Old note",
                    "createdAt": "2026-11-10T08:00:00Z",
                    "replies": {"nodes": []},
                },
                {
                    "id": "DC_NEW",
                    "url": "https://example.com/new",
                    "author": {"login": "nicholaswilde"},
                    "body": "Use 2 tsp salt instead",
                    "createdAt": "2026-11-14T10:00:00Z",
                    "replies": {"nodes": []},
                },
            ],
        )

        res = sync_giscus.triage_discussions(
            [disc],
            docs_dir=self.docs_dir,
            cook_dir=self.cook_dir,
            state_file=self.state_file,
            mode="auto",
        )
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["action"], "pr")
        self.assertTrue(res[0]["promoted"])
        self.assertEqual(res[0]["notes"], 1)
        mock_pr.assert_called_once()
        mock_issue.assert_not_called()
        pr_body = mock_pr.call_args.kwargs["body"]
        self.assertIn("<!-- giscus-comment-id: DC_NEW -->", pr_body)
        self.assertNotIn("DC_OLD", pr_body)

    @patch.object(sync_giscus, "fetch_existing_triage_comment_ids", return_value=set())
    @patch.object(sync_giscus, "open_triage_pr", return_value=None)
    @patch.object(sync_giscus, "open_triage_issue", return_value="https://github.com/o/r/issues/200")
    @patch.object(sync_giscus, "_run_git")
    def test_triage_discussions_falls_back_to_issue(
        self, mock_git, mock_issue, mock_pr, _mock_existing
    ):
        mock_git.return_value = type("R", (), {"returncode": 0, "stdout": "", "stderr": ""})()

        md_path = os.path.join(self.docs_dir, "breads", "test-loaf.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("---\ncomments: true\n---\n\n# Test Loaf\n")

        disc = self._make_discussion(
            number=1502,
            comments=[
                {
                    "id": "DC_FALLBACK",
                    "url": "https://example.com/fb",
                    "author": {"login": "nicholaswilde"},
                    "body": "Add 1 Tbsp honey",
                    "createdAt": "2026-11-14T10:00:00Z",
                    "replies": {"nodes": []},
                }
            ],
        )

        # No .cook file and comments:true already present -> no file edits -> fallback to issue
        res = sync_giscus.triage_discussions(
            [disc],
            docs_dir=self.docs_dir,
            cook_dir=self.cook_dir,
            state_file=self.state_file,
            mode="auto",
        )
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["action"], "issue")
        mock_pr.assert_not_called()
        mock_issue.assert_called_once()

    @patch.object(sync_giscus, "open_triage_pr")
    @patch.object(sync_giscus, "open_triage_issue")
    def test_triage_discussions_dry_run_makes_no_writes(self, mock_issue, mock_pr):
        md_path = os.path.join(self.docs_dir, "breads", "test-loaf.md")
        original_md = "---\ntags:\n  - must-try\n---\n\n# Test Loaf\n"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(original_md)

        disc = self._make_discussion(
            number=1503,
            comments=[
                {
                    "id": "DC_DRY",
                    "url": "https://example.com/dry",
                    "author": {"login": "nicholaswilde"},
                    "body": "Proof 30 minutes longer",
                    "createdAt": "2026-11-14T10:00:00Z",
                    "replies": {"nodes": []},
                }
            ],
        )

        res = sync_giscus.triage_discussions(
            [disc],
            docs_dir=self.docs_dir,
            cook_dir=self.cook_dir,
            state_file=self.state_file,
            dry_run=True,
        )
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["action"], "dry-run")
        self.assertTrue(res[0]["promoted"])
        mock_pr.assert_not_called()
        mock_issue.assert_not_called()
        with open(md_path, "r", encoding="utf-8") as f:
            self.assertEqual(f.read(), original_md)


if __name__ == "__main__":
    unittest.main()
