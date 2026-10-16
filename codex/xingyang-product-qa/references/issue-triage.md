# Issue triage

Classify the failing boundary from evidence. Do not infer personal fault from Git history, and do not treat the existence of an API call as proof that the backend is defective.

## Evidence chain

Build the shortest chain that explains the reported behavior:

1. User, role, page, entry point, and preconditions.
2. Expected behavior and observed behavior. If either is missing, state what must be reproduced or confirmed.
3. Frontend visibility, validation, state transitions, permissions, loading, empty, success, and failure handling.
4. Request trigger, endpoint, method, parameters, payload construction, and duplicate or missing requests.
5. Documented contract, returned status and body, response mapping, and error handling.
6. Environment, account permissions, feature flags, dictionaries, data prerequisites, and deployment differences.

Static frontend code can establish what the browser is designed to do. Runtime requests, responses, logs, and live configuration are needed to establish which deployed subsystem actually failed.

## Classification

| Classification | Evidence pattern | Recommendation |
| --- | --- | --- |
| Frontend leaning | The request is never sent when it should be; payload is built incorrectly; frontend state, permission, rendering, validation, or response mapping contradicts the confirmed contract | Frontend checks and fixes the local flow; backend helps confirm the contract when needed |
| Backend leaning | The frontend sends a contract-compliant request, but the captured response, server log, or documented server behavior is incorrect | Backend investigates data, permission, state transition, or service error; frontend verifies recovery and messaging |
| Integration or contract | Frontend behavior and API contract disagree, fields or enums differ, or both sides make incompatible assumptions | Product, frontend, and backend align one contract and acceptance example, then both sides adjust and verify |
| Configuration or environment | The issue depends on account permission, tenant data, feature flag, dictionary, deployment, or environment-specific configuration | The owner of the configuration validates the affected environment; engineering verifies graceful handling |
| Insufficient evidence | Only a symptom is available, or static code cannot locate the failing boundary | Reproduce and collect the minimum runtime evidence before assigning a subsystem |

Use “前端倾向”, “后端倾向”, “接口契约/联调”, “配置/环境”, or “证据不足”. Do not force every issue into frontend or backend.

## Confidence

- High: the expected contract and runtime boundary evidence both identify the failing subsystem.
- Medium: static implementation and documented contract strongly point to one boundary, but runtime evidence is incomplete.
- Low: based mainly on the symptom, an indirect code path, or missing expected behavior.

Always state the confidence and the evidence that would raise it.

## Resolution proposal

Write the user-visible target first. Then identify:

- which subsystem or role should investigate first;
- the exact state, permission, field, contract, or data condition to check;
- whether frontend and backend must coordinate;
- observable acceptance checks for normal, boundary, role/permission, failure, and recovery cases;
- a suggested technical contact from Git history only when it helps route the investigation.

Never name an individual as the cause of a defect. A contributor can be a suggested contact because of relevant recent changes, with dates and commits as evidence.
