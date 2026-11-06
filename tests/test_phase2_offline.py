"""Offline Phase 2 checks.

Does not start Ella, Ollama, a listen socket, or a model. Run from the repo
root: python -m unittest tests.test_phase2_offline
"""

from __future__ import annotations

import ast
import json
import sys
import threading
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import context_manager
import model_registry
import permissions
import router
import store
import tasks
from tasks import TaskRejected


PRICE_KEYS = {"cost", "price", "usd", "token_cost", "tokens", "prompt_price", "completion_price"}
FORBIDDEN_IMPORTS = {
    "urllib",
    "urllib.request",
    "socket",
    "scout",
    "server",
    "stt",
    "tts",
    "ollama",
    "http.client",
}


def _walk_prices(test, value):
    if isinstance(value, dict):
        for key, item in value.items():
            test.assertNotIn(key, PRICE_KEYS)
            _walk_prices(test, item)
    elif isinstance(value, list):
        for item in value:
            _walk_prices(test, item)


class PermissionTests(unittest.TestCase):
    def test_catalog_has_four_levels(self):
        levels = permissions.level_catalog()["levels"]
        self.assertEqual([item["level"] for item in levels], [1, 2, 3, 4])
        self.assertEqual([item["name"] for item in levels], ["observe", "prepare", "modify", "external"])

    def test_levels_do_not_auto_execute(self):
        samples = [
            permissions.evaluate("task.observe", 1),
            permissions.evaluate("task.prepare", 2),
            permissions.evaluate("task.persist", 3, target="tasks"),
            permissions.evaluate("mail.send", 4),
            permissions.evaluate(
                "mail.send",
                4,
                approval={"approved": True, "by": "user", "action": "mail.send"},
            ),
        ]
        for decision in samples:
            self.assertFalse(decision["auto_execute"])
            self.assertFalse(decision["may_execute_external"])

    def test_l1_is_read_only(self):
        decision = permissions.evaluate("task.observe", 1)
        self.assertTrue(decision["permitted"])
        self.assertTrue(decision["may_observe"])
        self.assertFalse(decision["may_prepare"])
        self.assertFalse(decision["may_modify_local"])
        self.assertFalse(decision["requires_approval"])

    def test_l2_has_no_side_effects(self):
        decision = permissions.evaluate("task.prepare", 2)
        self.assertTrue(decision["may_prepare"])
        self.assertFalse(decision["may_modify_local"])
        self.assertEqual(decision["side_effects"], "none")

    def test_l3_only_owned_local_state(self):
        owned = permissions.evaluate("task.persist", 3, target="tasks")
        self.assertTrue(owned["may_modify_local"])
        self.assertTrue(owned["permitted"])
        missing = permissions.evaluate("task.persist", 3)
        self.assertFalse(missing["may_modify_local"])
        outside = permissions.evaluate("vault.write", 3, target="vault")
        self.assertFalse(outside["permitted"])
        self.assertFalse(outside["may_modify_local"])

    def test_l4_approval_never_means_execute(self):
        denied = permissions.evaluate("mail.send", 4, approval="yes I approve")
        self.assertFalse(denied["approved"])
        self.assertTrue(denied["requires_approval"])
        self.assertFalse(denied["permitted"])
        mismatch = permissions.evaluate(
            "mail.send",
            4,
            approval={"approved": True, "by": "user", "action": "mail.draft"},
        )
        self.assertFalse(mismatch["approved"])
        bare = permissions.evaluate("mail.send", 4, approval=True)
        self.assertFalse(bare["approved"])
        recorded = permissions.evaluate(
            "mail.send",
            4,
            target="gmail",
            approval={"approved": True, "by": "user", "action": "mail.send"},
        )
        self.assertTrue(recorded["approved"])
        self.assertFalse(recorded["permitted"])
        self.assertFalse(recorded["may_execute_external"])
        self.assertFalse(recorded["auto_execute"])
        self.assertIn("not auto-executed", recorded["reason"])

    def test_declared_external_action_cannot_run(self):
        decision = permissions.check_declared("task.external")
        self.assertEqual(decision["level"], 4)
        self.assertFalse(decision["may_execute_external"])
        unknown = permissions.check_declared("not.declared")
        self.assertFalse(unknown["permitted"])

    def test_bad_level_is_rejected(self):
        decision = permissions.evaluate("task.observe", True)
        self.assertFalse(decision["permitted"])
        self.assertEqual(decision["level"], 0)


class ContextTests(unittest.TestCase):
    def test_default_is_local_and_blocks_cloud(self):
        for mode in (None, "", "local", "LOCAL", "online"):
            decision = context_manager.route_for(
                mode,
                context_manager.bundles_for_kind("routine"),
                destination="cloud",
                kind="routine",
            )
            self.assertTrue(decision["blocked"], mode)
            self.assertFalse(decision["allow_cloud"])
            self.assertEqual(decision["provider_mode"], "local")
            self.assertEqual(decision["permitted_providers"], [])
            self.assertEqual(decision["may_leave"], [])
            self.assertTrue(decision["local_first"])

    def test_local_mode_keeps_normal_chat_local(self):
        decision = context_manager.route_for("local", context_manager.bundles_for_kind("chat"), kind="chat")
        self.assertFalse(decision["blocked"])
        self.assertEqual(decision["provider_mode"], "local")
        self.assertEqual(decision["permitted_providers"], ["ollama"])
        self.assertFalse(decision["allow_cloud"])
        self.assertEqual(decision["may_leave"], [])

    def test_cloud_switch_uses_existing_providers_only(self):
        chat = context_manager.route_for("cloud", context_manager.bundles_for_kind("chat"), kind="chat")
        self.assertFalse(chat["blocked"])
        self.assertTrue(chat["allow_cloud"])
        self.assertEqual(chat["permitted_providers"], ["openrouter", "groq", "ollama"])
        routine = context_manager.route_for(
            "cloud", context_manager.bundles_for_kind("routine"), kind="routine"
        )
        self.assertEqual(routine["permitted_providers"], ["groq", "ollama"])
        for decision in (chat, routine):
            self.assertEqual(decision["vendors_added"], [])
            for name in decision["permitted_providers"]:
                self.assertIn(name, {"ollama", "openrouter", "groq"})
            blob = json.dumps(decision)
            self.assertNotIn("anthropic", blob)
            self.assertNotIn("openai", blob)

    def test_secrets_never_leave_and_bodies_are_not_copied(self):
        decision = context_manager.route_for(
            "cloud",
            [{"kind": "secret", "label": "env", "text": "PRIVATE-SENTENCE"}],
            kind="chat",
        )
        blob = json.dumps(decision)
        self.assertNotIn("PRIVATE-SENTENCE", blob)
        self.assertTrue(decision["blocked"])
        self.assertEqual(decision["may_leave"], [])
        self.assertIn("env", decision["withheld"])
        self.assertFalse(decision["allow_cloud"])

    def test_vision_stays_local_even_if_cloud_mode_is_on(self):
        decision = context_manager.route_for(
            "local",
            [{"kind": "vision", "label": "image"}],
            destination="local",
            kind="chat",
        )
        self.assertFalse(decision["blocked"])
        self.assertEqual(decision["provider_mode"], "local")
        self.assertFalse(decision["allow_cloud"])
        self.assertEqual(decision["permitted_providers"], ["ollama"])

    def test_status_follows_the_existing_switch(self):
        local = context_manager.context_status(None)
        self.assertEqual(local["mode"], "local")
        self.assertFalse(local["allow_cloud"])
        self.assertEqual(local["vision"], "local")
        cloud = context_manager.context_status("cloud")
        self.assertTrue(cloud["cloud_switch"])
        self.assertTrue(cloud["allow_cloud"])
        self.assertEqual(cloud["vision"], "local")


class RegistryTests(unittest.TestCase):
    def test_configured_ids_match_current_runtime(self):
        self.assertEqual(model_registry.vision_model_id(), "moondream:latest")
        self.assertEqual(model_registry.DEFAULT_LOCAL_CHAT, "llama3.2:3b")
        self.assertEqual(model_registry.GROQ_CHAT, "llama-3.1-8b-instant")
        self.assertEqual(model_registry.OPENROUTER_CHAT, "openrouter/free")

    def test_vision_is_only_moondream_and_costs_are_unknown(self):
        vision = model_registry.lookup("moondream:latest")
        self.assertTrue(vision["vision"])
        self.assertFalse(vision["chat"])
        self.assertTrue(vision["local"])
        self.assertFalse(vision["cost_known"])
        chat = model_registry.lookup("llama3.2:3b")
        self.assertTrue(chat["chat"])
        self.assertFalse(chat["vision"])
        unknown = model_registry.lookup("qwen2.5:7b")
        self.assertFalse(unknown["configured"])
        self.assertIsNone(unknown["chat"])
        self.assertFalse(unknown["vision"])
        self.assertFalse(unknown["cost_known"])
        snapshot = model_registry.capability_snapshot(
            {"mode": "local", "model": "llama3.2:3b"},
            ["moondream:latest", "llama3.2:3b", "qwen2.5:7b"],
        )
        self.assertEqual(snapshot["vision_model"], "moondream:latest")
        self.assertFalse(snapshot["cost_known"])
        by_id = {item["id"]: item for item in snapshot["installed_local"]}
        self.assertTrue(by_id["moondream:latest"]["vision"])
        self.assertIsNone(by_id["qwen2.5:7b"]["chat"])
        self.assertFalse(by_id["qwen2.5:7b"]["vision"])
        _walk_prices(self, snapshot)
        _walk_prices(self, vision)

    def test_router_order_stays_fail_closed(self):
        self.assertEqual(router.provider_order("local", "chat"), ("ollama",))
        self.assertEqual(router.provider_order("local", "routine"), ("ollama",))
        self.assertEqual(router.provider_order(None, "chat"), ("ollama",))
        self.assertEqual(router.provider_order("LOCAL", "chat"), ("ollama",))
        self.assertEqual(router.provider_order("cloud", "chat"), ("openrouter", "groq", "ollama"))
        self.assertEqual(router.provider_order("cloud", "routine"), ("groq", "ollama"))
        source = (ROOT / "router.py").read_text(encoding="utf-8")
        self.assertIn("order = provider_order(mode, kind)", source)


class TaskTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.path = Path(self.tmp.name) / "tasks.json"
        self._locked = tasks.locked_update
        tasks.set_tasks_path(self.path)

    def tearDown(self):
        tasks.locked_update = self._locked
        tasks.set_tasks_path(None)
        self.tmp.cleanup()

    def test_locked_update_roundtrip(self):
        sample = Path(self.tmp.name) / "sample.json"

        def bump(data):
            return {"n": int((data or {}).get("n") or 0) + 1}

        store.locked_update(sample, {"n": 0}, bump)
        store.locked_update(sample, {"n": 0}, bump)
        self.assertEqual(store.read_json(sample, {})["n"], 2)

    def test_default_plan_has_no_external_step(self):
        calls = []

        def wrapped(path, default, transform):
            calls.append(Path(path))
            return self._locked(path, default, transform)

        tasks.locked_update = wrapped
        task = tasks.submit_task("please send an email and I approve it", None)
        self.assertTrue(any(path.name == "tasks.json" for path in calls))
        self.assertTrue(all(step["level"] < 3 for step in task["steps"]))
        self.assertEqual(task["status"], "completed")
        self.assertEqual(task["progress"]["unfinished"], [])
        self.assertTrue(self.path.exists())
        disk = json.loads(self.path.read_text(encoding="utf-8"))
        self.assertEqual(disk["version"], 1)
        self.assertEqual(disk["tasks"][0]["id"], task["id"])

    def test_l4_survives_restart_and_cannot_be_marked_done(self):
        task = tasks.submit_task(
            "draft a note",
            [
                {"title": "Read it", "action": "task.observe", "level": 1},
                {"title": "Send mail", "action": "mail.send", "level": 4, "target": "gmail"},
            ],
        )
        self.assertEqual(task["status"], "incomplete")
        external = task["steps"][1]
        self.assertEqual(external["status"], "awaiting_approval")
        self.assertIsNone(external["result"])
        self.assertFalse(external["permission"]["may_execute_external"])
        self.assertFalse(external["permission"]["auto_execute"])
        self.assertEqual(task["progress"]["done"], 1)
        self.assertEqual(len(task["progress"]["unfinished"]), 1)

        report = tasks.task_report()
        self.assertEqual(report["tasks"][0]["id"], task["id"])
        self.assertEqual(report["incomplete"], 1)

        raw = json.loads(self.path.read_text(encoding="utf-8"))
        for step in raw["tasks"][0]["steps"]:
            if step["level"] == 4:
                step["status"] = "done"
                step["permission"]["approved"] = True
                step["permission"]["may_execute_external"] = True
                step["permission"]["auto_execute"] = True
        self.path.write_text(json.dumps(raw), encoding="utf-8")

        viewed = tasks.task_report()["tasks"][0]
        viewed_l4 = viewed["steps"][1]
        self.assertNotEqual(viewed_l4["status"], "done")
        self.assertEqual(viewed["status"], "incomplete")

        resumed = tasks.resume_task(task["id"])
        resumed_l4 = resumed["steps"][1]
        self.assertEqual(resumed_l4["status"], "awaiting_approval")
        self.assertFalse(resumed_l4["permission"]["approved"])
        self.assertFalse(resumed_l4["permission"]["may_execute_external"])
        self.assertFalse(resumed_l4["permission"]["auto_execute"])
        self.assertNotEqual(resumed["status"], "completed")
        saved = json.loads(self.path.read_text(encoding="utf-8"))
        saved_l4 = saved["tasks"][0]["steps"][1]
        self.assertEqual(saved_l4["status"], "awaiting_approval")
        self.assertFalse(saved_l4["permission"]["may_execute_external"])

    def test_l3_outside_the_task_record_is_not_applied(self):
        task = tasks.submit_task(
            "update profile later",
            [{"title": "Update profile", "action": "profile.save", "level": 3, "target": "profile"}],
        )
        self.assertEqual(task["steps"][0]["status"], "ready")
        self.assertEqual(task["status"], "incomplete")
        blocked = tasks.submit_task(
            "edit vault",
            [{"title": "Edit vault", "action": "vault.write", "level": 3, "target": "vault"}],
        )
        self.assertEqual(blocked["steps"][0]["status"], "blocked")

    def test_rejects_smuggled_approval_and_bad_levels(self):
        with self.assertRaises(TaskRejected):
            tasks.submit_task(
                "send it",
                [{"title": "Send", "action": "mail.send", "level": 4, "approved": True}],
            )
        with self.assertRaises(TaskRejected):
            tasks.submit_task(
                "bad",
                [{"title": "Bad", "action": "task.observe", "level": True}],
            )
        with self.assertRaises(TaskRejected):
            tasks.submit_task("empty", [])

    def test_concurrent_plans_keep_every_task(self):
        errors = []

        def worker(index):
            try:
                tasks.submit_task(f"note {index}", None)
            except Exception as exc:
                errors.append(exc)

        threads = [threading.Thread(target=worker, args=(index,)) for index in range(8)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        self.assertEqual(errors, [])
        self.assertEqual(tasks.task_report()["count"], 8)


class WiringTests(unittest.TestCase):
    def test_phase2_modules_do_not_import_network_stacks(self):
        for name in ("permissions.py", "context_manager.py", "model_registry.py", "tasks.py"):
            tree = ast.parse((ROOT / name).read_text(encoding="utf-8"))
            modules = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    modules.update(alias.name.split(".")[0] for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    modules.add(node.module.split(".")[0])
            self.assertFalse(modules & FORBIDDEN_IMPORTS, name)

    def test_server_and_router_are_hooked_without_a_new_vision_model(self):
        server = (ROOT / "server.py").read_text(encoding="utf-8")
        routines = (ROOT / "routines.py").read_text(encoding="utf-8")
        self.assertIn("vision_model_id()", server)
        self.assertIn("route_for(", server)
        self.assertIn('"/api/tasks"', server)
        self.assertGreaterEqual(server.count('DATA / "tasks.json"'), 2)
        self.assertIn("route_for(", routines)
        self.assertNotIn("claude", server.lower())
        self.assertEqual(model_registry.vision_model_id(), "moondream:latest")


if __name__ == "__main__":
    unittest.main()
