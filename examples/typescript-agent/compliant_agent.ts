/**
 * Compliant AI Agent Loop — The Power of 15
 * ==========================================
 * Insurance policy lookup agent with bounded execution,
 * error handling, and security boundaries.
 *
 * Author: Pramod Misra
 * Rules Reference: https://github.com/pramodmisra/power-of-15
 */

import Anthropic from "@anthropic-ai/sdk";

// Rule 6: Config in a typed object, not scattered constants
interface AgentConfig {
  readonly maxSteps: number;
  readonly model: string;
  readonly allowedTables: ReadonlySet<string>;
  readonly maxTokens: number;
}

const AGENT_CONFIG: AgentConfig = {
  maxSteps: 15,
  model: "claude-sonnet-4-20250514",
  allowedTables: new Set(["policies", "claims", "producers", "carriers"]),
  maxTokens: 1024,
} as const;

// Rule 9: Flat, typed interfaces — no deep nesting
interface ToolAction {
  type: "tool_call" | "final_answer";
  toolName?: string;
  toolInput?: Record<string, unknown>;
  result?: string;
}

interface AgentState {
  messages: Array<{ role: string; content: string }>;
  stepCount: number;
  lastError: string | null;
}

// Rule 14: Security boundary — validate tool inputs
function validateTableAccess(table: string, allowed: ReadonlySet<string>): void {
  // Rule 5: Input validation
  if (typeof table !== "string" || table.length === 0) {
    throw new Error("Table name must be a non-empty string");
  }
  if (!allowed.has(table)) {
    throw new Error(
      `Access denied: table '${table}' not in allowed set: [${[...allowed].join(", ")}]`
    );
  }
  // Rule 14: Prevent SQL injection patterns
  const dangerousPatterns = /[;'"\\]|--|\bDROP\b|\bDELETE\b|\bUPDATE\b/i;
  if (dangerousPatterns.test(table)) {
    throw new Error(`Suspicious input rejected: '${table}'`);
  }
}

// Rule 7: Structured error handling for API calls with retry
async function callWithRetry<T>(
  fn: () => Promise<T>,
  maxRetries: number = 3
): Promise<T> {
  // Rule 5: Validate
  if (maxRetries < 1 || maxRetries > 10) {
    throw new RangeError(`maxRetries must be 1-10, got: ${maxRetries}`);
  }

  // Rule 2: Bounded retry loop
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error: unknown) {
      // Rule 7: Handle specific errors, not generic catch
      if (error instanceof Anthropic.RateLimitError) {
        const waitMs = Math.min(1000 * Math.pow(2, attempt), 30000);
        console.warn(`Rate limited, waiting ${waitMs}ms (attempt ${attempt + 1}/${maxRetries})`);
        await new Promise((resolve) => setTimeout(resolve, waitMs));
        continue;
      }
      if (error instanceof Anthropic.APIError && attempt < maxRetries - 1) {
        console.warn(`API error (attempt ${attempt + 1}): ${error.message}`);
        continue;
      }
      throw error; // Rule 7: Don't swallow — re-throw unhandled errors
    }
  }
  throw new Error(`Failed after ${maxRetries} retries`);
}

// Simulated tool execution with validation
async function executeTool(action: ToolAction): Promise<string> {
  // Rule 5: Validate action structure
  if (!action.toolName) {
    throw new Error("Tool action missing toolName");
  }

  if (action.toolName === "query_policies") {
    const table = (action.toolInput?.table as string) ?? "";
    validateTableAccess(table, AGENT_CONFIG.allowedTables); // Rule 14
    return `Found 3 active policies in '${table}' for the requested criteria.`;
  }

  if (action.toolName === "get_claim_status") {
    const claimId = action.toolInput?.claim_id as string;
    // Rule 14: Mask PII in logs
    const maskedId = claimId ? `${claimId.slice(0, 4)}****` : "unknown";
    console.log(`Looking up claim: ${maskedId}`);
    return `Claim ${maskedId} status: Under Review. Estimated resolution: 5 business days.`;
  }

  throw new Error(`Unknown tool: ${action.toolName}`);
}

/**
 * Main agent loop — bounded by maxSteps (Rule 2)
 */
async function runAgent(userQuery: string): Promise<string> {
  // Rule 5: Input validation
  if (typeof userQuery !== "string" || userQuery.trim().length === 0) {
    throw new Error("Query must be a non-empty string");
  }

  // Rule 14: API key from environment, never hardcoded
  const client = new Anthropic(); // reads ANTHROPIC_API_KEY from env

  const state: AgentState = {
    messages: [{ role: "user", content: userQuery }],
    stepCount: 0,
    lastError: null,
  };

  // Rule 2: Bounded agent loop with explicit max
  for (let step = 0; step < AGENT_CONFIG.maxSteps; step++) {
    state.stepCount = step + 1;
    console.log(`[Step ${state.stepCount}/${AGENT_CONFIG.maxSteps}]`);

    // Rule 7: API call with retry and specific error handling
    const response = await callWithRetry(() =>
      client.messages.create({
        model: AGENT_CONFIG.model,
        max_tokens: AGENT_CONFIG.maxTokens,
        messages: state.messages as Array<{ role: "user" | "assistant"; content: string }>,
      })
    );

    // Rule 7: Check response structure
    const content = response.content[0];
    if (!content) {
      throw new Error("Empty response from Claude");
    }

    if (content.type === "text") {
      // Final answer — exit the loop
      const answer = content.text;
      // Rule 5: Validate output is non-empty
      if (answer.trim().length === 0) {
        state.lastError = "Empty answer received";
        continue;
      }
      console.log(`Agent completed in ${state.stepCount} steps`);
      return answer;
    }

    // If we reach here without a final answer, continue reasoning
    state.messages.push({ role: "assistant", content: JSON.stringify(content) });
  }

  // Rule 2: Explicit failure when bound is hit
  throw new Error(
    `Agent exhausted maximum steps (${AGENT_CONFIG.maxSteps}) without producing a final answer. ` +
    `Last error: ${state.lastError ?? "none"}`
  );
}

// Entry point
async function main(): Promise<void> {
  try {
    const answer = await runAgent("What is the status of claim CLM-2025-48291?");
    console.log("Answer:", answer);
  } catch (error: unknown) {
    // Rule 7: Specific error handling at the top level
    if (error instanceof Error) {
      console.error(`Agent failed: ${error.message}`);
    } else {
      console.error("Agent failed with unknown error");
    }
    process.exit(1);
  }
}

main();
