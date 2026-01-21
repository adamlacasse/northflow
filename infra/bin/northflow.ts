#!/usr/bin/env node
import * as cdk from "aws-cdk-lib";
import { NetworkStack } from "../lib/network-stack";
import { DatabaseStack } from "../lib/database-stack";
import { AppStack } from "../lib/app-stack";
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

type ImageSource = "ecr" | "local";
const imageSource: ImageSource = (app.node.tryGetContext("imageSource") as ImageSource) || "ecr";
const imageTag = app.node.tryGetContext("imageTag") || "latest";
const certificateArn = app.node.tryGetContext("certificateArn");
const googleClientIdParamName = app.node.tryGetContext("googleClientIdParamName");
const googleClientSecretArn = app.node.tryGetContext("googleClientSecretArn");
const githubClientIdParamName = app.node.tryGetContext("githubClientIdParamName");
const githubClientSecretArn = app.node.tryGetContext("githubClientSecretArn");
const oauthRedirectUriParamName = app.node.tryGetContext("oauthRedirectUriParamName");
const flaskSecretArn = app.node.tryGetContext("flaskSecretArn");

new AppStack(app, `${cfg.appName}-${stage}-app`, {
  env,
  description: `${cfg.appName} app (${stage})`,
  vpc: network.vpc,
  albSecurityGroup: network.albSecurityGroup,
  ecsSecurityGroup: network.ecsSecurityGroup,
  dbInstance: database.dbInstance,
  dbSecret: database.dbSecret,
  stage,
  imageSource,
  imageTag,
  enablePublicHttp: true,
  containerPort: 8000,
  appName: cfg.appName,
  dbName: cfg.dbName,
  certificateArn,
  googleClientIdParamName,
  googleClientSecretArn,
  githubClientIdParamName,
  githubClientSecretArn,
  oauthRedirectUriParamName,
  flaskSecretArn,
});
