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

from pathlib import Path

from setuptools import find_packages, setup


rootdir = Path(__file__).parent
long_description = (rootdir / "README.md").read_text()

setup(
    name="ibquant",
    version="0.0.8",
    description="A Python Framework for Interactive Brokers TWS API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Justin Goheen",
    license="Apache 2.0",
    author_email="",
    zip_safe=False,
    classifiers=[
        "Environment :: Console",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Software Development :: User Interfaces",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.10",
    ]
)


# python = ">=3.10, <3.12"
