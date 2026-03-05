FROM freqtradeorg/freqtrade:stable

WORKDIR /freqtrade

COPY --chmod=755 entrypoint.sh /entrypoint.sh

COPY config/ /freqtrade/config/
COPY user_data/ /freqtrade/user_data/
COPY olares/ /freqtrade/olares/
COPY REPORT.md /freqtrade/REPORT.md

ENV FT_CONFIG=/freqtrade/config/config.json
ENV FT_STRATEGY=GridSimple
ENV FT_CMD=trade

ENTRYPOINT ["/entrypoint.sh"]