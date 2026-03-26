# Legal Document Templates — Index

> ⚠️ These templates are starting points only. Always recommend clients have a licensed attorney review before use.

## Available Templates

| Template | Slug | Use Case |
|----------|------|----------|
| Client Service Agreement | `legal-service-agreement` | Service businesses |
| Independent Contractor Agreement | `legal-contractor-agreement` | Hiring freelancers/1099s |
| Non-Disclosure Agreement | `legal-nda` | Protecting business info |
| Privacy Policy | `legal-privacy-policy` | Websites collecting user data |
| Terms of Service | `legal-tos` | SaaS / website terms |
| Employee Offer Letter | `legal-offer-letter` | Hiring W2 employees |
| Refund Policy | `legal-refund-policy` | E-commerce / service businesses |

## Auto-Fill Variables
All templates use `{{variables}}` filled from `foundation.client_profiles`:
- `{{business_name}}`, `{{business_type}}`, `{{state}}`, `{{owner_name}}`
- `{{services}}`, `{{payment_terms}}`, `{{cancellation_policy}}`

## Generation Flow
1. Onboarding Orchestrator identifies which docs are needed (based on tier + industry)
2. Legal Docs Agent fills variables from client profile
3. Output is a formatted markdown document
4. Content Production Agent converts to PDF for client delivery
