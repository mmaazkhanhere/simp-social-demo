# Project Overview
Build an AI-powered conversational model designed for a Buy Here Pay Here (BHPH) dealership environment.

## Key Difference From Traditional Models
This is **not** appointment-driven.

## Primary Objective
- Guide the customer toward completing a credit application.
- Collect key qualification details.
- Trigger a dealership notification once the lead is ready or submits.

## Core Objectives
Your model should:
- Engage inbound leads (SMS-style conversation).
- Understand intent and respond naturally (human-like tone).
- Progressively guide toward credit application completion.
- Handle objections (credit concerns, hesitation, confusion).
- Collect structured data points during conversation.
- Trigger an event when the lead is "application-ready" or submitted.

## Conversation Goals (Priority Order)
- Build trust (BHPH customers are often skeptical).
- Identify financing intent.
- Collect qualification info:
  - Employment status.
  - Monthly income range.
  - Down payment ability.
  - Timeline to purchase.
- Move the customer to:
  - Apply online, or
  - Complete the application via conversation (simulated).

## Key Requirements
### 1. Conversation Engine
Simulate an SMS-style assistant (like "Sarah AI").

Responses must:
- Be concise.
- Mirror customer tone.
- Avoid robotic phrasing.
- Never push aggressively.

### 2. Dynamic Flow (No Scripts)
Do **not** build a rigid decision tree.

Use LLM reasoning to:
- Adapt questions based on answers.
- Skip irrelevant steps.
- Personalize responses.

### 3. Objection Handling
Your model must intelligently respond to:
- "I'm just looking"
- "My credit is bad"
- "I don't want my credit pulled"
- "How much down?"
- "I'm busy"

Focus on:
- Reducing friction.
- Reassuring approval likelihood.
- Keeping momentum toward the application.

### 4. Data Capture Layer
Extract and structure the following from conversation:

```json
{
  "name": "",
  "phone": "",
  "employment_status": "",
  "monthly_income_range": "",
  "down_payment_range": "",
  "timeline": "",
  "intent_score": ""
}
```

### 5. Lead Scoring Logic
Create a simple scoring model:
- Hot: ready to apply.
- Warm: interested but hesitant.
- Cold: low intent.

Explain your logic.

### 6. Trigger Event
Define and implement when the system notifies the dealership. Examples:
- Application completed.
- Strong intent detected.
- High qualification signals.

Include:
- Payload structure.
- Example webhook or API trigger.

### 7. Memory Handling
- Maintain conversation context.
- Avoid repeating questions.
- Handle corrections (for example: "actually I make more...").

## Evaluation Criteria
We will evaluate based on:
- Conversation quality (feels human vs robotic).
- Ability to drive toward application (not just chat).
- Smart handling of edge cases.
- Clean architecture and reasoning.
- Practicality for real dealership deployment.

## Time Expectation
We expect this to take 6-10 hours max. Focus on quality over completeness.

## Bonus (Optional)
- Multi-language support (Spanish).
- Tone variation based on customer sentiment.
- Integration concept with CRM/DMS.

## Final Note
We are not looking for perfection. We are looking for:
- How you think.
- How you structure real-world AI systems.
- How well you understand business outcomes.
