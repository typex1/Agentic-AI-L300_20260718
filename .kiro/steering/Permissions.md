# AWS Permissions

This environment has limited AWS permissions. When creating solutions, only use actions that are permitted.

## Region

All AWS operations must target **us-east-1**.

## Foundation Model

- **Model ID:** `amazon.nova-pro-v1:0`
- **Inference Profile:** `us.amazon.nova-pro-v1:0`

## Allowed Bedrock Runtime Actions

| Action | Service |
|--------|---------|
| `Converse` | bedrock-runtime |
| `ConverseStream` | bedrock-runtime |
| `InvokeModel` | bedrock-runtime |
| `InvokeModelWithResponseStream` | bedrock-runtime |

## Allowed Bedrock Control-Plane Actions (Guardrails Only)

| Action | Service |
|--------|---------|
| `CreateGuardrail` | bedrock |
| `ListGuardrails` | bedrock |
| `ApplyGuardrail` | bedrock |
| `CreateGuardrailVersion` | bedrock |
| `DeleteGuardrail` | bedrock |
| `UpdateGuardrail` | bedrock |
| `TagResource` | bedrock |
| `UntagResource` | bedrock |

## Allowed Other Services

| Service | Actions |
|---------|---------|
| S3 | PutObject, CreateBucket, DeleteObject, DeleteObjectVersion, DeleteBucket, PutEncryptionConfiguration, PutLifecycleConfiguration, PutBucketVersioning, PutBucketPublicAccessBlock |
| IAM | PassRole (to codebuild.amazonaws.com and bedrock-agentcore.amazonaws.com only) |
| ECR | CreateRepository, DeleteRepository, PutLifecyclePolicy, SetRepositoryPolicy, InitiateLayerUpload, UploadLayerPart, CompleteLayerUpload, PutImage |
| CodeBuild | CreateProject, StartBuild, UpdateProject, ListProjects, DeleteProject, BatchGetProjects |
| Cognito | CreateUserPool, CreateUserPoolClient, CreateUserPoolDomain, CreateResourceServer, AdminCreateUser, AdminSetUserPassword, AdminDeleteUser, UpdateUserPoolClient, DeleteUserPoolClient, DeleteUserPool |
| Secrets Manager | CreateSecret, GetSecretValue, DeleteSecret, PutSecretValue, UpdateSecret, TagResource, UntagResource |
| Bedrock AgentCore | CreateAgentRuntime, DeleteAgentRuntime, CreateAgentRuntimeEndpoint, DeleteAgentRuntimeEndpoint, InvokeAgentRuntime, CreateMemory, CreateEvent, DeleteMemory, CreateWorkloadIdentity, DeleteWorkloadIdentity, UploadWorkloadIdentity |
| CloudWatch Logs | DeleteLogGroup |

## Denied Actions

| Action | Service | Notes |
|--------|---------|-------|
| `ListFoundationModels` | bedrock | Control-plane model listing is denied |
| `GetFoundationModel` | bedrock | Control-plane model info is denied |
| `GetGuardrail` | bedrock | Reading individual guardrail details is denied |
| `InvokeModel` on `amazon.nova-lite-v1:0` | bedrock-runtime | Only nova-pro is permitted |

## Additional Access

- `arn:aws:iam::aws:policy/ReadOnlyAccess` is attached (broad read access to most services).

## Rules

- The available model is `amazon.nova-pro-v1:0` (NOT nova-lite).
- Both the direct model ID and the inference profile `us.amazon.nova-pro-v1:0` work.
- Guardrail control-plane actions are permitted (create, list, update, delete, apply).
- Do not attempt to list or describe foundation models via the API.
- IAM management access is not available; do not attempt IAM operations beyond PassRole.
- The Strands Agents framework works because it uses `bedrock-runtime:Converse` / `ConverseStream`.
