# Yuhi Tanaka's cloud resume

A static resume website for **yuhitanaka.com**, deployed from
[7uhi/serverless-resume](https://github.com/7uhi/serverless-resume) with **AWS Amplify Hosting**
in **us-east-2**. The PDF is displayed on desktop, downloadable on every device, and
available as expandable text on mobile.

## Update your resume

1. Edit your resume in Overleaf and download the finished PDF.
2. Replace `resume/Resume.pdf` (capital R).
3. Commit and push to `main`.

Once the repository is connected, Amplify builds and publishes automatically.
The preview, download, and text view all use that same PDF. The public document
URL stays `/resume.pdf`. No document compiler or AWS access keys are needed.
`site.json` controls the input PDF path, display name, and introduction.

## Hosting status

The Amplify build configuration is prepared; hosting has not been created or verified.
The previous S3/CDK deployment path was removed. GitHub Actions checks the build
and saves a `website` artifact; Amplify handles publishing independently.
An AWS-managed policy denied the identity-provider listing used by the original
GitHub-to-AWS OIDC setup. This configuration instead uses Amplify's native GitHub
connection. No paid-plan upgrade or advanced-features activation is proposed.

## Preview locally

The build requires Python 3 and Poppler's `pdftotext`. On macOS:

```sh
brew install poppler
python3 scripts/build.py
python3 -m http.server 8000 --directory dist --bind 127.0.0.1
```

Open http://localhost:8000. Amplify and GitHub Actions install Poppler themselves.
No npm dependencies are required. `npm run build` and `npm run preview` are optional
shortcuts for the Python commands.

`amplify.yml` installs Poppler using the default Amazon Linux build image, runs
the Python build, and publishes only `dist/`. `customHttp.yml` sets security and
cache headers. No PDF content is sent to a separate conversion service.
The text view requires a text-based PDF; check reading order if the resume uses
multiple columns. Missing, invalid, or textless PDFs stop the build.

## Deployment cost and permissions review

AWS hosting creates usage charges, potentially covered by credits or applicable
allowances. The last local preflight reported an active Free plan with $120 in
remaining credits; verify the current balance in AWS Settings before deployment.

Published Amplify standard rates, before allowances/credits:

| Usage | Rate |
| --- | --- |
| Standard build | $0.01 per build minute |
| Stored site data | $0.023 per GB-month |
| Data served | $0.15 per GB |
| Public SSL certificate | No additional charge |

An illustrative month with 20 build minutes, 1 GB served, and 0.005 GB stored is
about **$0.35 before allowances/credits**. This is a usage estimate, not a spending
cap. Higher traffic, more builds, or retained deployment data change the total.
Domain renewal remains with Spaceship. Optional WAF and backend resources are not
part of this configuration. GitHub Actions usage is billed separately under your
GitHub plan if its included allowance is exceeded.

The connection grants the official AWS Amplify GitHub App access to the selected
repository. Select **Only select repositories → 7uhi/serverless-resume**.
It allows Amplify to read the code and receive changes so it can build the site.
No custom GitHub deployment role or long-lived AWS credentials are needed.

Creating the app and granting GitHub access require approval under the local project
instructions. Preparing these files has not created resources or changed permissions.

## Connect Amplify after approval

1. Commit and push the prepared configuration to `main`.
2. Open the [Amplify console in Ohio](https://us-east-2.console.aws.amazon.com/amplify/apps?region=us-east-2)
   for the project using profile `student-aws`.
3. Choose to deploy a new app from GitHub. Authorize the official Amplify GitHub App
   for only `7uhi/serverless-resume`, then choose branch `main`.
4. Name the app `serverless-resume`. This is a static app with no backend.
   Use the default Amazon Linux build image, the repository's `amplify.yml`,
   build command `python3 scripts/build.py`, and output directory `dist`.
   No environment variables are required. Leave optional WAF and backend features off.
5. Review the settings, then deploy. Wait for a successful deployment and open the
   generated `amplifyapp.com` address.
6. Verify the homepage, embedded PDF, PDF download, mobile text view, and response
   headers. The first cloud build is still needed to verify the build image setup.

There is no infrastructure bootstrap or GitHub AWS deployment-role step.
Future PDF pushes are published by Amplify independently of the GitHub build check;
required PR checks can be used if you want builds reviewed before merging to `main`.

## Connect yuhitanaka.com

After the default URL works, open the app's **Hosting → Custom domains → Add domain**.
Enter `yuhitanaka.com`, map the root domain to `main`, and use Amplify's managed
certificate. If you also add `www`, choose whether it should redirect to the root.

Keep the domain registered at Spaceship. Add the exact certificate-validation and
traffic-routing records Amplify displays to your active DNS service. For the root
domain, use the provider's supported apex ALIAS/ANAME mechanism; do not enter a
standard root CNAME or hardcode CloudFront IP addresses. Inspect the DNS provider's
available record types before changing records. Preserve existing email/MX/TXT records.
Keep validation records for certificate renewal.

Wait for Amplify's domain status to become available, then test HTTPS and PDF
download at `https://yuhitanaka.com`. No DNS records have been changed yet.

## Read-only AWS checks

```sh
python3 scripts/check_aws.py
```

This uses `student-aws` and saves login, plan, and Amplify app inventory to
`.build/aws-preflight.json`, which is ignored by Git. It creates no resources or
permissions. Because the agent's network cannot reach AWS, run it in your normal
Terminal when an inventory is needed. Its results include identifiers, not credentials.

## Verification status

- Python syntax checks pass, and the configured PDF exists with a PDF file header.
- Local extraction and full build verification still need Poppler.
- Amplify configuration follows AWS's documented build and header formats; the first
  cloud build, public-domain checks, and visual review remain pending.
- No AWS hosting app, GitHub authorization, or DNS changes have been performed.

References: [Amplify pricing](https://aws.amazon.com/amplify/pricing/),
[GitHub connection](https://docs.aws.amazon.com/amplify/latest/userguide/setting-up-GitHub-access.html),
[Build specification](https://docs.aws.amazon.com/amplify/latest/userguide/yml-specification-syntax.html),
[Custom domains](https://docs.aws.amazon.com/amplify/latest/userguide/to-add-a-custom-domain-managed-by-a-third-party-dns-provider.html).
