# Observation contract

One JSON object per line. Required fields: `id` (stable observation identifier), `observed_at` (ISO 8601 timestamp with offset), `product_id`, `name`, `category`, `store`, `channel`, `price` (NZD decimal string), `quantity` (positive decimal string), `unit` (`g`, `ml`, `egg`, `wash`, `sheet`, or `item`), `offer_type` (`regular`, `sale`, `member`, `multibuy`), `source_url`, `alcohol` (boolean).

Optional: `brand`, `exclusive_brand` (required for a brand-restricted category), `variant`, `expires_at` (timestamp with offset), `in_stock`, `ply`, `sheet_dimensions`, `minimum_purchase`, `reward_conditions`, `source_kind`. Quantity is the total quantity purchased at the recorded price: for a multibuy record total payment and total size, and preserve minimum_purchase. product_id identifies an exact SKU including package size. Separate kinds of meat, cuts, milk formulations, detergents and paper quality into different categories for comparisons. Paper categories must include ply/dimensions when known; detergent categories must distinguish laundry from dishwasher and compatible dosage assumptions.

No zero/negative amounts, unsupported units, missing store context, or fabricated baseline prices. Deduplicate by id. A receipt proves a purchased price at its timestamp, not ongoing availability. JSONL files belong in private memory storage.

Official starting sources:
- https://www.paknsave.co.nz/upper-north-island/gisborne/gisborne-city
- https://www.paknsave.co.nz/shop/frequently-asked-questions
- https://www.woolworths.co.nz/
- https://www.woolworths.co.nz/help/everyday-rewards-faqs
