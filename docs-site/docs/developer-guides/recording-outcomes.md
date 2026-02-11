---
sidebar_position: 6
---

# Recording Outcomes

Learn how to record effective outcomes that improve your playbooks over time.

## Why Record Outcomes?

Outcomes are the fuel for playbook evolution. They tell ACE:

- What works well (preserve it)
- What doesn't work (fix it)
- What's missing (add it)
- What's confusing (clarify it)

After 5 outcomes accumulate, ACE automatically triggers evolution to generate an improved playbook version.

## How to Record

Using Claude Desktop or Claude Code:

```
"Record an outcome for playbook abc-123:
- Task: Reviewed authentication PR with 300 lines of changes
- Outcome: success
- Notes: Caught SQL injection in user lookup, suggested parameterized query"
```

## Outcome Values

| Value | When to Use |
|-------|-------------|
| **success** | Task completed correctly with good results |
| **partial** | Task completed but with gaps or issues |
| **failure** | Task did not complete or results were wrong |

## Writing Effective Outcomes

### Task Description

Be specific about what was done:

- "Reviewed code" - too vague
- "Reviewed user authentication module PR (#234) with 300 lines of TypeScript changes" - gives evolution useful context

### Notes

Include actionable details:

- "It went well" - too vague for evolution to learn from
- "Caught SQL injection in user lookup function. Suggested parameterized queries. Missed rate limiting issue that was found later." - tells evolution what to reinforce and what to add

### Reasoning Trace

When available, include how the agent approached the task. This helps evolution understand the decision-making process and improve guidance for future tasks.

## Viewing Outcomes

1. Navigate to your playbook
2. Click the **Outcomes** tab
3. View all recorded outcomes

## Size Limits

| Field | Max Size |
|-------|----------|
| `task_description` | 10 KB |
| `notes` | 2 KB |
| `reasoning_trace` | 10 KB |

## Next Steps

- [Understanding evolution](/docs/user-guides/understanding-evolution)
- [MCP integration](/docs/developer-guides/mcp-integration/overview)
