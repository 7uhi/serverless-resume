const cdk = require('aws-cdk-lib');
const s3 = require('aws-cdk-lib/aws-s3');
const cloudfront = require('aws-cdk-lib/aws-cloudfront');
const origins = require('aws-cdk-lib/aws-cloudfront-origins');
const acm = require('aws-cdk-lib/aws-certificatemanager');

const app = new cdk.App();
const stack = new cdk.Stack(app, 'CloudResume', { env: { region: 'us-east-2' } });
const domain = app.node.tryGetContext('domain');
const certificateArn = app.node.tryGetContext('certificateArn');
if (Boolean(domain) !== Boolean(certificateArn)) {
  throw new Error('Provide both -c domain=... and -c certificateArn=... or neither.');
}
if (certificateArn && !/^arn:aws:acm:us-east-1:\d{12}:certificate\//.test(certificateArn)) {
  throw new Error('CloudFront requires an ACM certificate in us-east-1.');
}
const bucket = new s3.Bucket(stack, 'Website', {
  blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
  enforceSSL: true,
  encryption: s3.BucketEncryption.S3_MANAGED,
  objectOwnership: s3.ObjectOwnership.BUCKET_OWNER_ENFORCED,
  removalPolicy: cdk.RemovalPolicy.RETAIN,
});
const headers = new cloudfront.ResponseHeadersPolicy(stack, 'SecurityHeaders', {
  securityHeadersBehavior: {
    contentTypeOptions: { override: true },
    referrerPolicy: { referrerPolicy: cloudfront.HeadersReferrerPolicy.NO_REFERRER, override: true },
    strictTransportSecurity: { accessControlMaxAge: cdk.Duration.days(180), override: true },
  },
  customHeadersBehavior: { customHeaders: [{ header: 'Content-Security-Policy', value: "default-src 'self'; style-src 'self'; frame-src 'self'; object-src 'none'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'", override: true }] },
});
const distribution = new cloudfront.Distribution(stack, 'Cdn', {
  defaultRootObject: 'index.html',
  priceClass: cloudfront.PriceClass.PRICE_CLASS_100,
  minimumProtocolVersion: cloudfront.SecurityPolicyProtocol.TLS_V1_2_2021,
  ...(domain ? {
    domainNames: [domain],
    certificate: acm.Certificate.fromCertificateArn(stack, 'ExistingCertificate', certificateArn),
  } : {}),
  defaultBehavior: {
    origin: origins.S3BucketOrigin.withOriginAccessControl(bucket),
    viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
    allowedMethods: cloudfront.AllowedMethods.ALLOW_GET_HEAD,
    cachePolicy: cloudfront.CachePolicy.CACHING_DISABLED,
    responseHeadersPolicy: headers,
    compress: true,
  },
});
new cdk.CfnOutput(stack, 'BucketName', { value: bucket.bucketName });
new cdk.CfnOutput(stack, 'DistributionId', { value: distribution.distributionId });
new cdk.CfnOutput(stack, 'DistributionDomain', { value: distribution.distributionDomainName });
new cdk.CfnOutput(stack, 'WebsiteUrl', { value: `https://${domain || distribution.distributionDomainName}` });
cdk.Tags.of(stack).add('Project', 'cloud-resume');
