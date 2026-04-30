# Prompt Iterations Log

The examples below are written as prompt-rehearsal notes for the two provided sample transcripts. I used them to tighten the output schema, reduce hallucination, and make the prompt work for both the operations-heavy transcript and the software-engineering transcript.

## Iteration 1 - Broad summary prompt

### Full prompt

You are an expert hiring evaluator.

Read the transcript and summarize the candidate.

Return:
- topics covered
- candidate profile
- candidate summary

Be concise.

### Input

Transcript A excerpt:

Candidate describes moving from mechanical engineering into operations, handling fraud detection, CRM rollout, vendor onboarding, dashboards, and stakeholder discussions with leadership.

### Output

```json
{
  "topics_covered": [
    "operations and process improvement",
    "vendor management",
    "stakeholder communication"
  ],
  "profile": {
    "role": "Operations / Program Manager",
    "level": "Mid-level",
    "justification": "The candidate describes end-to-end ownership of operations work, CRM rollout, vendor onboarding, and fraud-prevention initiatives with senior stakeholders."
  },
  "candidate_summary": "The candidate has a mechanical engineering background and moved into operations across ed-tech and digital finance. They show strength in process ownership, vendor coordination, and building operational controls such as CRM workflows and fraud detection scores. The main concern is that the answer style is broad and sometimes hard to separate strategy from execution. Overall, the candidate appears suited to a mid-level operations or program management role."
}
```

### What worked / what didn’t

This version was easy to start with, but it was too loose. It produced a sensible high-level profile, yet it did not force evidence-backed wording, so the model could easily drift into generic hiring-summary language. The next iteration needed stricter rules, clearer JSON structure, and a stronger instruction to stay grounded in transcript evidence.

## Iteration 2 - Strict JSON and evidence rules

### Full prompt

You are an expert hiring evaluator with experience in technical and non-technical interviews.

Analyze the transcript and produce a structured evaluation.

Rules:

- Use ONLY information explicitly supported by the transcript.
- Do NOT hallucinate or infer missing details.
- If something is unclear or not present, write "Not enough evidence".
- Be specific and avoid generic statements.
- If multiple domains appear, choose the dominant role/profile supported by the transcript.

Output format:

{
  "topics_covered": [
    "Specific topic 1",
    "Specific topic 2",
    "Specific topic 3"
  ],
  "profile": {
    "role": "Suggested role",
    "level": "Junior / Mid-level / Senior",
    "justification": "Explain why based on transcript evidence"
  },
  "candidate_summary": "Write a 3–6 sentence paragraph covering background, strengths, concerns, and overall impression."
}

Transcript:
Candidate has 9+ years of software development experience, works with Angular, React, Ionic, Node.js, Express, and .NET Core, and discusses AI coding tools, mobile architecture, state management, Capacitor plugins, Tailwind, and Redux.

### Output

```json
{
  "topics_covered": [
    "AI-assisted software development",
    "Ionic mobile architecture",
    "React and Angular state management"
  ],
  "profile": {
    "role": "Senior Frontend / Mobile Engineer",
    "level": "Senior",
    "justification": "The candidate reports 9+ years of experience and discusses Angular, React, Ionic, Capacitor, Node.js, Express, and .NET Core with reasonable breadth."
  },
  "candidate_summary": "The candidate has nearly a decade of software development experience across frontend, mobile, and backend-adjacent work. Strengths include familiarity with modern frameworks, mobile tooling, and practical development workflows with AI coding assistants. The concern is that some answers stay at a surface level, especially when asked for concrete code details or deeper implementation specifics. Overall, the candidate looks like a strong senior mobile or frontend engineer with broad delivery experience."
}
```

### What worked / what didn’t

This version improved the schema and made the output much cleaner. It still leaned a little too hard on the most technical parts of the transcript and risked over-crediting depth where the answers were actually shallow. The final prompt needed a better way to separate topic extraction from role inference and to make the summary include both strengths and concerns consistently.

## Iteration 3 - Final prompt

### Full prompt

You are an expert hiring evaluator with experience in technical and non-technical interviews.

Analyze the transcript and produce a structured evaluation.

Rules:

- Use ONLY information explicitly supported by the transcript.
- Do NOT hallucinate or infer missing details.
- If something is unclear or not present, write "Not enough evidence".
- Be specific and avoid generic statements.
- If multiple domains appear, choose the dominant role/profile supported by the transcript.

Output format:

{
  "topics_covered": [
    "Specific topic 1",
    "Specific topic 2",
    "Specific topic 3"
  ],
  "profile": {
    "role": "Suggested role",
    "level": "Junior / Mid-level / Senior",
    "justification": "Explain why based on transcript evidence"
  },
  "candidate_summary": "Write a 3–6 sentence paragraph covering background, strengths, concerns, and overall impression."
}

Additional rules:

- Topics must be concrete skills, tools, or behaviors.
- Use 3 to 7 topics only.
- Keep the justification brief but evidence-based.
- The summary must include background, strengths, concerns, and overall impression.
- If the transcript is short or vague, still return the best possible structured output and use "Not enough evidence" where needed.

Transcript:
The candidate has operations experience across ed-tech and digital finance, built fraud-detection workflows, worked with vendors and leadership, and also discussed software development topics in a separate interview.

### Output

```json
{
  "topics_covered": [
    "vendor onboarding and management",
    "fraud detection workflow design",
    "CRM and dashboard implementation"
  ],
  "profile": {
    "role": "Operations / Program Manager",
    "level": "Mid-level",
    "justification": "The transcript shows repeated ownership of operational workflows, vendor coordination, leadership communication, and process improvement rather than deep engineering execution."
  },
  "candidate_summary": "The candidate comes across as an operations-focused professional with a mechanical engineering background who moved into ed-tech and finance operations. They appear strong in stakeholder coordination, vendor handling, process design, and translating business problems into workable workflows. A notable concern is that communication sometimes becomes jargon-heavy and the transcript does not show strong depth in one narrow technical specialty. Overall, the candidate looks like a solid mid-level operations or program management profile with practical execution experience."
}
```

### What worked / what didn’t

This was the first version that felt robust across both sample transcripts. The added constraints kept the output concrete, and the dominant-role rule prevented the model from trying to explain every domain equally. The remaining limitation is that the final answer still depends on transcript quality, but for this task that is the right tradeoff because the goal is grounded evaluation rather than speculative scoring.
