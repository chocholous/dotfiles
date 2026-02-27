---
name: codex-second-opinion
description: Get second opinions and validation from OpenAI Codex CLI. Use when you need alternative AI perspective on architecture, code review, or to validate your own analysis and recommendations.
---

# Codex Second Opinion Skill

This skill enables you to leverage OpenAI's Codex CLI to get alternative AI perspectives on your work, validate architectural decisions, and cross-check your recommendations.

## When to Use This Skill

Invoke this skill when you need:

1. **Second opinions** - Validate your architectural decisions or implementation approach
2. **Code review from different perspective** - Get OpenAI's view on code you're analyzing
3. **Multi-model consensus** - Confirm your recommendations with another AI model
4. **Alternative solutions** - Explore different approaches to a problem
5. **Validation of analysis** - Double-check your understanding of complex code

## DO NOT Use This Skill For

- Simple questions you can answer directly
- Tasks that don't benefit from multiple perspectives
- When you're confident in your answer and validation isn't needed

## Usage Patterns

### 1. Basic Second Opinion (Simple Text Answer)

For straightforward validation questions:

```bash
codex exec --skip-git-repo-check --output-last-message /tmp/codex-opinion.txt "Your question or prompt here"
cat /tmp/codex-opinion.txt
```

**Example:**
```bash
codex exec --skip-git-repo-check --output-last-message /tmp/codex-opinion.txt \
  "Review this MCP server architecture approach: [describe]. What are the pros, cons, and alternatives?"
cat /tmp/codex-opinion.txt
```

### 2. Structured Opinion with JSON Schema

When you need predictable, parseable output:

```bash
# Create schema for structured response
cat > /tmp/opinion-schema.json << 'EOF'
{
  "type": "object",
  "additionalProperties": false,
  "properties": {
    "assessment": { "type": "string" },
    "strengths": {
      "type": "array",
      "items": { "type": "string" }
    },
    "concerns": {
      "type": "array",
      "items": { "type": "string" }
    },
    "alternatives": {
      "type": "array",
      "items": { "type": "string" }
    },
    "recommendation": { "type": "string" }
  },
  "required": ["assessment", "strengths", "concerns", "alternatives", "recommendation"]
}
EOF

# Get structured opinion
codex exec --skip-git-repo-check --output-schema /tmp/opinion-schema.json \
  --output-last-message /tmp/opinion.json \
  "Evaluate this approach: [your approach description]"

# Process result
cat /tmp/opinion.json
```

### 3. Code Review Validation

Get Codex's perspective on code you're reviewing:

```bash
codex exec --skip-git-repo-check --output-last-message /tmp/code-review.txt \
  "Review the code in [file:path] focusing on [security/performance/architecture].
  I think [your assessment]. Do you agree or see different issues?"
cat /tmp/code-review.txt
```

## Common Use Cases

### Use Case 1: Validate Architectural Decision

```bash
# Ask Codex to validate your architectural choice
codex exec --skip-git-repo-check --output-last-message /tmp/arch-validation.txt \
  "I'm designing an MCP server with CLI bridge pattern instead of direct Python implementation.
  My reasoning: [explain your reasoning].
  Evaluate this decision and suggest alternatives if this isn't optimal."

cat /tmp/arch-validation.txt
```

### Use Case 2: Get Alternative Implementation Ideas

```bash
# Create schema for implementation comparison
cat > /tmp/implementation-schema.json << 'EOF'
{
  "type": "object",
  "additionalProperties": false,
  "properties": {
    "approaches": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "properties": {
          "name": { "type": "string" },
          "pros": { "type": "array", "items": { "type": "string" } },
          "cons": { "type": "array", "items": { "type": "string" } },
          "complexity": { "type": "string" }
        },
        "required": ["name", "pros", "cons", "complexity"]
      }
    },
    "recommended": { "type": "string" }
  },
  "required": ["approaches", "recommended"]
}
EOF

codex exec --skip-git-repo-check --output-schema /tmp/implementation-schema.json \
  --output-last-message /tmp/implementations.json \
  "What are different approaches to implement [feature X]? Compare them."

cat /tmp/implementations.json
```

### Use Case 3: Security Review Double-Check

```bash
codex exec --skip-git-repo-check --output-last-message /tmp/security-review.txt \
  "I reviewed [file:path] for security issues. I found: [list your findings].
  Did I miss anything? Are there additional security concerns?"

cat /tmp/security-review.txt
```

### Use Case 4: Test Coverage Analysis

```bash
cat > /tmp/coverage-schema.json << 'EOF'
{
  "type": "object",
  "additionalProperties": false,
  "properties": {
    "coverage_assessment": { "type": "string" },
    "well_tested": { "type": "array", "items": { "type": "string" } },
    "missing_tests": { "type": "array", "items": { "type": "string" } },
    "test_priorities": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "properties": {
          "area": { "type": "string" },
          "priority": { "type": "string" },
          "rationale": { "type": "string" }
        },
        "required": ["area", "priority", "rationale"]
      }
    }
  },
  "required": ["coverage_assessment", "well_tested", "missing_tests", "test_priorities"]
}
EOF

codex exec --skip-git-repo-check --output-schema /tmp/coverage-schema.json \
  --output-last-message /tmp/coverage.json \
  "Analyze test coverage in [directory/file]. What's missing?"

cat /tmp/coverage.json
```

## Key Parameters Reference

### Model Selection
```bash
codex exec --skip-git-repo-check -m gpt-5.3-codex "prompt"   # GPT-5.3-Codex (latest, best reasoning)
codex exec --skip-git-repo-check -m gpt-5.2-codex "prompt"   # GPT-5.2-Codex (default)
# Default model (gpt-5.2-codex) is usually sufficient
# NOTE: o4-mini does NOT work with ChatGPT accounts
```

### Working Directory
```bash
codex exec --skip-git-repo-check -C /path/to/project "analyze this project structure"
```

### Sandbox Mode
```bash
# exec command defaults to read-only (safe)
codex exec --skip-git-repo-check --sandbox read-only "prompt"
```

### Approval Policy
```bash
# exec defaults to -a never (no interruptions)
codex exec --skip-git-repo-check -a never "prompt"
```

## Best Practices

### 1. Always Save Output to /tmp
```bash
# Good: Ephemeral files in /tmp
codex exec --skip-git-repo-check --output-last-message /tmp/codex-answer.txt "question"

# Avoid: Creating files in project directory
# codex exec --output-last-message ./answer.txt "question"
```

### 2. Provide Context in Your Prompts
```bash
# Good: Detailed context
codex exec --skip-git-repo-check --output-last-message /tmp/opinion.txt \
  "I'm building an MCP server for X. Current approach is Y because Z.
  Evaluate if this is the best approach or suggest alternatives."

# Less effective: Vague question
# codex exec --output-last-message /tmp/opinion.txt "Is MCP server good?"
```

### 3. Compare and Present Both Perspectives
```bash
# Get Codex opinion
codex exec --skip-git-repo-check --output-last-message /tmp/codex-view.txt "Evaluate [approach]"

# Then present both views to user:
echo "=== MY ANALYSIS ==="
echo "[Your analysis]"
echo ""
echo "=== CODEX SECOND OPINION ==="
cat /tmp/codex-view.txt
```

### 4. Use JSON Schemas for Complex Analysis
When you need structured comparison or multiple data points, use JSON schemas for reliable parsing.

### 5. Ask Specific Questions
```bash
# Good: Specific
"What are security concerns with this authentication implementation in auth.py:45-67?"

# Less effective: Too broad
"Is this code good?"
```

## Authentication

Codex requires authentication. Check first:

```bash
codex --version  # Should show version if authenticated
```

If not authenticated, user needs to run:
```bash
# Method 1: ChatGPT login (Plus/Pro/Team/Enterprise)
codex login

# Method 2: OpenAI API key
printenv OPENAI_API_KEY | codex login --with-api-key
```

## Error Handling

```bash
# Check if codex is available
if ! command -v codex &> /dev/null; then
    echo "Codex CLI not installed. User needs to install it first."
    exit 1
fi

# Run with error handling
if codex exec --skip-git-repo-check --output-last-message /tmp/answer.txt "question"; then
    cat /tmp/answer.txt
else
    echo "Codex execution failed. Check authentication or prompt."
    exit 1
fi
```

## Workflow Example

When using this skill, follow this pattern:

1. **Analyze the task** yourself first
2. **Formulate your opinion/solution**
3. **Invoke Codex** for second opinion with context about your analysis
4. **Compare perspectives** - note where you agree/disagree
5. **Present to user** - show both perspectives and your synthesis

```bash
# Example workflow for architecture decision
# Step 1 & 2: You've analyzed and formed opinion

# Step 3: Get Codex opinion
codex exec --skip-git-repo-check --output-last-message /tmp/codex-arch.txt \
  "I'm deciding between microservices vs monolith for [project].
  My analysis: [your analysis and recommendation].
  What's your assessment? Any concerns with my approach?"

# Step 4 & 5: Compare and present
cat /tmp/codex-arch.txt
# Then synthesize both views for the user
```

## Important Notes

- **Codex uses OpenAI models** (GPT-5.3-Codex, GPT-5.2-Codex), not Anthropic Claude. o4-mini does NOT work with ChatGPT accounts.
- **Read-only by default** - exec mode is safe, won't modify files
- **Non-interactive** - exec mode is scriptable and doesn't interrupt
- **Complementary tool** - Use for validation, not as replacement for your analysis
- **Context matters** - Codex sees the project files in working directory

## Quick Reference

```bash
# Simple question
codex exec --skip-git-repo-check --output-last-message /tmp/out.txt "question"
cat /tmp/out.txt

# With JSON schema
codex exec --skip-git-repo-check --output-schema /tmp/schema.json \
  --output-last-message /tmp/result.json "question"
cat /tmp/result.json

# Latest model
codex exec --skip-git-repo-check -m gpt-5.3-codex --output-last-message /tmp/out.txt "complex question"
cat /tmp/out.txt

# Different directory
codex exec --skip-git-repo-check -C /path/to/project --output-last-message /tmp/out.txt "analyze"
cat /tmp/out.txt
```

## Advanced: Streaming JSON Events

For real-time monitoring (rarely needed in this skill):

```bash
# Extract final message from JSON stream
codex exec --skip-git-repo-check --json "question" 2>/dev/null | \
  jq -r 'select(.item.type=="agent_message") | .item.text' | tail -1
```

---

**Remember:** This skill is for getting second opinions, not for doing the work. Always form your own analysis first, then use Codex to validate, challenge, or enhance it.
