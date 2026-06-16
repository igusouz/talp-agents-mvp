Few-shot examples for QA analysis.

Global guidance:
- Every output item must include literal evidence from the story.
- If information is missing, prefer ambiguity + refinement question over inferred requirements.
- Keep compatibility fields populated (plain string lists) and mirror them in *_trace fields.

Example 1
Input:
Story: As a user, I want to reset my password so I can recover access to my account.
Acceptance criteria:
- The user must receive a reset email
- The reset link expires in 30 minutes
- The new password must contain at least one number

Output:
{
  "summary": "The story supports a password reset flow with email delivery, link expiration, and password complexity validation. The main gaps are around account lookup behavior, token invalidation, and error handling.",
  "ac_map": [
    "AC1: The user must receive a reset email",
    "AC2: The reset link expires in 30 minutes",
    "AC3: The new password must contain at least one number"
  ],
  "bdd_scenarios": [
    {
      "id": "SC1",
      "title": "Successful password reset email is sent",
      "scenario_type": "positive",
      "ac_ids": ["AC1"],
      "given": ["the user has a registered account"],
      "when": ["the user submits a valid email address"],
      "then": ["a password reset email is sent to the user"],
      "notes": ["Email should arrive within 5 minutes."],
      "evidence_us": "The user must receive a reset email",
      "origin": "explicit_in_story"
    }
  ],
  "negative_cases": ["Submit an unregistered email address and verify the system response.", "Use an expired reset link."],
  "negative_cases_trace": [
    {
      "text": "Use an expired reset link.",
      "evidence_us": "The reset link expires in 30 minutes",
      "origin": "explicit_in_story",
      "ac_ids": ["AC2"],
      "scenario_id": "SC1"
    }
  ],
  "edge_cases": ["Request multiple reset emails in a short period.", "Attempt reset from a partially verified account."],
  "edge_cases_trace": [
    {
      "text": "Request multiple reset emails in a short period.",
      "evidence_us": "The user must receive a reset email",
      "origin": "direct_inference",
      "ac_ids": ["AC1"],
      "scenario_id": "SC1"
    }
  ],
  "ambiguities": ["The story does not specify whether unregistered emails should return the same response as registered ones."],
  "ambiguities_trace": [
    {
      "text": "The story does not specify whether unregistered emails should return the same response as registered ones.",
      "evidence_us": "As a user, I want to reset my password",
      "origin": "direct_inference",
      "ambiguity_id": "AMB1"
    }
  ],
  "risks": ["Password reset is a high-security flow and should prevent token reuse."],
  "risks_trace": [
    {
      "text": "Password reset is a high-security flow and should prevent token reuse.",
      "evidence_us": "reset my password",
      "origin": "direct_inference",
      "ac_ids": ["AC1", "AC2"]
    }
  ],
  "automation_suggestions": ["Automate the email request API and the token validation path.", "Add an integration test for link expiration."],
  "automation_suggestions_trace": [
    {
      "text": "Add an integration test for link expiration.",
      "evidence_us": "The reset link expires in 30 minutes",
      "origin": "explicit_in_story",
      "ac_ids": ["AC2"],
      "scenario_id": "SC1"
    }
  ],
  "questions_for_refinement": ["Should unregistered emails receive the same response message as registered emails?"],
  "questions_for_refinement_trace": [
    {
      "text": "Should unregistered emails receive the same response message as registered emails?",
      "evidence_us": "As a user, I want to reset my password",
      "origin": "direct_inference",
      "ambiguity_id": "AMB1"
    }
  ],
  "blocked_hypotheses": []
}

Example 2
Input:
Story: As a shopper, I want to apply a promo code so I can get a discount.

Output guidance:
- Do not assume discount stacking rules unless they are provided.
- Capture missing validation rules as ambiguities.
- Include invalid code, expired code, and already-used code as negative cases.
- Provide evidence_us for each generated item.
