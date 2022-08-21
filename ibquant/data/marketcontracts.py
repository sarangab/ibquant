import ib_insync as ib


class MarketContracts:

    EquityMinis = dict(
        SNP500=ib.Future("ES", exchange="GLOBEX"),
        RUSSELL=ib.Future("RTY", exchange="GLOBEX"),
        N100=ib.Future("NQ", exchange="GLOBEX"),
    )

    EquityMicros = dict(
        SNP500=ib.Future("MES", exchange="GLOBEX"),
        RUSSELL=ib.Future("M2K", exchange="GLOBEX"),
        N100=ib.Future("MNQ", exchange="GLOBEX"),
    )

    EquityMicrosIndex = dict(
        SNP500=ib.Index("MES", exchange="GLOBEX"),
        RUSSELL=ib.Future("M2K", exchange="GLOBEX"),
        N100=ib.Future("MNQ", exchange="GLOBEX"),
    )

    VixTerms = dict(
        VIX=ib.Index("VIX", exchange="CBOE"),
        VIX3M=ib.Index("VIX3M", exchange="CBOE"),
        VIX6M=ib.Index("VIX6M", exchange="CBOE"),
        VIX1Y=ib.Index("VIX1Y", exchange="CBOE"),
        VIX9D=ib.Index("VIX9D", exchange="CBOE"),
    )

    IndexVol = dict(
        SNP500=ib.Index("VIX", exchange="CBOE"),
        N100=ib.Index("VXN", exchange="CBOE"),
        RUSSELL=ib.Index("RVX", exchange="CBOE"),
    )
