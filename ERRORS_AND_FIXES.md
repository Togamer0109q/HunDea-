# Common Errors and Fixes

This is a quick reference for the most common runtime errors and how to fix them.

## 1) Missing GG.deals key
**Error**
- `Missing GGDEALS_API_KEY in .env`

**Fix**
- Create `.env` from `.env.example` and set:
  - `GGDEALS_API_KEY=...`
  - `GGDEALS_REGION=us` (optional)

## 2) Missing python-dotenv
**Error**
- `ModuleNotFoundError: No module named 'dotenv'`

**Fix**
- Install dependencies:
  - `pip install python-dotenv`
  - or `pip install -r requirements.txt`
  - or `pip install -r requirements_v3.txt`

## 3) SistemaScoring takes no arguments
**Error**
- `TypeError: SistemaScoring() takes no arguments`

**Fix**
- Ensure `modules/core/scoring.py` includes `__init__(self, logger=None)`.

## 4) ReviewsExternas logger mismatch
**Error**
- `TypeError: ReviewsExternas.__init__() got an unexpected keyword argument 'logger'`

**Fix**
- Ensure `modules/reviews_externas.py` supports `logger` in `__init__`.

## 4b) ItchHunter logger mismatch
**Error**
- `TypeError: ItchHunter.__init__() got an unexpected keyword argument 'logger'`

**Fix**
- Ensure `modules/itch_hunter.py` supports `logger` in `__init__`.

## 4c) MegaAPIAggregator stats missing
**Error**
- `AttributeError: 'MegaAPIAggregator' object has no attribute 'stats'`

**Fix**
- Initialize `self.stats` before calling `_init_hunters()`.

## 5) GG.deals rate limit (429)
**Error**
- `429 Too Many Requests`

**Fix**
- Reduce batch size or wait for reset.
- Use fewer Steam App IDs per minute.

## 6) Xbox Reco API DNS failure
**Error**
- `Failed to resolve or connect to Xbox API`

**Fix**
- This is a DNS/network issue. Ensure the machine can resolve:
  - `reco-public.rec.mp.microsoft.com`
- Fallback to CheapShark still works.

## 7) 0 deals after filtering
**Symptom**
- Deals fetched but filtered to 0.

**Fix**
- Review `config.json` filters:
  - `min_discount`, `min_score`, `max_price`
- Set lower thresholds for testing.

## 8) GG.deals enrichment not applied
**Symptom**
- No `ggdeals_*` fields on deals.

**Fix**
- Ensure:
  - `GGDEALS_API_KEY` set in `.env`
  - Deals include `steam_app_id`
  - Run `hundea_v3_ultra.py` (uses MegaAPIAggregator)

## 9) PlayStation deals always 0
**Symptom**
- PlatPrices returns 0 deals.

**Fix**
- Verify `PLATPRICES_API_KEY` in `.env`
- Try different region or check if API has current discounts.
