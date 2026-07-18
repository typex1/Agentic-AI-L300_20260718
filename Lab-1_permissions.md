# Lab 1 - Permissions Extracted from AgenticAI-L300_lab1_CFN.yaml

## Foundation Model

- **Model ID:** `amazon.nova-pro-v1:0`
- **Inference Profile:** `us.amazon.nova-pro-v1:0`

---

## Service Linked Role

- **Service:** `runtime-identity.bedrock-agentcore.amazonaws.com`
- **Role:** `AWSServiceRoleForBedrockAgentCoreRuntimeIdentity`

---

## Code Editor Instance Policy (CodeEditorCombinedPolicy)

### S3 Permissions

| Action | Resource |
|--------|----------|
| `s3:PutObject` | `arn:aws:s3:::sagemaker-{Region}-{AccountId}/*`, `arn:aws:s3:::bedrock-agentcore-codebuild-sources-{AccountId}-{Region}/*` |
| `s3:PutEncryptionConfiguration` | `arn:aws:s3:::sagemaker-{Region}-{AccountId}`, `arn:aws:s3:::bedrock-agentcore-codebuild-sources-{AccountId}-{Region}` |
| `s3:PutLifecycleConfiguration` | Same as above |
| `s3:PutBucketVersioning` | Same as above |
| `s3:PutBucketPublicAccessBlock` | Same as above |
| `s3:CreateBucket` | `arn:aws:s3:::sagemaker-{Region}-{AccountId}`, `arn:aws:s3:::bedrock-agentcore-codebuild-sources-{AccountId}-{Region}` |
| `s3:DeleteObject` | `arn:aws:s3:::bedrock-agentcore-codebuild-sources-*/*` |
| `s3:DeleteObjectVersion` | Same as above |
| `s3:DeleteBucket` | `arn:aws:s3:::bedrock-agentcore-codebuild-sources-*` |

### IAM Permissions

| Action | Resource | Condition |
|--------|----------|-----------|
| `iam:PassRole` | `arn:aws:iam::{AccountId}:role/AmazonBedrockAgentCoreSDKCodeBuild-{Region}-5d12c2867b` | `iam:PassedToService: codebuild.amazonaws.com` |
| `iam:PassRole` | `arn:aws:iam::{AccountId}:role/AmazonBedrockAgentCoreSDKRuntime-{Region}` | `iam:PassedToService: bedrock-agentcore.amazonaws.com` |

### Bedrock Model Invocation Permissions

| Action | Resource |
|--------|----------|
| `bedrock:TagResource` | `arn:aws:bedrock:*::foundation-model/amazon.nova-pro-v1:0`, `arn:aws:bedrock:*:*:inference-profile/us.amazon.nova-pro-v1:0` |
| `bedrock:UntagResource` | Same as above |
| `bedrock:InvokeModel` | Same as above |
| `bedrock:InvokeModelWithResponseStream` | Same as above |

### Bedrock Guardrails Permissions

| Action | Resource |
|--------|----------|
| `bedrock:CreateGuardrail` | `*` |
| `bedrock:ListGuardrails` | `*` |
| `bedrock:ApplyGuardrail` | `arn:aws:bedrock:{Region}:{AccountId}:guardrail/*` |
| `bedrock:CreateGuardrailVersion` | Same as above |
| `bedrock:DeleteGuardrail` | Same as above |
| `bedrock:UpdateGuardrail` | Same as above |

### ECR Permissions

| Action | Resource |
|--------|----------|
| `ecr:PutLifecyclePolicy` | `arn:aws:ecr:{Region}:{AccountId}:repository/bedrock-agentcore-personal_finance_agent` |
| `ecr:SetRepositoryPolicy` | Same as above |
| `ecr:InitiateLayerUpload` | Same as above |
| `ecr:UploadLayerPart` | Same as above |
| `ecr:CompleteLayerUpload` | Same as above |
| `ecr:PutImage` | Same as above |
| `ecr:DeleteRepository` | Same as above |
| `ecr:CreateRepository` | Same as above |

### CodeBuild Permissions

| Action | Resource |
|--------|----------|
| `codebuild:CreateProject` | `arn:aws:codebuild:{Region}:{AccountId}:project/bedrock-agentcore-personal_finance_agent-builder` |
| `codebuild:StartBuild` | Same as above |
| `codebuild:UpdateProject` | Same as above |
| `codebuild:ListProjects` | Same as above |
| `codebuild:DeleteProject` | Same as above |
| `codebuild:BatchGetProjects` | Same as above |

### Cognito Permissions

| Action | Resource |
|--------|----------|
| `cognito-idp:CreateResourceServer` | `arn:aws:cognito-idp:{Region}:{AccountId}:userpool/*` |
| `cognito-idp:AdminSetUserPassword` | Same as above |
| `cognito-idp:CreateUserPool` | Same as above |
| `cognito-idp:CreateUserPoolClient` | Same as above |
| `cognito-idp:AdminCreateUser` | Same as above |
| `cognito-idp:CreateUserPoolDomain` | Same as above |
| `cognito-idp:DeleteUserPool` | Same as above |
| `cognito-idp:AdminDeleteUser` | Same as above |
| `cognito-idp:UpdateUserPoolClient` | Same as above |
| `cognito-idp:DeleteUserPoolClient` | Same as above |

### Secrets Manager Permissions

| Action | Resource |
|--------|----------|
| `secretsmanager:CreateSecret` | `arn:aws:secretsmanager:{Region}:{AccountId}:secret:agentcore-lab-credentials-*` |
| `secretsmanager:GetSecretValue` | Same as above |
| `secretsmanager:DeleteSecret` | Same as above |
| `secretsmanager:PutSecretValue` | Same as above |
| `secretsmanager:UpdateSecret` | Same as above |
| `secretsmanager:TagResource` | Same as above |
| `secretsmanager:UntagResource` | Same as above |

### AgentCore Runtime Permissions

| Action | Resource |
|--------|----------|
| `bedrock-agentcore:CreateAgentRuntime` | `arn:aws:bedrock-agentcore:{Region}:{AccountId}:runtime/*` |
| `bedrock-agentcore:CreateAgentRuntimeEndpoint` | `arn:aws:bedrock-agentcore:{Region}:{AccountId}:runtime/personal_finance_agent-*/runtime-endpoint/DEFAULT` |
| `bedrock-agentcore:CreateWorkloadIdentity` | `arn:aws:bedrock-agentcore:{Region}:{AccountId}:workload-identity-directory/default`, `...default/workload-identity/*` |
| `bedrock-agentcore:DeleteWorkloadIdentity` | Same as above |
| `bedrock-agentcore:UploadWorkloadIdentity` | Same as above |
| `bedrock-agentcore:InvokeAgentRuntime` | `arn:aws:bedrock-agentcore:{Region}:{AccountId}:runtime/*` |
| `bedrock-agentcore:DeleteAgentRuntime` | Same as above |
| `bedrock-agentcore:DeleteAgentRuntimeEndpoint` | `arn:aws:bedrock-agentcore:{Region}:{AccountId}:runtime/personal_finance_agent-*/runtime-endpoint/DEFAULT` |

### AgentCore Memory Permissions

| Action | Resource |
|--------|----------|
| `bedrock-agentcore:CreateMemory` | `arn:aws:bedrock-agentcore:{Region}:{AccountId}:memory/FinancialAdvisorMemory-*` |
| `bedrock-agentcore:CreateEvent` | Same as above |
| `bedrock-agentcore:DeleteMemory` | Same as above |

### CloudWatch Logs Permissions

| Action | Resource |
|--------|----------|
| `logs:DeleteLogGroup` | `arn:aws:logs:{Region}:{AccountId}:log-group:/aws/bedrock-agentcore/runtimes/*`, `arn:aws:logs:{Region}:{AccountId}:log-group:/aws/codebuild/bedrock-agentcore-*` |

### Additional Attached Policy

- `arn:aws:iam::aws:policy/ReadOnlyAccess`

---

## CodeBuild Role (AmazonBedrockAgentCoreSDKCodeBuild-{Region}-5d12c2867b)

**Assumed by:** `codebuild.amazonaws.com`

| Action | Resource |
|--------|----------|
| `ecr:GetAuthorizationToken` | `*` |
| `ecr:BatchCheckLayerAvailability` | `arn:aws:ecr:{Region}:{AccountId}:repository/bedrock-agentcore-personal_finance_agent` |
| `ecr:BatchGetImage` | Same as above |
| `ecr:GetDownloadUrlForLayer` | Same as above |
| `ecr:PutImage` | Same as above |
| `ecr:InitiateLayerUpload` | Same as above |
| `ecr:UploadLayerPart` | Same as above |
| `ecr:CompleteLayerUpload` | Same as above |
| `logs:CreateLogGroup` | `arn:aws:logs:{Region}:{AccountId}:log-group:/aws/codebuild/bedrock-agentcore-*` |
| `logs:CreateLogStream` | Same as above |
| `logs:PutLogEvents` | Same as above |
| `s3:GetObject` | `arn:aws:s3:::bedrock-agentcore-codebuild-sources-{AccountId}-{Region}/*` |

---

## AgentCore Runtime Role (AmazonBedrockAgentCoreSDKRuntime-{Region})

**Assumed by:** `bedrock-agentcore.amazonaws.com`

### ECR Access

| Action | Resource |
|--------|----------|
| `ecr:BatchGetImage` | `arn:aws:ecr:{Region}:{AccountId}:repository/bedrock-agentcore-personal_finance_agent` |
| `ecr:GetDownloadUrlForLayer` | Same as above |
| `ecr:GetAuthorizationToken` | `*` |

### CloudWatch Logs

| Action | Resource |
|--------|----------|
| `logs:DescribeLogStreams` | `arn:aws:logs:{Region}:{AccountId}:log-group:/aws/bedrock-agentcore/runtimes/*` |
| `logs:CreateLogGroup` | Same as above |
| `logs:DescribeLogGroups` | `*` |
| `logs:CreateLogStream` | `arn:aws:logs:{Region}:{AccountId}:log-group:/aws/bedrock-agentcore/runtimes/*:log-stream:*` |
| `logs:PutLogEvents` | Same as above |

### X-Ray Telemetry

| Action | Resource |
|--------|----------|
| `xray:PutTraceSegments` | `*` |
| `xray:PutTelemetryRecords` | `*` |
| `xray:GetSamplingRules` | `*` |
| `xray:GetSamplingTargets` | `*` |

### CloudWatch Metrics

| Action | Resource | Condition |
|--------|----------|-----------|
| `cloudwatch:PutMetricData` | `*` | `cloudwatch:namespace = bedrock-agentcore` |

### AgentCore Runtime Invocation

| Action | Resource |
|--------|----------|
| `bedrock-agentcore:InvokeAgentRuntime` | `arn:aws:bedrock-agentcore:{Region}:{AccountId}:runtime/*` |

### AgentCore Memory

| Action | Resource |
|--------|----------|
| `bedrock-agentcore:CreateMemory` | `*` |
| `bedrock-agentcore:CreateEvent` | `arn:aws:bedrock-agentcore:{Region}:{AccountId}:memory/*` |
| `bedrock-agentcore:GetEvent` | Same as above |
| `bedrock-agentcore:GetMemory` | Same as above |
| `bedrock-agentcore:GetMemoryRecord` | Same as above |
| `bedrock-agentcore:ListActors` | Same as above |
| `bedrock-agentcore:ListEvents` | Same as above |
| `bedrock-agentcore:ListMemoryRecords` | Same as above |
| `bedrock-agentcore:ListSessions` | Same as above |
| `bedrock-agentcore:DeleteEvent` | Same as above |
| `bedrock-agentcore:DeleteMemoryRecord` | Same as above |
| `bedrock-agentcore:RetrieveMemoryRecords` | Same as above |

### AgentCore Identity - API Key Access

| Action | Resource |
|--------|----------|
| `bedrock-agentcore:GetResourceApiKey` | `arn:aws:bedrock-agentcore:{Region}:{AccountId}:token-vault/default`, `...token-vault/default/apikeycredentialprovider/*`, `...workload-identity-directory/default`, `...workload-identity-directory/default/workload-identity/personal_finance_agent-*` |

### AgentCore Identity - OAuth2 Token Access

| Action | Resource |
|--------|----------|
| `bedrock-agentcore:GetResourceOauth2Token` | `arn:aws:bedrock-agentcore:{Region}:{AccountId}:token-vault/default`, `...token-vault/default/oauth2credentialprovider/*`, `...workload-identity-directory/default`, `...workload-identity-directory/default/workload-identity/personal_finance_agent-*` |

### AgentCore Identity - Workload Access Token

| Action | Resource |
|--------|----------|
| `bedrock-agentcore:GetWorkloadAccessToken` | `arn:aws:bedrock-agentcore:{Region}:{AccountId}:workload-identity-directory/default`, `...workload-identity-directory/default/workload-identity/personal_finance_agent-*` |
| `bedrock-agentcore:GetWorkloadAccessTokenForJWT` | Same as above |
| `bedrock-agentcore:GetWorkloadAccessTokenForUserId` | Same as above |

### Bedrock Model Invocation (Runtime)

| Action | Resource |
|--------|----------|
| `bedrock:InvokeModel` | `arn:aws:bedrock:*::foundation-model/amazon.nova-pro-v1:0`, `arn:aws:bedrock:*:*:inference-profile/us.amazon.nova-pro-v1:0` |
| `bedrock:InvokeModelWithResponseStream` | Same as above |
| `bedrock:ApplyGuardrail` | `arn:aws:bedrock:{Region}:{AccountId}:guardrail-profile/*`, `arn:aws:bedrock:{Region}:{AccountId}:guardrail/*` |

---

## Summary of Key AgentCore Permissions

| Category | Actions |
|----------|---------|
| **Runtime Management** | CreateAgentRuntime, DeleteAgentRuntime, CreateAgentRuntimeEndpoint, DeleteAgentRuntimeEndpoint, InvokeAgentRuntime |
| **Memory Management** | CreateMemory, CreateEvent, GetEvent, GetMemory, GetMemoryRecord, ListActors, ListEvents, ListMemoryRecords, ListSessions, DeleteEvent, DeleteMemory, DeleteMemoryRecord, RetrieveMemoryRecords |
| **Identity Management** | CreateWorkloadIdentity, DeleteWorkloadIdentity, UploadWorkloadIdentity, GetWorkloadAccessToken, GetWorkloadAccessTokenForJWT, GetWorkloadAccessTokenForUserId |
| **Token Vault** | GetResourceApiKey, GetResourceOauth2Token |
| **Model Access** | InvokeModel, InvokeModelWithResponseStream (amazon.nova-pro-v1:0) |
| **Guardrails** | CreateGuardrail, ListGuardrails, ApplyGuardrail, CreateGuardrailVersion, DeleteGuardrail, UpdateGuardrail |
