#!/usr/bin/env node
import * as cdk from "aws-cdk-lib";
import { NetworkStack } from "../lib/network-stack";
import { DatabaseStack } from "../lib/database-stack";
import { AppEc2Stack } from "../lib/app-ec2-stack";
import { buildConfig } from "../lib/config";

const app = new cdk.App();
const stage = app.node.tryGetContext("stage") || process.env.STAGE || "prod";
const env = {
  account: process.env.CDK_DEFAULT_ACCOUNT,
  region: process.env.CDK_DEFAULT_REGION || "us-east-1",
};

const cfg = buildConfig(stage);

const network = new NetworkStack(app, `${cfg.appName}-${stage}-network`, {
  env,
  description: `${cfg.appName} network (${stage})`,
  natGateways: 1,
});

const database = new DatabaseStack(app, `${cfg.appName}-${stage}-database`, {
  env,
  description: `${cfg.appName} database (${stage})`,
  vpc: network.vpc,
  dbSecurityGroup: network.dbSecurityGroup,
  dbName: cfg.dbName,
  deletionProtection: cfg.deletionProtection,
  instanceSize: cfg.dbInstanceSize,
});



// Optional context for OAuth params
const googleClientIdParamName = app.node.tryGetContext("googleClientIdParamName");
const googleClientSecretArn = app.node.tryGetContext("googleClientSecretArn");
const githubClientIdParamName = app.node.tryGetContext("githubClientIdParamName");
const githubClientSecretArn = app.node.tryGetContext("githubClientSecretArn");
const oauthRedirectUriParamName = app.node.tryGetContext("oauthRedirectUriParamName");
const acmCertificateArn = app.node.tryGetContext("acmCertificateArn");

new AppEc2Stack(app, `${cfg.appName}-${stage}-app`, {
  env,
  description: `${cfg.appName} app (${stage})`,
  vpc: network.vpc,
  webSecurityGroup: network.webSecurityGroup,
  albSecurityGroup: network.albSecurityGroup,
  dbInstance: database.dbInstance,
  dbSecret: database.dbSecret,
  stage,
  appName: cfg.appName,
  dbName: cfg.dbName,
  googleClientIdParamName,
  googleClientSecretArn,
  githubClientIdParamName,
  githubClientSecretArn,
  oauthRedirectUriParamName,
  acmCertificateArn,
});
