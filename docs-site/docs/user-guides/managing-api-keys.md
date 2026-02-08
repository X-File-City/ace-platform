---
sidebar_position: 3
---

# Managing API Keys

Create and manage API keys to authenticate MCP tool access with ACE.

## Overview

API keys authenticate your MCP tool requests to ACE. Each key has specific scopes that control what actions it can perform.

## Creating API Keys

### Prerequisites

- Verified email address
- Active ACE account

### From the Dashboard

1. Log in to [app.aceagent.io](https://app.aceagent.io)
2. Navigate to **API Keys** in the sidebar
3. Click **Create API Key**
4. Configure your key:
   - **Name** - Descriptive name (e.g., "Production Agent", "Local Dev")
   - **Scopes** - Select required permissions
5. Click **Create**
6. **Copy your key immediately** - it won't be shown again!

## API Key Scopes

| Scope | Description | Use Case |
|-------|-------------|----------|
| `playbooks:read` | View playbook content | Agents that use playbooks |
| `playbooks:write` | Create and update playbooks | Admin tools, dashboard |
| `outcomes:write` | Submit task outcomes | Active agents |
| `evolution:read` | View evolution status | Monitoring |
| `evolution:write` | Manually trigger evolution | Admin tools |

### Recommended Scope Combinations

**Production Agent (Read + Record):**
- `playbooks:read`
- `outcomes:write`

**Full Access:**
- Select All (all scopes)

**Monitoring Only:**
- `playbooks:read`
- `evolution:read`

## Using API Keys

### MCP Configuration

Pass your API key via the `X-API-Key` header in your MCP client config. See the [MCP Integration Overview](/docs/developer-guides/mcp-integration/overview) for setup instructions.

### Environment Variables

Store keys in environment variables for MCP clients and tooling:

```bash
export ACE_API_KEY="ace_..."
```

## Key Security

### Best Practices

1. **Never commit keys to version control**
   ```gitignore
   # .gitignore
   .env
   .env.local
   **/secrets/*
   ```

2. **Use environment variables**
   - Development: `.env` files
   - Production: Secret managers (AWS Secrets, Vault, etc.)

3. **Rotate keys regularly**
   - Create new key
   - Update configurations
   - Revoke old key

4. **Use minimum required scopes**
   - Production agents don't need `playbooks:write`
   - Read-only dashboards don't need write scopes

5. **Use separate keys per environment**
   - Development key
   - Staging key
   - Production key

### What to Do If a Key Is Compromised

1. **Immediately revoke the key** in the dashboard
2. **Create a new key** with the same scopes
3. **Update all configurations** using the old key
4. **Review activity logs** for unauthorized usage
5. **Rotate any other secrets** that might be exposed

## Viewing API Keys

Each key card on the dashboard shows:

- **Name** and **key prefix** (`ace_...`)
- **Scopes** as badges
- **Created** date and **last used** date

:::note
You cannot view the full key after creation. Only the prefix is shown.
:::

## Deleting API Keys

1. Go to **API Keys**
2. Click the **trash icon** on the key you want to delete
3. Confirm by clicking **Delete** in the confirmation prompt

:::warning
Deleting a key is immediate and irreversible. All requests using that key will fail.
:::

## Key Format

ACE API keys follow the format `ace_<random_string>`. The first 8 characters are stored as the key prefix for identification.

## Rate Limits

If you encounter rate limits, wait and retry with exponential backoff.

## Troubleshooting

### "Invalid API Key"

- Verify the key is copied correctly (no extra spaces)
- Check the key hasn't been revoked
- Ensure you're using the correct environment

### "Insufficient Scopes"

- Check the error message for required scope
- Create a new key with additional scopes
- Update your configuration

### "API Key Required"

- Verify the `X-API-Key` header is present
- Ensure the key isn't empty or malformed

### Key Not Working with MCP

- Verify the `X-API-Key` header is set in your MCP config
- Check the key is correct (no extra spaces)
- Restart your MCP client after config changes

## Next Steps

- [Set up MCP integration](/docs/developer-guides/mcp-integration/overview)
- [Monitor usage](/docs/user-guides/billing-subscriptions)
