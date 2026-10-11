# Observation contract

One JSON object per line. Required fields: id (stable identifier), observed_at (ISO 8601 with offset), product_id (exact SKU and package), name, category, store, channel, price (NZD decimal string), quantity (positive decimal string), unit (g, ml, egg, wash, sheet, item), offer_type (regular, sale, member, multibuy), source_url, alcohol (boolean).

Optional: brand, exclusive_brand (required for restricted categories), variant, expires_at (timestamp with offset), in_stock, ply, sheet_dimensions, minimum_purchase, reward_conditions, source_kind. Multibuy quantity is total purchased quantity at total price; preserve the minimum purchase. Categories must distinguish meat cuts, formulations, detergent types and paper quality.

Reject invalid amounts, unknown units, missing store context and fabricated baselines. Deduplicate by id. Receipts prove historical purchases, not ongoing availability. Keep JSONL in private memory.

`price_scope` is `local` (default), `reference` (a configured other branch) or `regional` (a regional advertisement). Reference rows require the actual `store` and `reference_for` target location. Never rename their store to Gisborne. Historical matching also includes scope. Reference comparisons require explicit opt-in and carry an approximate flag; regional advertisements require separate review of branch exclusions and validity.

Official sources:
- https://www.paknsave.co.nz/upper-north-island/gisborne/gisborne-city
- https://www.paknsave.co.nz/shop/frequently-asked-questions
- https://www.woolworths.co.nz/
- https://www.woolworths.co.nz/help/everyday-rewards-faqs
