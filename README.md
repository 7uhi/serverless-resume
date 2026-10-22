# Yuhi Tanaka's cloud resume

A static resume website for **yuhitanaka.com**, hosted on private Amazon S3 through
CloudFront. Your uploaded PDF is displayed on desktop and offered as a download.
An expandable text view, extracted from that same PDF, works on mobile and without a
browser PDF viewer. Text extraction preserves the words, but not complex PDF layouts;
review its reading order with your actual resume. No application server is needed.

## Current status

The build scripts, site, AWS CDK infrastructure, and GitHub workflow are prepared.
Your resume PDF is at `resume/Resume.pdf`. No AWS resources, IAM roles, certificates,
or DNS records have been created. The site is not deployed.

## 1. Update your resume

1. Edit your resume in Overleaf (or your preferred editor) and download the finished PDF.
2. Replace `resume/Resume.pdf` (capital R), keeping the filename unchanged.
3. Commit and push to `main`. Once AWS publishing is configured, GitHub updates the site.

The project only uses the finished PDF. It does not compile source files.
The `pdf` field in `site.json` sets the input path. The public URL stays `/resume.pdf`.
The `name` and `description` fields control the landing-page copy. The preview,
download, and expandable text view all use the same PDF, so there is no second
resume to maintain in HTML.

## 2. Build locally

Install Poppler for PDF text extraction. On macOS:

```sh
brew install poppler
python3 scripts/build.py
python3 -m http.server 8000 --directory dist --bind 127.0.0.1
```

GitHub installs Poppler automatically. No Python packages or document compiler are required.
Open http://localhost:8000. Check the original PDF, the download button, and the text
view at desktop and mobile widths. PDF text extraction requires a text-based PDF,
not a scanned image. Builds fail before publication if the PDF is missing, invalid,
or has no extractable text.

## 3. Review and deploy AWS hosting

Regional resources belong in **us-east-2**, using the **student-aws** profile.
Before running commands that create resources, review charges and explicitly approve
deployment. CDK bootstrap and deployment also create or change permissions and need
approval under your local AWS instructions.

Hosting has usage-based S3 storage/request and CloudFront delivery charges. CDK
bootstrap adds supporting storage. GitHub Actions may consume billable minutes and
artifact storage depending on repository visibility and plan. No monthly estimate
has been calculated yet; check current AWS pricing and your project's free/paid plan
before deployment. A registered domain's renewal remains with Spaceship.

After approval and AWS login:

```sh
npm install
AWS_PROFILE=student-aws npx cdk synth --strict
# First-time CDK setup only; creates resources and IAM roles:
AWS_PROFILE=student-aws npx cdk bootstrap --region us-east-2
AWS_PROFILE=student-aws npx cdk diff
AWS_PROFILE=student-aws npx cdk deploy --outputs-file .build/aws-outputs.json
AWS_PROFILE=student-aws python3 scripts/publish.py
```

Commit the generated `package-lock.json`, then use `npm ci` on subsequent installs.
The default deployment uses the CloudFront-generated HTTPS address. Public S3 access
is blocked; CloudFront accesses objects using Origin Access Control. HTTP redirects
to HTTPS. Caching is disabled initially so every update is visible without an
invalidation step. Revisit caching if traffic grows. S3 objects are retained if the
stack is removed; cleanup must be deliberate and separately approved.

## 4. Connect yuhitanaka.com at Spaceship

CloudFront requires its ACM certificate in **us-east-1**. Your local project rules
restrict regional resources to us-east-2. Do not create a certificate in us-east-1
until that restriction is resolved. This project only imports an existing compatible
certificate; it does not bypass the restriction with a second regional stack.

Once an issued certificate for `yuhitanaka.com` is available, review this update:

```sh
AWS_PROFILE=student-aws npx cdk diff -c domain=yuhitanaka.com -c certificateArn=YOUR_CERTIFICATE_ARN
AWS_PROFILE=student-aws npx cdk deploy -c domain=yuhitanaka.com -c certificateArn=YOUR_CERTIFICATE_ARN
```

Use the same context arguments on subsequent infrastructure deployments. This
configuration serves the apex domain only; add `www` explicitly to both the
certificate and distribution if desired.

At Spaceship, keep any existing email/MX/TXT records. Add the ACM validation CNAME
records AWS provides, and leave them in place for renewal. After the distribution is
deployed, point the apex domain at the stack's `DistributionDomain` output using your
DNS provider's supported apex ALIAS/ANAME feature. A standard CNAME cannot be used
at the apex. Confirm Spaceship's current capabilities before making the change.
If the active DNS service cannot alias the apex to CloudFront, a Route 53 hosted zone
and nameserver migration is an alternative; copy all existing DNS records first and
review its charges. Do not hardcode CloudFront IP addresses. DNS changes are not
automated here because your current DNS records have not been inspected.

## 5. Enable push-to-publish on GitHub

1. Create a repository and push this project with your resume to its `main` branch.
2. The workflow builds the website from your PDF and saves a downloadable `website` artifact.
   Pull requests build for review and cannot publish.
3. After AWS deployment, create a narrowly scoped GitHub OIDC deployment role, with
   explicit permission approval. Trust only your repository's `production` environment,
   and restrict that GitHub environment to the `main` branch. Do not use AWS access keys.
4. Give the role `cloudformation:DescribeStacks` on the CloudResume stack and
   `s3:PutObject` on only these objects in its website bucket: `index.html`, `style.css`,
   and `resume.pdf`. The publishing script requires no infrastructure-write permissions.
5. Set repository variable `AWS_DEPLOY_ROLE_ARN` to that role's ARN. Configure production
   environment protection according to how automatically you want updates published.

Until this variable is set, builds work and publishing is skipped. Then your regular
update is: replace `resume/Resume.pdf`, commit, push. The workflow extracts the
text and publishes the PDF and website files. Failed builds leave the existing website untouched.
Do not push sensitive documents: the uploaded resume and all included personal
details will be public when published. Source code need not be in a public repository.

## Verification

- The configured input PDF exists and has a PDF file header.
- Python syntax checks pass. Local extraction and a full build still require Poppler.
- Review the PDF and the extracted text's reading order before publication.
- Dependency installation was blocked by network DNS failure to registry.npmjs.org;
  a lockfile and CDK synthesis are still pending.
- The AWS plan check could not reach the AWS sign-in endpoint, so project status
  has not been verified.
- Confirm AWS plan, certificate availability, existing DNS records, and hosting cost.
- Deploy with approval, then test HTTPS and PDF download from the public domain.

References: [CloudFront S3 Origin Access Control](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_cloudfront_origins-readme.html),
[CloudFront custom domains](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/CreatingCNAME.html).
# serverless-resume
