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

import plotly.graph_objects as go


def plot_strategy(data, symbol="SPY"):
    """plots strategy returns given a dataframe"""

    trading = data.loc[data["Trades"] != 0, "Trades"]
    starts = trading.index[::2]
    stops = trading.index.difference(starts)

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=data.index, y=data["Close"], name=f"{symbol} Close"))

    for start, stop in zip(starts, stops):
        fig.add_vrect(
            x0=start,
            x1=stop,
            fillcolor="grey",
            opacity=0.25,
            line_width=0,
        )

    fig.update_layout(
        title={
            "text": symbol + " (grey shaded areas indicate flat position)",
            "y": 0.97,
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "top",
        },
        legend=dict(title="", yanchor="top", y=1.06, xanchor="left", x=0, orientation="h"),
        xaxis_rangeslider_visible=False,
        height=400,
        width=1000,
        margin=dict(l=25, r=10, b=25, t=30),
    )

    return fig
