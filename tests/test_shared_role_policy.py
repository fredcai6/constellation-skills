"""Real native installer boundary for the role sources also consumed by Pi."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from scripts import install_constellation as installer

ROOT = Path(__file__).resolve().parents[1]
SHARED = ROOT / 'skills' / '_shared'

class SharedRolePolicyTests(unittest.TestCase):
    def test_manifest_and_entrypoints_use_actual_bundled_source_for_both_native_agents(self):
        manifest = json.loads((SHARED / 'role-policy/manifest.json').read_text())
        self.assertEqual(set(manifest['roles']), {'commander', 'implementer', 'reviewer'})
        skills = {s.source_name: s for s in installer.discover_skills()}
        for agent in ('codex', 'claude'):
            with self.subTest(agent=agent), tempfile.TemporaryDirectory() as tmp:
                dest = Path(tmp) / 'skills'
                with patch.object(installer, 'resolve_interpreter', return_value=installer.InterpreterResolution(sys.executable, (sys.executable,), 'probe')):
                    self.assertEqual(installer.main(['--agent', agent, '--scope', 'user', '--dest', str(dest), '--skills', 'commander', 'commander-delegated', 'implementer', 'reviewer'], env={}, out=lambda _: None), 0)
                for role, paths in manifest['roles'].items():
                    bundled = dest / f'constellation-{role}'
                    entry = (bundled / 'SKILL.md').read_text()
                    if role == 'commander':
                        self.assertIn('references/commander-core.md', entry)
                        entry = (bundled / 'references/commander-core.md').read_text()
                    self.assertIn(f'references/role-policy/{role}.md', entry)
                    self.assertIn(f'references/role-policy/{role}-native.md', entry)
                    for path in paths:
                        with self.subTest(role=role, path=path):
                            self.assertEqual((bundled / 'references' / path).read_bytes(), (SHARED / path).read_bytes())
                    self.assertNotIn('## Start here', (SHARED / f'role-policy/{role}.md').read_text())
                    self.assertIn('## Start here', (bundled / f'references/role-policy/{role}-native.md').read_text())
                # All other inherited-everyone consumers get the pointer's closure.
                for skill in skills.values():
                    self.assertIn('role-policy/everyone.md', skill.required_references)
                    self.assertIn('role-policy/everyone-native.md', skill.required_references)
                common = (SHARED / 'role-policy/commander.md').read_text()
                intake = common.split('## Intake and boundary evidence\n', 1)[1].split('\n## ', 1)[0]
                self.assertIn('UNCONFIRMED — DO NOT CUT', intake)
                self.assertIn('needed action', intake)
                self.assertIn('load-bearing unknown', intake)
                commander = dest / 'constellation-commander'
                self.assertIn(intake, (commander / 'references/role-policy/commander.md').read_text())
                self.assertNotIn(intake, (commander / 'references/role-policy/commander-native.md').read_text())
                self.assertTrue((commander / 'scripts/verify_spec_confirmed.py').is_file())
                delegated = dest / 'constellation-commander-delegated'
                self.assertIn('constellation-commander', (delegated / 'SKILL.md').read_text())
                self.assertTrue((dest / 'constellation-commander/references/commander-core.md').is_file())

    def test_missing_canonical_role_ref_is_an_installer_error(self):
        skill = next(s for s in installer.discover_skills() if s.source_name == 'reviewer')
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(installer.InstallError):
                installer.validate_required_references([skill], Path(tmp))

if __name__ == '__main__':
    unittest.main()
