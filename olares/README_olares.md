## Run as Otomic Edge Algorithm on Olares

### Image
Build and push the image to a registry reachable by Olares.

### Deploy in Olares Studio
Create App → Port your own container to Olares. :contentReference[oaicite:9]{index=9}

- Image: <your_image>
- Container Port: 8080
- Env:
  - FT_CONFIG=/freqtrade/config/kraken.json  (or coinbase/bybit/binance)
  - FT_STRATEGY=GridSimple (or any strategy in user_data/strategies)
  - DISABLE_TRADING=1 (recommended default)
  - DATA_DIR=/data (optional)
- Storage Volume (recommended):
  - Mount path: /data

### Multi-exchange
Deploy multiple apps/instances:
- App A: FT_CONFIG=/freqtrade/config/kraken.json
- App B: FT_CONFIG=/freqtrade/config/coinbase.json
- App C: FT_CONFIG=/freqtrade/config/bybit.json

Each instance is one exchange.

### Offline validation (no exchange required)
Run offline validation inside the container:
python /freqtrade/offline_validate.py