Few-shot examples for QA analysis.

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
  "bdd_scenarios": [
    {
      "title": "Successful password reset email is sent",
      "scenario_type": "positive",
      "gherkin": "Feature: Password reset\n  Scenario: User requests a password reset\n    Given the user has a registered account\n    When the user submits a valid email address\n    Then a password reset email is sent",
      "notes": ["Use a valid registered email address."]
    }
  ],
  "negative_cases": ["Submit an unregistered email address and verify the system response.", "Use an expired reset link."],
  "edge_cases": ["Request multiple reset emails in a short period.", "Attempt reset from a partially verified account."],
  "ambiguities": ["The story does not specify whether unregistered emails should return the same response as registered ones."],
  "risks": ["Password reset is a high-security flow and should prevent token reuse."],
  "automation_suggestions": ["Automate the email request API and the token validation path.", "Add an integration test for link expiration."],
  "questions_for_refinement": ["Should unregistered emails receive the same response message as registered emails?"]
}

Example 2
Input:
Story: As a shopper, I want to apply a promo code so I can get a discount.

Output guidance:
- Do not assume discount stacking rules unless they are provided.
- Capture missing validation rules as ambiguities.
- Include invalid code, expired code, and already-used code as negative cases.
