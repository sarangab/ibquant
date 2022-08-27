# Copyright Justin R. Goheen.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import ib_insync as ib


class MarketContracts:

    EquityFutureMinis = dict(
        SNP500=ib.Future("ES", exchange="GLOBEX"),
        RUSSELL=ib.Future("RTY", exchange="GLOBEX"),
        N100=ib.Future("NQ", exchange="GLOBEX"),
    )

    EquityFutureMicros = dict(
        SNP500=ib.Future("MES", exchange="GLOBEX"),
        RUSSELL=ib.Future("M2K", exchange="GLOBEX"),
        N100=ib.Future("MNQ", exchange="GLOBEX"),
    )

    EquityFutureMicrosIndex = dict(
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

    IndexVolatility = dict(
        SNP500=ib.Index("VIX", exchange="CBOE"),
        N100=ib.Index("VXN", exchange="CBOE"),
        RUSSELL=ib.Index("RVX", exchange="CBOE"),
    )
