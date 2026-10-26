#!/usr/bin/env python3
"""Portable, offline checks for all nine generated staging workflows."""
import importlib.util
from pathlib import Path
import re
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('release_generator', ROOT / 'scripts/closed-source/publish_tree.py')
GENERATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GENERATOR)
PRODUCTS = ('lmaudio', 'lmcad', 'lmdraw', 'lmfilament', 'lmimg', 'lmmagnum', 'lmoffice', 'lmpdf', 'lmvideo')


class WorkflowGeneration(unittest.TestCase):
    def test_all_products_render_dispatch_only_linux_workflows(self):
        with tempfile.TemporaryDirectory() as temp:
            for product in PRODUCTS:
                with self.subTest(product=product):
                    source = Path(temp) / product
                    source.mkdir()
                    if product in ('lmaudio', 'lmimg', 'lmdraw'):
                        (source / 'CMakeLists.txt').write_text(f'project({product} VERSION 0.2.1 LANGUAGES C CXX)\n')
                    else:
                        (source / 'VERSION').write_text('0.2.1\n')
                    output = Path(temp) / f'{product}.yml'
                    with patch.object(GENERATOR.subprocess, 'check_output', return_value='0123456789abcdef\n'):
                        GENERATOR.generate_private_ci(source, product, output)
                    text = output.read_text()
                    self.assertNotRegex(text, r'\{\{(?:PRODUCT|MAJOR|MINOR|BUILD_|TEST_|SOURCE_CI_COMMIT)')
                    self.assertNotRegex(text, r'(?m)^  (push|pull_request):')
                    self.assertEqual(re.findall(r'(?m)^  ([a-z0-9-]+):$', text.split('jobs:\n')[1]), ['version', 'linux-x64', 'linux-arm64', 'stage'])
                    for required in ('workflow_dispatch:', 'ubuntu-22.04-arm', 'GITHUB_RUN_NUMBER', 'private-run-id', '--prerelease', '--latest=false', 'SOURCE_CI_COMMIT'):
                        # The source placeholder is replaced by an auditable commit.
                        self.assertIn('0123456789abcdef' if required == 'SOURCE_CI_COMMIT' else required, text)
                    build, stage = text.split('  stage:\n', 1)
                    self.assertNotIn('secrets.RELEASE_TOKEN', build)
                    self.assertIn('secrets.RELEASE_TOKEN', stage)
                    self.assertIn('cp public/LICENSE release-artifacts/LICENSE', stage)
                    self.assertIn("-printf '%f\\0'", stage)
                    if product in ('lmcad', 'lmfilament'):
                        self.assertIn('relink-objects', text)
                    # Parse each literal run block without depending on PyYAML.
                    for block in re.findall(r'(?m)^        run: \|\n((?:          [^\n]*\n|\n)+)', text):
                        script = '\n'.join(line[10:] if line.startswith('          ') else line for line in block.splitlines())
                        script = re.sub(r'\$\{\{.*?\}\}', 'fixture-value', script)
                        result = subprocess.run(['bash', '-n'], input=script, text=True, capture_output=True)
                        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == '__main__':
    unittest.main()
