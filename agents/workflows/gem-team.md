# Gem Team Execution Workflow

This workflow implements the 6-phase execution loop of the Gem Team architecture, optimized for the Antigravity orchestration pattern.

## Overview
The Central Agent Manager (gem-orchestrator) drives this workflow, spawning specialized sub-agents to complete each phase.

## Phase 1 & 2: Discuss and PRD
**Goal:** Capture user intent and establish the source of truth.

1. **Interact:** The Orchestrator MUST interact with the user to clarify the objective.
2. **Clarify:** Detect "gray areas" (APIs, UI, logic, data) and ask 3-5 targeted questions.
3. **PRD Output:** Generate or update `docs/PRD.yaml`.
   - Include: user_stories, in_scope, out_of_scope, acceptance_criteria, decisions.

## Phase 3 & 4: Research and Planning
**Goal:** Map the codebase and design a parallel execution strategy.

1. **Research Delegation:** Spawn `gem-researcher` sub-agents for each identified focus area.
2. **Workspace Evaluation:** Analyze existing patterns, dependencies, and architectural conventions.
3. **Planning Delegation:** Spawn `gem-planner` to create a DAG (Directed Acyclic Graph) of tasks.
4. **Plan Output:** Generate `docs/plan/{plan_id}/plan.yaml`.
   - Must include: wave assignments, agent assignments, and contracts between dependent tasks.
5. **Critique Gate:** Spawn `gem-critic` to audit the plan. If blocking issues found, loop back to Planning.

## Phase 5: Execution (The Wave)
**Goal:** Process independent tasks in parallel waves.

1. **Wave Identification:** Group tasks from `plan.yaml` into execution Waves based on their dependencies.
2. **Parallel Dispatch:** For each task in the current Wave:
   - Spawn a parallel sub-agent thread (e.g., `gem-implementer`, `gem-devops`, `gem-documentation-writer`).
   - Inject the specific role definition from `.agents/gem-team-roles/` into the sub-agent prompt.
3. **Synchronization:** Wait for ALL sub-agents in the current Wave to report their outputs.
4. **Integration Check:** After each Wave, the Orchestrator must verify that the changes co-exist correctly (build, lint, tests).

## Phase 6: Verification and Gates
**Goal:** Ensure absolute compliance with the PRD and quality standards.

1. **Verification Gate:** For each completed task/wave, the Orchestrator MUST review outputs against the `acceptance_criteria` in `PRD.yaml`.
2. **Specialized Audit:**
   - **UI Tasks:** Automatically spawn `gem-designer` to validate visual hierarchy and accessibility.
   - **Security-Sensitive:** Automatically spawn `gem-reviewer` for deep security audit.
3. **Failure Routing:**
   - IF a task fails or integration breaks:
     - Spawn `gem-debugger` persona to diagnose the root cause.
     - Inject the diagnosis into a new sub-agent for a targeted fix.
4. **Final Summary:** Present the execution results, including metrics (tasks completed, tests passed, coverage).

## Orchestration Rules
- **Autonomy:** Sub-agents execute to completion without interrupting the Orchestrator unless a critical blocker is found.
- **Context Injection:** Always provide sub-agents with the relevant `PRD.yaml` and `research_findings_*.yaml` sections.
- **State Management:** The Orchestrator updates `plan.yaml` status for every task completion.
