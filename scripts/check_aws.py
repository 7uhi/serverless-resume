"""Save read-only AWS deployment checks for review. Creates no AWS resources."""
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PROFILE = 'student-aws'
REGION = 'us-east-2'


def query(*args):
    result = subprocess.run(
        ['aws', *args, '--profile', PROFILE, '--region', REGION, '--output', 'json', '--no-cli-pager'],
        capture_output=True, text=True, timeout=90,
    )
    if result.returncode:
        return {'error': result.stderr.strip() or f'AWS CLI exited with {result.returncode}'}
    return json.loads(result.stdout)


def main():
    identity = query('sts', 'get-caller-identity')
    checks = {'profile': PROFILE, 'region': REGION, 'identity': identity}
    if 'error' not in identity:
        checks['plan'] = query('freetier', 'get-account-plan-state')
        checks['hosting'] = query('amplify', 'list-apps', '--query',
                                  'apps[].{Name:name,Id:appId,Repository:repository,Domain:defaultDomain}')
    output = ROOT / '.build' / 'aws-preflight.json'
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(checks, indent=2) + '\n')
    failures = [key for key, value in checks.items() if isinstance(value, dict) and 'error' in value]
    print(f'Saved read-only checks to {output.relative_to(ROOT)} (ignored by Git).')
    if failures:
        for key in failures:
            print(f'{key}: {checks[key]["error"]}', file=sys.stderr)
        return 1
    print('Checks complete. No resources or permissions were changed.')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (FileNotFoundError, subprocess.TimeoutExpired, json.JSONDecodeError) as error:
        sys.exit(f'Check failed: {error}')
