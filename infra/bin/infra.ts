#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib/core';
import { DataStack } from '../lib/data-stack';
import { QueueStack } from '../lib/queue-stack';
import { AuthStack } from '../lib/auth-stack';
import { ObservabilityStack } from '../lib/observability-stack';

const app = new cdk.App();

const env = {
  account: process.env.CDK_DEFAULT_ACCOUNT,
  region: 'us-east-1',
};

new DataStack(app, 'AmCopilotDataStack', { env });
new QueueStack(app, 'AmCopilotQueueStack', { env });
new AuthStack(app, 'AmCopilotAuthStack', { env });
new ObservabilityStack(app, 'AmCopilotObservabilityStack', { env });
