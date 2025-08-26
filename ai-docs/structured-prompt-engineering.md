# Structured Prompt Engineering Framework

A systematic approach to building high-quality prompts using composable components for consistent, predictable AI interactions.

## The Core Framework

```typescript
const createPrompt = (opts: {
  // The context of the task
  taskContext: string;
  // Any advice about output tone
  toneContext?: string;
  // Background data, documents, etc.
  backgroundData?: string;
  // Detailed task instructions & rules
  detailedTaskInstructions?: string;
  // Exemplars of good/bad output
  examples?: string;
  // Conversation history between the user and the assistant
  conversationHistory?: string;
  // The "ask" for the LLM: "Create an annotated version
  // of the transcript..."
  finalRequest: string;
  // "Think about your answer first", if needed
  chainOfThought?: string;
  // "Reply in <response></response> tags"
  outputFormatting?: string;
}) => {
  return [
    opts.taskContext,
    opts.toneContext,
    opts.backgroundData,
    opts.detailedTaskInstructions,
    opts.examples,
    opts.conversationHistory,
    opts.finalRequest,
    opts.chainOfThought,
    opts.outputFormatting,
  ]
    .filter(Boolean)
    .join("\n\n");
};
```

## Component Breakdown

### 1. Task Context
**Purpose**: Set the role and domain expertise
**Effect**: Primes the model's knowledge and perspective

```typescript
// Examples:
"You are a senior software architect with 15 years of experience"
"You are a technical writer specializing in API documentation"
"You are a security engineer focused on application vulnerabilities"
```

### 2. Tone Context
**Purpose**: Control voice, formality, and audience alignment
**Effect**: Ensures appropriate communication style

```typescript
// Examples:
"Write in a technical but accessible tone for developers"
"Use formal business language for executive stakeholders"
"Explain complex concepts simply for non-technical users"
```

### 3. Background Data
**Purpose**: Provide domain-specific knowledge and context
**Effect**: Grounds responses in facts, reduces hallucination

```typescript
// Examples:
`Current system: Node.js, PostgreSQL, 10M req/day, 8 engineers`
`Company: B2B SaaS, $50M ARR, SOC2 compliant, GDPR required`
`Codebase: React/TypeScript, 500K LOC, microservices architecture`
```

### 4. Detailed Task Instructions
**Purpose**: Eliminate ambiguity and define quality criteria
**Effect**: Creates consistent, structured outputs

```typescript
// Examples:
`- Focus on scalability and maintainability
- Identify potential bottlenecks
- Rate recommendations by difficulty (1-5)
- Flag security considerations
- Provide specific implementation steps`
```

### 5. Examples
**Purpose**: Show exactly what good output looks like
**Effect**: Dramatically improves quality through pattern matching

```typescript
// Examples:
`GOOD: "CRITICAL: SQL injection in line 42. Use parameterized queries: db.query('SELECT * FROM users WHERE id = ?', [userId])"
BAD: "Fix the SQL query"`
```

### 6. Output Formatting
**Purpose**: Structure responses for consistency and parsing
**Effect**: Predictable format for downstream processing

```typescript
// Examples:
"Structure as: Risk Assessment, Recommendations, Next Steps"
"Reply in JSON format with keys: analysis, confidence, suggestions"
"Use <analysis></analysis> tags for your reasoning"
```

## Pre-Built Templates

### Code Review Template
```typescript
const codeReviewPrompt = createPrompt({
  taskContext: "You are a senior software engineer conducting a thorough code review",
  toneContext: "Professional and constructive, focus on education",
  detailedTaskInstructions: `
    - Identify bugs, security issues, and performance problems
    - Suggest specific improvements with code examples
    - Rate issues by severity: Critical/High/Medium/Low
    - Explain the reasoning behind each recommendation
  `,
  examples: `
    GOOD: "HIGH: Race condition in user authentication. The token validation happens after database write. Move validation before write operation."
    BAD: "Fix the auth issue"
  `,
  outputFormatting: "Group by: Security Issues, Performance Issues, Code Quality, Suggestions"
});
```

### Technical Documentation Template
```typescript
const technicalDocsPrompt = createPrompt({
  taskContext: "You are a technical writer specializing in developer documentation",
  toneContext: "Clear, concise, and developer-friendly with practical examples",
  detailedTaskInstructions: `
    - Start with clear overview and purpose
    - Include code examples for all concepts
    - Explain parameters, return values, and error cases
    - Add troubleshooting section for common issues
    - Link to related documentation where relevant
  `,
  examples: `
    GOOD: "## Authentication\nUse API keys in the Authorization header:\n\`\`\`bash\ncurl -H 'Authorization: Bearer your-api-key' https://api.example.com/users\n\`\`\`"
    BAD: "Use the API key for authentication"
  `,
  outputFormatting: "Structure as: Overview, Quick Start, Reference, Examples, Troubleshooting"
});
```

### System Analysis Template
```typescript
const systemAnalysisPrompt = createPrompt({
  taskContext: "You are a systems architect analyzing complex technical problems",
  toneContext: "Analytical and thorough, balance technical depth with clarity",
  detailedTaskInstructions: `
    - Break down the problem into components
    - Identify root causes vs symptoms
    - Propose multiple solution approaches
    - Analyze trade-offs for each approach
    - Estimate implementation complexity and timeline
  `,
  examples: `
    GOOD: "Root cause: Database connection pooling exhausted under load. Solutions: 1) Increase pool size (Quick, medium risk) 2) Implement connection multiplexing (Complex, low risk) 3) Add read replicas (Medium complexity, scales well)"
    BAD: "The database is slow, add more resources"
  `,
  outputFormatting: "Structure as: Problem Analysis, Root Causes, Solution Options, Recommendation, Implementation Plan"
});
```

## Advanced Patterns

### Dynamic Context Loading
```typescript
const createContextAwarePrompt = async (task: string, projectPath: string) => {
  const projectMeta = await getProjectMetadata(projectPath);
  const relevantFiles = await searchRelevantContext(task, projectPath);
  
  return createPrompt({
    taskContext: `You are working on ${projectMeta.name} (${projectMeta.techStack})`,
    backgroundData: `
      Project: ${projectMeta.description}
      Tech Stack: ${projectMeta.techStack}
      Team Size: ${projectMeta.teamSize}
      
      Relevant Code:
      ${relevantFiles.join('\n')}
    `,
    finalRequest: task
  });
};
```

### Multi-Agent Specialization
```typescript
const createSpecializedAgent = (role: 'security' | 'performance' | 'architecture') => {
  const configs = {
    security: {
      taskContext: "You are a cybersecurity expert specializing in application security",
      detailedTaskInstructions: `
        - Identify OWASP Top 10 vulnerabilities
        - Check for input validation issues
        - Verify authentication and authorization
        - Flag sensitive data exposure
      `,
      examples: securityExamples
    },
    performance: {
      taskContext: "You are a performance engineer optimizing web applications",
      detailedTaskInstructions: `
        - Identify performance bottlenecks
        - Suggest caching strategies
        - Analyze database query efficiency
        - Check for memory leaks
      `,
      examples: performanceExamples
    },
    architecture: {
      taskContext: "You are a solutions architect designing scalable systems",
      detailedTaskInstructions: `
        - Evaluate system design patterns
        - Assess scalability and maintainability
        - Identify single points of failure
        - Suggest architectural improvements
      `,
      examples: architectureExamples
    }
  };
  
  return (request: string, context: string) => 
    createPrompt({
      ...configs[role],
      backgroundData: context,
      finalRequest: request
    });
};
```

### Conversation Continuation
```typescript
const createContinuationPrompt = (history: ConversationTurn[], newRequest: string) => {
  return createPrompt({
    taskContext: "Continue the ongoing technical discussion",
    conversationHistory: formatConversationHistory(history),
    detailedTaskInstructions: `
      - Maintain consistency with previous recommendations
      - Build upon previously discussed solutions
      - Reference earlier conversation points when relevant
      - Avoid contradicting previous advice unless explicitly correcting
    `,
    finalRequest: newRequest
  });
};
```

## Quality Control Checklist

Before using any prompt, verify:

- [ ] **Task Context**: Clear role and expertise defined
- [ ] **Background Data**: Relevant facts and constraints included
- [ ] **Instructions**: Specific, actionable, unambiguous
- [ ] **Examples**: Show both good and bad outputs
- [ ] **Format**: Consistent structure for parsing/processing
- [ ] **Scope**: Request is focused and achievable
- [ ] **Validation**: Success criteria clearly defined

## Common Anti-Patterns to Avoid

### ❌ Vague Instructions
```typescript
// BAD
finalRequest: "Make the code better"

// GOOD
finalRequest: "Refactor this function to improve readability and reduce cyclomatic complexity below 10"
```

### ❌ Missing Context
```typescript
// BAD
taskContext: "You are a developer"

// GOOD
taskContext: "You are a senior Python developer working on a Django REST API for a financial services company"
```

### ❌ No Examples
```typescript
// BAD
detailedTaskInstructions: "Write good documentation"

// GOOD
detailedTaskInstructions: "Write API documentation with examples"
examples: `
GOOD: "## POST /users\nCreates a new user account.\n\`\`\`json\n{\"name\": \"John\", \"email\": \"john@example.com\"}\n\`\`\`"
BAD: "Creates user"
`
```

## Implementation Guide

1. **Start Simple**: Begin with `taskContext` and `finalRequest`
2. **Add Context**: Include `backgroundData` for domain knowledge
3. **Define Quality**: Add `detailedTaskInstructions` for consistency
4. **Show Examples**: Include `examples` for pattern matching
5. **Control Output**: Use `outputFormatting` for structure
6. **Iterate**: Refine based on actual outputs and needs

This framework transforms prompt engineering from art to science, enabling consistent, high-quality AI interactions at scale.