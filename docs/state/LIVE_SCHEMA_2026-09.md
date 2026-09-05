# LIVE SCHEMA — 2026-09-05
Captured via `supabase db query --linked` against information_schema/pg_catalog (no Docker, per the ground-truth header). This is the actual live state of project `rhtwtoinmiekttvunlzs`, not a spec's description of it.

## Tables (18)

### `foundation.agents` — RLS ON
| col | type | nullable | default |
|---|---|---|---|
| id | uuid | NO | gen_random_uuid() |
| name | text | NO |  |
| description | text | YES |  |
| system_prompt | text | YES |  |
| tools | ARRAY | YES | '{}'::text[] |
| model | text | YES | 'claude-sonnet-4-6'::text |
| platform | text | YES |  |
| agent_type | text | YES |  |
| embedding | USER-DEFINED | YES |  |
| config | jsonb | YES | '{}'::jsonb |
| metadata | jsonb | YES | '{}'::jsonb |
| is_active | boolean | YES | true |
| created_at | timestamp with time zone | YES | now() |
| updated_at | timestamp with time zone | YES | now() |

Policies: `Allow public read on agents` (SELECT, roles=['public']); `Allow service role write on agents` (ALL, roles=['public'])

### `foundation.ai_employees` — RLS ON
| col | type | nullable | default |
|---|---|---|---|
| id | text | NO |  |
| name | text | NO |  |
| biblical_name | text | YES |  |
| product_name | text | YES |  |
| role | text | NO |  |
| department | text | NO |  |
| department_label | text | NO |  |
| model_tier | text | NO | 'standard'::text |
| tier_access | text | NO | 'All'::text |
| is_csuite | boolean | YES | false |
| is_confidential | boolean | YES | false |
| style | text | YES |  |
| helps | text | YES |  |
| outside_scope | text | YES |  |
| system_prompt | text | YES |  |
| handoff_to | ARRAY | YES | '{}'::text[] |
| covers_for | ARRAY | YES | '{}'::text[] |
| covered_by | ARRAY | YES | '{}'::text[] |
| reports_to | text | YES |  |
| supervises | ARRAY | YES | '{}'::text[] |
| color | text | YES |  |
| bg | text | YES |  |
| config | jsonb | YES | '{}'::jsonb |
| is_active | boolean | YES | true |
| created_at | timestamp with time zone | YES | now() |
| updated_at | timestamp with time zone | YES | now() |
| legacy_slug | text | YES |  |

Policies: `public_read_employees` (SELECT, roles=['public'])

### `foundation.brand_profiles` — RLS ON
| col | type | nullable | default |
|---|---|---|---|
| id | uuid | NO | gen_random_uuid() |
| business_slug | text | NO |  |
| business_name | text | NO |  |
| tagline | text | YES |  |
| tone | text | YES |  |
| colors | jsonb | YES | '{}'::jsonb |
| fonts | jsonb | YES | '{}'::jsonb |
| logo_url | text | YES |  |
| industry | text | YES |  |
| description | text | YES |  |
| guidelines | text | YES |  |
| embedding | USER-DEFINED | YES |  |
| metadata | jsonb | YES | '{}'::jsonb |
| created_at | timestamp with time zone | YES | now() |
| updated_at | timestamp with time zone | YES | now() |

Policies: `Allow public read on brand_profiles` (SELECT, roles=['public']); `Allow service role write on brand_profiles` (ALL, roles=['public'])

### `foundation.client_deployments` — RLS ON
| col | type | nullable | default |
|---|---|---|---|
| id | uuid | NO | gen_random_uuid() |
| profile_id | uuid | YES |  |
| deployment_type | text | NO |  |
| status | text | YES | 'queued'::text |
| config | jsonb | YES | '{}'::jsonb |
| output | jsonb | YES | '{}'::jsonb |
| agent_used | uuid | YES |  |
| skill_used | uuid | YES |  |
| started_at | timestamp with time zone | YES |  |
| completed_at | timestamp with time zone | YES |  |
| error_log | text | YES |  |
| created_at | timestamp with time zone | YES | now() |
| updated_at | timestamp with time zone | YES | now() |

Policies: `service_role_all` (ALL, roles=['public'])

### `foundation.client_profiles` — RLS ON
| col | type | nullable | default |
|---|---|---|---|
| id | uuid | NO | gen_random_uuid() |
| business_name | text | NO |  |
| contact_name | text | YES |  |
| contact_email | text | YES |  |
| contact_phone | text | YES |  |
| industry | text | YES |  |
| website | text | YES |  |
| onboarding_platform | text | YES |  |
| services | ARRAY | YES | '{}'::text[] |
| notes | text | YES |  |
| brand_profile_id | uuid | YES |  |
| embedding | USER-DEFINED | YES |  |
| onboarding_data | jsonb | YES | '{}'::jsonb |
| metadata | jsonb | YES | '{}'::jsonb |
| status | text | YES | 'onboarding'::text |
| created_at | timestamp with time zone | YES | now() |
| updated_at | timestamp with time zone | YES | now() |

Policies: `Allow public read on client_profiles` (SELECT, roles=['public']); `Allow service role write on client_profiles` (ALL, roles=['public'])

### `foundation.eden_sessions` — RLS ON
| col | type | nullable | default |
|---|---|---|---|
| id | uuid | NO | gen_random_uuid() |
| session_token | text | NO |  |
| platform_slug | text | NO |  |
| started_at | timestamp with time zone | YES | now() |
| ended_at | timestamp with time zone | YES |  |
| message_count | integer | YES | 0 |
| escalation_flag | boolean | YES | false |

### `foundation.employee_platform_subscriptions` — RLS ON
| col | type | nullable | default |
|---|---|---|---|
| id | uuid | NO | gen_random_uuid() |
| platform_slug | text | NO |  |
| employee_id | text | NO |  |
| is_active | boolean | YES | true |
| config_override | jsonb | YES | '{}'::jsonb |
| created_at | timestamp with time zone | YES | now() |

Policies: `public_read_subscriptions` (SELECT, roles=['public'])

### `foundation.employee_sync_log` — RLS ON
| col | type | nullable | default |
|---|---|---|---|
| id | uuid | NO | gen_random_uuid() |
| platform_slug | text | NO |  |
| synced_at | timestamp with time zone | YES | now() |
| employee_count | integer | YES |  |
| sync_status | text | YES | 'success'::text |
| notes | text | YES |  |

### `foundation.llm_usage` — RLS ON
| col | type | nullable | default |
|---|---|---|---|
| id | uuid | NO | gen_random_uuid() |
| project | text | NO |  |
| agent_name | text | YES |  |
| model | text | NO |  |
| tier | text | NO |  |
| input_tokens | integer | NO | 0 |
| output_tokens | integer | NO | 0 |
| cache_read_input_tokens | integer | NO | 0 |
| cache_creation_input_tokens | integer | NO | 0 |
| estimated_cost_usd | numeric | NO | 0 |
| task_type | text | YES |  |
| fallback_from | text | YES |  |
| created_at | timestamp with time zone | YES | now() |

Policies: `service_role_all_llm_usage` (ALL, roles=['public'])

### `foundation.skills` — RLS ON
| col | type | nullable | default |
|---|---|---|---|
| id | uuid | NO | gen_random_uuid() |
| name | text | NO |  |
| description | text | YES |  |
| prompt | text | YES |  |
| category | text | YES |  |
| tags | ARRAY | YES | '{}'::text[] |
| version | integer | YES | 1 |
| embedding | USER-DEFINED | YES |  |
| metadata | jsonb | YES | '{}'::jsonb |
| created_at | timestamp with time zone | YES | now() |
| updated_at | timestamp with time zone | YES | now() |

Policies: `Allow public read on skills` (SELECT, roles=['public']); `Allow service role write on skills` (ALL, roles=['public'])

### `foundation.templates` — RLS ON
| col | type | nullable | default |
|---|---|---|---|
| id | uuid | NO | gen_random_uuid() |
| name | text | NO |  |
| description | text | YES |  |
| template_type | text | NO |  |
| industry | text | YES |  |
| content | text | YES |  |
| file_url | text | YES |  |
| tags | ARRAY | YES | '{}'::text[] |
| embedding | USER-DEFINED | YES |  |
| metadata | jsonb | YES | '{}'::jsonb |
| created_at | timestamp with time zone | YES | now() |
| updated_at | timestamp with time zone | YES | now() |

Policies: `Allow public read on templates` (SELECT, roles=['public']); `Allow service role write on templates` (ALL, roles=['public'])

### `public.industries` — RLS ON
| col | type | nullable | default |
|---|---|---|---|
| id | uuid | NO | gen_random_uuid() |
| slug | text | NO |  |
| display_name | text | NO |  |
| category | text | YES |  |
| icon | text | YES |  |
| sort_order | integer | YES | 0 |

### `public.industry_playbooks` — RLS ON
| col | type | nullable | default |
|---|---|---|---|
| id | uuid | NO | gen_random_uuid() |
| agent_slug | text | NO |  |
| industry_slug | text | NO |  |
| version | integer | YES | 1 |
| playbook | jsonb | NO |  |
| role_override | text | YES |  |
| is_active | boolean | YES | true |
| created_at | timestamp with time zone | YES | now() |

### `public.llm_usage` — RLS OFF
| col | type | nullable | default |
|---|---|---|---|
| id | uuid | NO | gen_random_uuid() |
| created_at | timestamp with time zone | YES | now() |
| project | text | NO |  |
| agent_name | text | YES |  |
| model | text | NO |  |
| tier | text | NO |  |
| input_tokens | integer | YES |  |
| output_tokens | integer | YES |  |
| estimated_cost_usd | numeric | YES |  |
| task_type | text | YES |  |
| session_id | text | YES |  |

### `public.pricing_config` — RLS ON
| col | type | nullable | default |
|---|---|---|---|
| id | uuid | NO | gen_random_uuid() |
| product | text | NO |  |
| variable | text | NO |  |
| value_key | text | NO |  |
| multiplier | numeric | NO |  |
| label | text | YES |  |
| display_order | integer | YES | 0 |
| active | boolean | YES | true |
| updated_at | timestamp with time zone | YES | now() |

Policies: `anon_read_config` (SELECT, roles=['anon']); `authenticated_read_config` (SELECT, roles=['authenticated']); `service_role_all_config` (ALL, roles=['service_role'])

### `public.pricing_outcomes` — RLS ON
| col | type | nullable | default |
|---|---|---|---|
| id | uuid | NO | gen_random_uuid() |
| quote_id | uuid | YES |  |
| closed | boolean | YES |  |
| closed_at | timestamp with time zone | YES |  |
| final_monthly_price | numeric | YES |  |
| negotiation_delta_pct | numeric | YES |  |
| churn_month | integer | YES |  |
| churn_reason | text | YES |  |
| ltv | numeric | YES |  |
| upsell_product | text | YES |  |
| upsell_monthly | numeric | YES |  |
| notes | text | YES |  |
| updated_at | timestamp with time zone | YES | now() |

Policies: `service_role_all_outcomes` (ALL, roles=['service_role'])

### `public.pricing_quotes` — RLS ON
| col | type | nullable | default |
|---|---|---|---|
| id | uuid | NO | gen_random_uuid() |
| contact_id | uuid | YES |  |
| product | text | NO |  |
| inputs | jsonb | NO |  |
| multipliers | jsonb | NO |  |
| base_fee | numeric | NO |  |
| monthly_price | numeric | NO |  |
| setup_fee | numeric | NO |  |
| estimated_roi | numeric | YES |  |
| roi_model | text | YES |  |
| roi_multiple | numeric | YES |  |
| tier | text | YES |  |
| price_capped | boolean | YES | false |
| bundle_products | ARRAY | YES |  |
| bundle_discount_pct | numeric | YES |  |
| source | text | NO | 'customer_calc'::text |
| status | text | NO | 'draft'::text |
| negotiation_notes | text | YES |  |
| override_multipliers | jsonb | YES |  |
| created_at | timestamp with time zone | YES | now() |
| updated_at | timestamp with time zone | YES | now() |
| expires_at | timestamp with time zone | YES | (now() + '30 days'::interval) |

Policies: `service_role_all_quotes` (ALL, roles=['service_role'])

### `public.transfer_logs` — RLS ON
| col | type | nullable | default |
|---|---|---|---|
| id | uuid | NO | gen_random_uuid() |
| business_id | text | NO |  |
| call_sid | text | NO |  |
| from_number | text | NO | ''::text |
| to_extension | text | NO |  |
| destination_number | text | NO |  |
| transfer_type | text | NO | 'cold'::text |
| status | text | NO |  |
| duration_seconds | integer | YES |  |
| fallback_used | boolean | NO | false |
| error_message | text | YES |  |
| created_at | timestamp with time zone | NO | now() |
| completed_at | timestamp with time zone | YES |  |

Policies: `Service role bypass transfer_logs` (ALL, roles=['public'])

## Functions (126)

- `foundation.search_agents(query_embedding vector, match_threshold double precision, match_count integer, filter_type text, filter_platform text)`
- `foundation.search_skills(query_embedding vector, match_threshold double precision, match_count integer, filter_category text)`
- `foundation.search_templates(query_embedding vector, match_threshold double precision, match_count integer, filter_type text, filter_industry text)`
- `foundation.set_updated_at()`
- `foundation.update_updated_at()`
- `public.array_to_halfvec(real[], integer, boolean)`
- `public.array_to_halfvec(numeric[], integer, boolean)`
- `public.array_to_halfvec(integer[], integer, boolean)`
- `public.array_to_halfvec(double precision[], integer, boolean)`
- `public.array_to_sparsevec(real[], integer, boolean)`
- `public.array_to_sparsevec(numeric[], integer, boolean)`
- `public.array_to_sparsevec(double precision[], integer, boolean)`
- `public.array_to_sparsevec(integer[], integer, boolean)`
- `public.array_to_vector(double precision[], integer, boolean)`
- `public.array_to_vector(numeric[], integer, boolean)`
- `public.array_to_vector(integer[], integer, boolean)`
- `public.array_to_vector(real[], integer, boolean)`
- `public.avg(vector)`
- `public.avg(halfvec)`
- `public.binary_quantize(vector)`
- `public.binary_quantize(halfvec)`
- `public.calculate_blast_video_price(p_market numeric, p_structure numeric, p_revenue numeric, p_videos integer, p_complexity numeric, p_locations integer)`
- `public.calculate_blast_video_roi(p_videos integer, p_complexity numeric, p_vertical numeric)`
- `public.cosine_distance(vector, vector)`
- `public.cosine_distance(halfvec, halfvec)`
- `public.cosine_distance(sparsevec, sparsevec)`
- `public.halfvec(halfvec, integer, boolean)`
- `public.halfvec_accum(double precision[], halfvec)`
- `public.halfvec_add(halfvec, halfvec)`
- `public.halfvec_avg(double precision[])`
- `public.halfvec_cmp(halfvec, halfvec)`
- `public.halfvec_combine(double precision[], double precision[])`
- `public.halfvec_concat(halfvec, halfvec)`
- `public.halfvec_eq(halfvec, halfvec)`
- `public.halfvec_ge(halfvec, halfvec)`
- `public.halfvec_gt(halfvec, halfvec)`
- `public.halfvec_in(cstring, oid, integer)`
- `public.halfvec_l2_squared_distance(halfvec, halfvec)`
- `public.halfvec_le(halfvec, halfvec)`
- `public.halfvec_lt(halfvec, halfvec)`
- `public.halfvec_mul(halfvec, halfvec)`
- `public.halfvec_ne(halfvec, halfvec)`
- `public.halfvec_negative_inner_product(halfvec, halfvec)`
- `public.halfvec_out(halfvec)`
- `public.halfvec_recv(internal, oid, integer)`
- `public.halfvec_send(halfvec)`
- `public.halfvec_spherical_distance(halfvec, halfvec)`
- `public.halfvec_sub(halfvec, halfvec)`
- `public.halfvec_to_float4(halfvec, integer, boolean)`
- `public.halfvec_to_sparsevec(halfvec, integer, boolean)`
- `public.halfvec_to_vector(halfvec, integer, boolean)`
- `public.halfvec_typmod_in(cstring[])`
- `public.hamming_distance(bit, bit)`
- `public.hnsw_bit_support(internal)`
- `public.hnsw_halfvec_support(internal)`
- `public.hnsw_sparsevec_support(internal)`
- `public.hnswhandler(internal)`
- `public.inner_product(vector, vector)`
- `public.inner_product(sparsevec, sparsevec)`
- `public.inner_product(halfvec, halfvec)`
- `public.ivfflat_bit_support(internal)`
- `public.ivfflat_halfvec_support(internal)`
- `public.ivfflathandler(internal)`
- `public.jaccard_distance(bit, bit)`
- `public.l1_distance(vector, vector)`
- `public.l1_distance(halfvec, halfvec)`
- `public.l1_distance(sparsevec, sparsevec)`
- `public.l2_distance(halfvec, halfvec)`
- `public.l2_distance(sparsevec, sparsevec)`
- `public.l2_distance(vector, vector)`
- `public.l2_norm(halfvec)`
- `public.l2_norm(sparsevec)`
- `public.l2_normalize(vector)`
- `public.l2_normalize(halfvec)`
- `public.l2_normalize(sparsevec)`
- `public.sparsevec(sparsevec, integer, boolean)`
- `public.sparsevec_cmp(sparsevec, sparsevec)`
- `public.sparsevec_eq(sparsevec, sparsevec)`
- `public.sparsevec_ge(sparsevec, sparsevec)`
- `public.sparsevec_gt(sparsevec, sparsevec)`
- `public.sparsevec_in(cstring, oid, integer)`
- `public.sparsevec_l2_squared_distance(sparsevec, sparsevec)`
- `public.sparsevec_le(sparsevec, sparsevec)`
- `public.sparsevec_lt(sparsevec, sparsevec)`
- `public.sparsevec_ne(sparsevec, sparsevec)`
- `public.sparsevec_negative_inner_product(sparsevec, sparsevec)`
- `public.sparsevec_out(sparsevec)`
- `public.sparsevec_recv(internal, oid, integer)`
- `public.sparsevec_send(sparsevec)`
- `public.sparsevec_to_halfvec(sparsevec, integer, boolean)`
- `public.sparsevec_to_vector(sparsevec, integer, boolean)`
- `public.sparsevec_typmod_in(cstring[])`
- `public.subvector(vector, integer, integer)`
- `public.subvector(halfvec, integer, integer)`
- `public.sum(vector)`
- `public.sum(halfvec)`
- `public.update_updated_at_column()`
- `public.vector(vector, integer, boolean)`
- `public.vector_accum(double precision[], vector)`
- `public.vector_add(vector, vector)`
- `public.vector_avg(double precision[])`
- `public.vector_cmp(vector, vector)`
- `public.vector_combine(double precision[], double precision[])`
- `public.vector_concat(vector, vector)`
- `public.vector_dims(vector)`
- `public.vector_dims(halfvec)`
- `public.vector_eq(vector, vector)`
- `public.vector_ge(vector, vector)`
- `public.vector_gt(vector, vector)`
- `public.vector_in(cstring, oid, integer)`
- `public.vector_l2_squared_distance(vector, vector)`
- `public.vector_le(vector, vector)`
- `public.vector_lt(vector, vector)`
- `public.vector_mul(vector, vector)`
- `public.vector_ne(vector, vector)`
- `public.vector_negative_inner_product(vector, vector)`
- `public.vector_norm(vector)`
- `public.vector_out(vector)`
- `public.vector_recv(internal, oid, integer)`
- `public.vector_send(vector)`
- `public.vector_spherical_distance(vector, vector)`
- `public.vector_sub(vector, vector)`
- `public.vector_to_float4(vector, integer, boolean)`
- `public.vector_to_halfvec(vector, integer, boolean)`
- `public.vector_to_sparsevec(vector, integer, boolean)`
- `public.vector_typmod_in(cstring[])`

## supabase_migrations.schema_migrations (CLI-tracked history)

- `20260818193841` — create_llm_usage
- `20260818193842` — update_csuite_model_tiers
- `20260818195000` — joanna_rename
- `20260905120000` — caleb_ciso_nehemiah_coo
- `20260905130000` — caleb_legacy_slug

No other rows exist. Anything in `public` or `foundation` not accounted for by one of these five migrations was created outside the CLI (dashboard SQL editor or similar) and is genuinely untracked — see MIGRATION_DRIFT.md.