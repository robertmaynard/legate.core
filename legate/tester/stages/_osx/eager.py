# Copyright 2022 NVIDIA Corporation
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
#
from __future__ import annotations

from typing import TYPE_CHECKING

from ..test_stage import TestStage
from ..util import EAGER_ENV, UNPIN_ENV, Shard, StageSpec, adjust_workers

if TYPE_CHECKING:
    from ....util.types import ArgList, EnvDict
    from ... import FeatureType
    from ...config import Config
    from ...test_system import TestSystem


class Eager(TestStage):
    """A test stage for exercising Eager Numpy execution features.

    Parameters
    ----------
    config: Config
        Test runner configuration

    system: TestSystem
        Process execution wrapper

    """

    kind: FeatureType = "eager"

    args: ArgList = []

    def __init__(self, config: Config, system: TestSystem) -> None:
        self._init(config, system)

    def env(self, config: Config, system: TestSystem) -> EnvDict:
        env = dict(EAGER_ENV)
        env.update(UNPIN_ENV)
        return env

    def shard_args(self, shard: Shard, config: Config) -> ArgList:
        return ["--cpus", "1"]

    def compute_spec(self, config: Config, system: TestSystem) -> StageSpec:
        N = len(system.cpus)
        degree = min(N, 60)  # ~LEGION_MAX_NUM_PROCS just in case
        workers = adjust_workers(degree, config.requested_workers)

        # return a dummy set of shards just for the runner to iterate over
        return StageSpec(workers, [(i,) for i in range(workers)])
