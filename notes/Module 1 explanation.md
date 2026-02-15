# Module 1: Three User Types

How to implement **Guests**, **Registered Clients**, and **Dispatch Operators** with the same auth stack (Cognito + DynamoDB + Lambda, 3FA).

---

## User types (from requirements)

| Type | Auth | Capabilities |
|------|------|--------------|
| **Guests** | None | View availability/pricing, virtual assistant, aggregated feedback |
| **Registered Clients** | 3FA | + Book services, chatbot, messaging with operators, submit feedback |
| **Dispatch Operators** | 3FA | + Manage services/pricing, bookings, analytics, messaging with clients |

---

## Implementation

**One Cognito User Pool** for Clients and Operators (same 3FA). Guests do not have accounts.

**Role storage:** Store `role` (`"client"` or `"operator"`) in:
- Cognito custom attribute (e.g. `custom:role`), and/or  
- DynamoDB user profile (e.g. `userId`/`cognitoSub`, `role`, …).

**Creating operators:** Self-sign-up = client. Operators: admin creates account and sets `role` to `operator`, or admin promotes a user (update `role` in DynamoDB/Cognito).

**Enforcement:** After 3FA, every protected API/Lambda validates the token, resolves the user, and checks `role`. Guest-only routes require no token. Client-only endpoints return 403 if `role !== "client"`. Operator-only endpoints return 403 if `role !== "operator"`.

**Front-end:** Same login flow for Clients and Operators. After login, fetch profile (or decode token) for `role` and show the correct nav/features (client vs operator).
