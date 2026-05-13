import * as cdk from 'aws-cdk-lib/core';
import * as s3 from 'aws-cdk-lib/aws-s3';
import { Construct } from 'constructs';

export class DataStack extends cdk.Stack {
  public readonly syntheticBucket: s3.Bucket;
  public readonly artifactsBucket: s3.Bucket;

  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    this.syntheticBucket = new s3.Bucket(this, 'SyntheticDataBucket', {
      bucketName: `am-copilot-synthetic-${this.account}-${this.region}`,
      encryption: s3.BucketEncryption.S3_MANAGED,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      versioned: true,
      removalPolicy: cdk.RemovalPolicy.RETAIN,
    });

    this.artifactsBucket = new s3.Bucket(this, 'ArtifactsBucket', {
      bucketName: `am-copilot-artifacts-${this.account}-${this.region}`,
      encryption: s3.BucketEncryption.S3_MANAGED,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      versioned: true,
      removalPolicy: cdk.RemovalPolicy.RETAIN,
    });
  }
}
