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
from plotly.colors import diverging
from plotly.subplots import make_subplots


class MarketDepthVisualizations:
    def plot_spread(data, index_location=1):
        """plots bids on right and asks on left to visualize mid price as spread"""

        prices = [i for i in data.columns if "price" in i]
        sizes = [i for i in data.columns if "size" in i]

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(
            go.Scatter(
                x=data.iloc[index_location][[i for i in prices if "bid" in i]],
                y=data.iloc[index_location][[i for i in sizes if "bid" in i]],
                fill="tozeroy",
                name="Bids",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=data.iloc[index_location][[i for i in prices if "ask" in i]],
                y=data.iloc[index_location][[i for i in sizes if "ask" in i]],
                fill="tozeroy",
                name="Asks",
            ),
            secondary_y=True,
        )
        fig.update_layout(
            title={
                "text": "Spread",
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
        fig.show()

    def plot_levels(data, levels=10):
        """
        plots a cmap-like timeseries plot to visualize dominate bid and asks across time
        levels: max number is 10
        """
        fig = go.Figure()
        for i in range(1, levels + 1):
            fig.add_trace(go.Scatter(y=data[f"bidprice{i}"], marker_color=diverging.Spectral[i], showlegend=False))
            fig.add_trace(go.Scatter(y=data[f"askprice{i}"], marker_color=diverging.Spectral[i], showlegend=False))

        fig.update_layout(
            title={
                "text": "Levels",
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

        fig.show()

    def plot_heatmap(data, levels=5):
        """overlays a mid-price plot onto a heatmap of dominate bids and asks"""

        prices = [i for i in data.columns if "price" in i]
        all_sizes = [i for i in data.columns if "size" in i]
        bids = [i for i in all_sizes if "bid" in i]
        asks = [i for i in all_sizes if "ask" in i]
        sizes = asks[::-1][: levels + 1] + bids[: levels + 1]  # make sizes meet in the middle

        fig = make_subplots(specs=[[{"secondary_y": True}]])

        fig.add_trace(
            go.Scatter(y=data[prices].mean(axis=1), marker_color="white", line=dict(width=4)), secondary_y=True
        )
        fig.add_trace(go.Heatmap(z=data[sizes].T, name="Bid Ask Size"))

        fig.update_layout(
            title={
                "text": str(data.index[0].date())
                + f" start: {str(data.index[0].time())}"
                + f" end: {str(data.index[-1].time())}",
                "y": 0.97,
                "x": 0.2,
                "xanchor": "left",
                "yanchor": "top",
            },
            xaxis_rangeslider_visible=False,
            height=400,
            width=1000,
            margin=dict(l=25, r=10, b=25, t=30),
        )

        fig.show()
