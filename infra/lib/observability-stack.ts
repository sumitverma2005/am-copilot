import * as cdk from 'aws-cdk-lib/core';
import * as logs from 'aws-cdk-lib/aws-logs';
import { Construct } from 'constructs';

export class ObservabilityStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const retention = logs.RetentionDays.ONE_MONTH;

    const services = [
      'api-gateway',
      'evaluation-worker',
      'scoring-engine',
      'compliance-engine',
      'evidence-engine',
      'ctm-integration',
      'notification-service',
    ];

    for (const svc of services) {
      new logs.LogGroup(this, `LogGroup-${svc}`, {
        logGroupName: `/am-copilot/${svc}`,
        retention,
        removalPolicy: cdk.RemovalPolicy.RETAIN,
      });
    }
  }
}
