import * as cdk from 'aws-cdk-lib/core';
import * as sqs from 'aws-cdk-lib/aws-sqs';
import { Construct } from 'constructs';

export class QueueStack extends cdk.Stack {
  public readonly evaluationQueue: sqs.Queue;
  public readonly deadLetterQueue: sqs.Queue;

  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    this.deadLetterQueue = new sqs.Queue(this, 'EvaluationDLQ', {
      queueName: 'am-copilot-evaluation-dlq',
      retentionPeriod: cdk.Duration.days(14),
      encryption: sqs.QueueEncryption.SQS_MANAGED,
    });

    this.evaluationQueue = new sqs.Queue(this, 'EvaluationQueue', {
      queueName: 'am-copilot-evaluation',
      retentionPeriod: cdk.Duration.days(14),
      visibilityTimeout: cdk.Duration.seconds(300),
      encryption: sqs.QueueEncryption.SQS_MANAGED,
      deadLetterQueue: {
        queue: this.deadLetterQueue,
        maxReceiveCount: 3,
      },
    });
  }
}
