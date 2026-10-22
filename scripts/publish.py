"""Publish a built site to an existing stack. Uses AWS CLI credentials or AWS_PROFILE."""
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def aws(*args, capture=False):
    result = subprocess.run(['aws', *args, '--region', 'us-east-2'], check=True,
                            capture_output=capture, text=True)
    return result.stdout if capture else None


def main():
    for name in ('index.html', 'style.css', 'resume.pdf'):
        if not (ROOT / 'dist' / name).is_file():
            sys.exit(f'Missing dist/{name}. Build the website first.')
    data = json.loads(aws('cloudformation', 'describe-stacks', '--stack-name',
                         os.environ.get('RESUME_STACK', 'CloudResume'), '--output', 'json', capture=True))
    outputs = {item['OutputKey']: item['OutputValue'] for item in data['Stacks'][0]['Outputs']}
    destination = f"s3://{outputs['BucketName']}"
    # Upload the document first, then expose the page that links to it.
    aws('s3', 'cp', str(ROOT / 'dist/resume.pdf'), f'{destination}/resume.pdf',
        '--content-type', 'application/pdf', '--cache-control', 'public,max-age=0,must-revalidate')
    aws('s3', 'cp', str(ROOT / 'dist/style.css'), f'{destination}/style.css',
        '--content-type', 'text/css; charset=utf-8', '--cache-control', 'public,max-age=0,must-revalidate')
    aws('s3', 'cp', str(ROOT / 'dist/index.html'), f'{destination}/index.html',
        '--content-type', 'text/html; charset=utf-8', '--cache-control', 'no-cache')
    print(f"Published {outputs['WebsiteUrl']}")


if __name__ == '__main__':
    main()
