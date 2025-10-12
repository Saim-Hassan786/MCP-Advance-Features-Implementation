# MCP Advanced Concepts — Roots, Sampling, Progress, Logging, and Transport

## Roots

### Definition & Purpose  
In MCP, **roots** refer to filesystem or workspace boundaries that clients expose to servers, defining **where** servers may operate (i.e. file access scopes).  
They act as safety and scoping constructs: servers request the root listing, and all server-side file or resource operations should respect those roots.

### Specification & Capabilities  
- Clients declare a `roots` capability during handshake (e.g. `"roots": { "listChanged": true }`)  
- Servers issue requests using the `roots/list` method to learn which roots the client has exposed.  
- Clients may emit notifications (`notifications/roots/list_changed`) if the set of roots changes.  
- A root object includes:
  - `uri` (a `file://` URI)  
  - Optional `name` for display  
  - The protocol currently expects `file://` URIs in the standard.  

### Security & Boundaries  
- Servers must **validate** that operations stay within declared roots (no path traversal)  
- Clients should restrict exposure of sensitive roots and require user consent  
- If roots become unavailable or change, servers must handle gracefully (fail or degrade)   

## Sampling

### Concept & Role in MCP  
Sampling provides a mechanism by which a **server** can request that the **client** invoke an LLM (or other model) to generate completions, under client control, enabling “agentic” workflows.  
In effect, sampling moves the model invocation into the client’s domain so that the client (and ultimately the user) retains control over what the LLM sees and generates.

### Flow & Message Format  
1. Server sends a `sampling/createMessage` request to client  
2. Client reviews or may modify the request (e.g. sanitization, filtering)  
3. Client performs the sampling (calls its LLM)  
4. Client may review or filter the response  
5. Client returns the sampled result back to the server 

#### Key fields in the sampling request include:
- `messages[]`: conversation history  
- `modelPreferences`: hints on preferred models (cost, speed, intelligence)  
- `temperature`, `maxTokens`, `stopSequences`  
- `includeContext`: which context to include (none, this server, all servers)  
- `metadata`: optional params  

The response includes:
- `model`: which model was used  
- `role`, `content` (text or image)  
- `stopReason`, etc. 

### Guarantees & Controls  
- **User oversight**: since sampling is client-executed, users can inspect, sanitize, or reject before returning.  
- **Privacy & security**: client controls which context is exposed.  
- **Consistency & determinism**: through deterministic choices (e.g. seed) where desired.

### Limitations & Best Practices  
- Clients may impose rate limits or filter requests  
- Clients must validate or sanitize model output  
- Sampling may not be supported by all clients (e.g. Claude Desktop currently doesn’t support sampling) 
- Avoid over-invoking sampling to manage cost  
- Use coherent context inclusion (`includeContext`) to limit token bloat  


## Progress & Checkpointing

### Why Progress Matters  
In MCP, many operations or tool calls may be long-running or multi-step. Clients and servers both benefit from progress reporting, so users or orchestrators know the state and can resume or cancel mid-work.

While the MCP spec defines support for **progress** utilities, the detailed semantics depend on implementation choices (the spec mentions “progress tracking” as an additional utility)

### Conceptual Model  
- **Progress event**: structured message indicating `{ stage, percentComplete, metadata }`  
- **Checkpoint**: persistent snapshot of intermediate state, enabling resumability or retries  
- **Monotonicity**: progress should not regress (unless rollback)  
- **Idempotence**: resumed work from checkpoint should yield the same end state when repeated  

### Implementation Patterns  
- Emit progress events periodically (e.g. every N records or after each sub-stage)  
- Map internal states to public progress (e.g. “fetching → processing → writing”)  
- Optionally include ETA, last processed ID, counts  
- In architectures with checkpoints, wrap durable side effects and checkpoint writes in the same atomic transaction  

### Guarantees & Trade-offs  
- Provides **visibility** into long-running tasks  
- Supports **interruption and resumption**  
- Requires careful design to maintain **idempotence**  
- Checkpoint frequency is a trade-off (fine-grained → higher overhead; coarse → more rework on failure)


## Logging & Notifications

### Role in MCP  
Logging and notifications are part of the MCP specification’s “additional utilities.” They let servers emit structured messages to clients (or hosts) to indicate status, diagnostics, or events.

### Logging / Notification Message Types  
- **Log messages**: e.g. `notifications/log` method, carrying structured log entries  
- **Notifications**: for things like root list changes, resources or tools being added or removed  
- **Progress / sampling / cancellation events** may use notification-style channels  

### Schema & Structure  
Log entries generally include:
- Timestamp  
- Severity (INFO, WARN, ERROR, DEBUG)  
- Component / module  
- Root or request IDs (for correlation)  
- Message or structured payload  

Notifications often are one-way (no RPC response expected), e.g. `notifications/roots/list_changed` 

### Guarantees & Best Practices  
- **Causality linking**: logs and notifications should include trace or request IDs for correlation  
- **Structured format**: use JSON or typed objects, not free-form text  
- **Filter / sampling**: high-volume logs may be sampled or aggregated  
- **Retention & redaction**: sensitive data must be sanitized; clients/hosts choose retention policies  


## Transport Modes: Stateful vs Stateless in MCP

### Default MCP Design (Stateful, Long-lived)

The core MCP spec assumes a **stateful, long-lived connection** between client and server (e.g. via STDIO or streaming HTTP) to support:
- Server-initiated requests (e.g. sampling, notifications)  
- Progress updates or logging pushed from server  
- Subscriptions or tool/resource changes pushed dynamically  
- Bidirectional flows beyond simple request-response 

The protocol is not optimized for ephemeral request/close patterns — repeated short connections break features like notifications.

### Stateless / HTTP-only Mode (degraded features)

Because long-lived connections are harder to scale or deploy (especially in serverless / autoscaling environments), MCP supports a **stateless HTTP fallback** (or a “stateless” mode) that sacrifices certain features.

#### What is lost in stateless mode:
- No server-to-client push (notifications, root changes)  
- No sampling requests (server can’t ask client to sample)  
- No streaming progress / intermediate logs (only final result)  
- Subscriptions, dynamic updates, or real-time flows are disabled  

#### What remains:
- Basic tool / resource calls in request–response style  
- Simpler scaling and load balancing (no sticky sessions needed)  
- Simpler deployment in stateless infra  

#### Configuration flags and decisions  
- The `stateless_http = true` mode disables the streaming path and pushes the protocol into simpler request/response behavior.  
- Some MCP implementations allow hybrid behaviors: e.g. use HTTP + SSE/streaming where possible, fallback gracefully.   
- Clients/servers must negotiate capabilities (e.g. whether notifications, sampling, progress are supported) during handshake.  

### Trade-offs & Architectural Implications

| Feature | Stateful / Streaming | Stateless / HTTP-only |
|---|---|---|
| Notifications & server push | ✅ | ❌ |
| Sampling | ✅ | ❌ |
| Real-time progress | ✅ | ❌ (only final) |
| Scalability / load balancing | Less easy (session affinity) | Easier |
| Complexity | More complex | Simpler |
| Fault tolerance | Requires session recovery | Simpler retry logic |
| Use-case suitability | Interactive, agentic, long workflows | Simple APIs, scalable services |

While stateful mode unlocks full MCP capability, many deployment environments favor the simplicity of stateless mode — hence hybrid or fallback modes are common in real-world MCP stacks.

---

## Interplay & Architectural Trade-offs

- **Roots & Transport**: The server may push root updates via notifications if using stateful transport; in stateless mode, changes may be pulled.  
- **Sampling & Transport**: Sampling requires server-to-client requests, so it is only viable in stateful / streaming contexts.  
- **Progress & Transport**: Live progress updates depend
