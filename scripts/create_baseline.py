#!/usr/bin/env python3
"""
Create baseline metrics before refactoring.
This captures the current state for regression testing.
"""

import inspect
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict

import orjson


def run_command(cmd: str) -> tuple[str, int]:
    """Run command and return output and exit code."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=30
        )
        return result.stdout, result.returncode
    except Exception as e:
        return str(e), 1


def capture_public_apis() -> Dict[str, Any]:
    """Document all public APIs for regression testing."""
    apis = {}
    
    # Capture Conversation API
    try:
        from claude_parser.domain.entities.conversation import Conversation
        apis['Conversation'] = {
            'methods': [m for m in dir(Conversation) if not m.startswith('_')],
            'properties': [
                'session_id', 'filepath', 'current_dir', 'git_branch',
                'messages', 'assistant_messages', 'user_messages', 
                'tool_uses', 'summaries'
            ]
        }
    except Exception as e:
        apis['Conversation'] = {'error': str(e)}
    
    # Capture Parser API
    try:
        from claude_parser.models.parser import parse_message
        apis['parse_message'] = {
            'signature': str(inspect.signature(parse_message)),
            'module': 'claude_parser.models.parser'
        }
    except Exception as e:
        apis['parse_message'] = {'error': str(e)}
    
    # Capture Hook APIs
    try:
        from claude_parser.hooks import models as hook_models
        apis['hooks'] = {
            'parseHookData': hasattr(hook_models, 'parseHookData'),
            'isValidHookData': hasattr(hook_models, 'isValidHookData'),
            'isPreToolUse': hasattr(hook_models, 'isPreToolUse'),
            'isPostToolUse': hasattr(hook_models, 'isPostToolUse'),
        }
    except Exception as e:
        apis['hooks'] = {'error': str(e)}
    
    # Capture main API functions
    try:
        from claude_parser import load, watch
        apis['main'] = {
            'load': str(inspect.signature(load)),
            'watch': str(inspect.signature(watch)) if watch else None,
        }
    except Exception as e:
        apis['main'] = {'error': str(e)}
    
    return apis


def capture_test_results() -> Dict[str, Any]:
    """Run tests and capture results."""
    print("Running tests to capture baseline...")
    
    # Run pytest with json output
    output, code = run_command(
        "poetry run pytest tests/ --tb=no --co -q 2>/dev/null | wc -l"
    )
    test_count = int(output.strip()) if output.strip().isdigit() else 0
    
    # Get test pass rate
    output, code = run_command(
        "poetry run pytest tests/ -q --tb=no 2>/dev/null | tail -1"
    )
    
    return {
        'total_tests': test_count,
        'exit_code': code,
        'summary': output.strip() if output else 'No output'
    }


def capture_coverage() -> Dict[str, Any]:
    """Capture test coverage metrics."""
    print("Capturing coverage baseline...")
    
    output, code = run_command(
        "poetry run pytest tests/ --cov=claude_parser --cov-report=json --tb=no -q 2>/dev/null"
    )
    
    coverage_file = Path("coverage.json")
    if coverage_file.exists():
        coverage_data = json.loads(coverage_file.read_text())
        coverage_file.unlink()  # Clean up
        return {
            'total_coverage': coverage_data.get('totals', {}).get('percent_covered', 0),
            'files': coverage_data.get('files', {})
        }
    
    return {'total_coverage': 0, 'error': 'Could not capture coverage'}


def capture_code_metrics() -> Dict[str, Any]:
    """Capture code quality metrics."""
    print("Capturing code metrics...")
    
    metrics = {}
    
    # Count Python files
    py_files = list(Path("claude_parser").rglob("*.py"))
    test_files = list(Path("tests").rglob("*.py"))
    
    metrics['file_count'] = {
        'source': len(py_files),
        'tests': len(test_files),
        'total': len(py_files) + len(test_files)
    }
    
    # Count lines of code
    total_lines = 0
    for f in py_files:
        try:
            total_lines += len(f.read_text().splitlines())
        except:
            pass
    
    metrics['line_count'] = total_lines
    
    # Check for violations (simplified)
    violations = {
        'magic_strings': 0,
        'long_files': 0,
        'import_json': 0
    }
    
    for f in py_files:
        try:
            content = f.read_text()
            lines = content.splitlines()
            
            # Check for magic strings
            if 'abc123' in content or '/path/to/' in content:
                violations['magic_strings'] += 1
            
            # Check for long files
            if len(lines) > 150:
                violations['long_files'] += 1
            
            # Check for json imports
            if 'import json' in content:
                violations['import_json'] += 1
        except:
            pass
    
    metrics['violations'] = violations
    
    return metrics


def capture_performance() -> Dict[str, Any]:
    """Capture performance baseline."""
    print("Capturing performance baseline...")
    
    # Simple benchmark of loading a file
    benchmark_code = """
import time
from claude_parser import load
from pathlib import Path

test_file = None
for f in Path('jsonl-prod-data-for-test/test-data').glob('*.jsonl'):
    if f.exists():
        test_file = f
        break

if test_file:
    start = time.time()
    conv = load(str(test_file))
    elapsed = time.time() - start
    print(f"{elapsed:.4f}")
else:
    print("0.0")
"""
    
    output, code = run_command(f'poetry run python -c "{benchmark_code}"')
    load_time = float(output.strip()) if output.strip() else 0.0
    
    return {
        'load_time': load_time,
        'benchmark_file': 'test-data'
    }


def create_baseline():
    """Create complete baseline snapshot."""
    print("Creating baseline snapshot...")
    
    import pendulum
    
    baseline = {
        'timestamp': pendulum.now().isoformat(),
        'apis': capture_public_apis(),
        'tests': capture_test_results(),
        'coverage': capture_coverage(),
        'metrics': capture_code_metrics(),
        'performance': capture_performance(),
    }
    
    # Save baseline
    baseline_file = Path("baseline.json")
    baseline_file.write_bytes(
        orjson.dumps(baseline, option=orjson.OPT_INDENT_2)
    )
    
    print(f"\n✅ Baseline created: {baseline_file}")
    print(f"   - APIs documented: {len(baseline['apis'])}")
    print(f"   - Tests captured: {baseline['tests']['total_tests']}")
    print(f"   - Coverage: {baseline['coverage']['total_coverage']:.1f}%")
    print(f"   - Files: {baseline['metrics']['file_count']['total']}")
    print(f"   - Violations: {sum(baseline['metrics']['violations'].values())}")
    
    return baseline


if __name__ == "__main__":
    baseline = create_baseline()
    
    # Exit with error if tests are failing
    if baseline['tests']['exit_code'] != 0:
        print("\n⚠️ Warning: Tests are not passing in baseline!")
        sys.exit(1)