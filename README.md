# nz-grocery-deals

Portable skill and private price-memory format for Gisborne grocery tracking. Read SKILL.md in any LLM with file access, or install this folder as nz-grocery-deals in the host's skill directory. Copy templates/profile.json to memory/profile.json to begin private memory. No credentials are included.

The skill records verified source observations, compares compatible prices, and supports Everyday Rewards. PAK'nSAVE Gisborne has no online shopping: its local offers require a separate verified source such as advertisements or receipts. Live collection is not yet automated. Do not treat this package as a deployed daily monitoring service.

Run `python -m unittest discover -s tests` to validate the comparison helper. Scripts use the Python standard library. `python scripts/compare.py memory/prices.jsonl` prints regular alternatives beating offers within compatible categories. The caller must supply verified observations and restrict candidates to permitted watchlist brands. Alcohol is excluded in the helper itself.

Hosted deployment requires a tested source collector, persistent private history, and Telegram delivery configuration. GitHub Actions can run while the PC is off, but schedules may be delayed and public-repository schedules may disable after 60 days without activity. Do not enable a schedule until source collection and history persistence work. Never store private state in public commits or public workflow artifacts. A local signed-in browser does not provide hosted authentication. Secrets: TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID; configure privately through GitHub settings. Verify the destination using the bot's incoming /start event before sending.

Planned public repository: Mozz814/nz-grocery-deals. Existing repository configuration should be inspected before changing the remote. Local checkout target: E:\AI Brain\AI Skills\Grocery. Sync private history to that disk when online through a separately configured private backend.
