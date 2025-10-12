# MCP — Advanced Features

**Conceptual guide to advanced MCP features: roots, sampling, progress, logging, stateful & stateless transport**

# Conceptual overview

MCP (as a control plane around tasks/events/data flowing through systems) must solve three fundamental problems simultaneously:

* **Correctness** — which source (root) is authoritative, how to represent lineage and versioning.
* **Efficiency** — how to process or surface only what matters (sampling), while preserving guarantees.
* **Resilience & UX** — make long-running processes observable (progress, logging), and choose transport semantics (stateful vs stateless) that align with consistency/scale goals.

The following sections break down each advanced feature area and present theoretical foundations and practical implications.

---

# Roots (canonical sources & lineage)

## Definition

Roots define lineage and ownership, and they anchor identity, replayability, and conflict resolution.

## Why roots matter

* **Determinism & replay**: If you know the root and all derived transforms, you can recompute or replay outcomes deterministically.
* **Conflict resolution**: When multiple sources produce variants, roots help prioritize and reconcile.
* **Auditing**: Business/legal audits require knowing the original source and the derivation chain.

# Sampling (selection strategies & guarantees)

## Definition

Sampling is the strategy that chooses a subset of items (events, messages, data points) from a larger stream or dataset for processing, inspection, or storage.

## Use cases

* Observability: sample logs/traces to control cost.
* Model training: select representative examples.
* User-facing features: show a small, relevant set of tasks.

# Progress

## Purpose

Progress tracking makes long-running tasks transparent and resumable. It helps users, operators, and other systems understand where a work item is in its lifecycle.

# Logging (observability, schema, retention)

## Purpose

Logging is how you observe system behavior, debug problems, and produce audit trails.

# Transport modes: stateful vs stateless (trade-offs & patterns)

## Definitions

* **Stateful transport**: the transport layer (or connection) maintains session/state across multiple requests (e.g., persistent TCP connections, websockets, or sessions in application layer).
* **Stateless transport**: each request is independent and contains all necessary context (e.g., REST over HTTP with tokens).

## Trade-offs

### Scalability

* **Stateless** systems scale horizontally more easily (no affinity needed).
* **Stateful** systems require sticky sessions or shared state stores.

### Latency & Efficiency

* **Stateful** transports (long-lived connections) reduce handshake overhead and can be more efficient for streaming/real-time.
* **Stateless** transports have per-request overhead but fit well with CDNs, load balancers.

### Consistency & Reliability

* **Stateful** allows continuous progress tracking per connection (useful for long-running transports and back-and-forth protocols).
* **Stateless** requires embedding ids/checkpoints in each message to maintain state semantics.

### Failure modes

* **Stateful**: connection loss means loss of in-memory session; need session persistence or reconnection logic.
* **Stateless**: requires idempotency/dedup to avoid reprocessing.

## Patterns & best practices

1. **Stateful transport with persistent backing**

   * Use ephemeral connection + durable checkpoint store (Redis, DB). On reconnect, resume using last checkpoint.
2. **Stateless transport with session tokens**

   * Encode minimal resume state in token or use session store keyed by token.
3. **Hybrid**

   * Use stateful websockets for live interaction and fallback to stateless HTTP for background processing & recovery.

## When to choose what

* Use **stateless** when: you need massive horizontal scale, short-lived requests, or easy caching/load-balancing.
* Use **stateful** when: you need real-time streaming, low-latency two-way communication, or continuous context that is expensive to rehydrate.
