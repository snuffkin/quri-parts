# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#      http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from abc import abstractmethod, abstractproperty
from collections import Counter
from collections.abc import Collection, Mapping
from dataclasses import dataclass
from typing import Protocol, Union

from typing_extensions import TypeAlias

from quri_parts.circuit import ImmutableQuantumCircuit

#: SamplingCounts represents count statistics of repeated sampling or the
#: measurement probabilities of a quantum circuit. Keys are observed bit
#: patterns encoded in integers and values are counts of observation or the
#: probabilities of the corresponding bit patterns.
SamplingCounts: TypeAlias = Mapping[int, Union[float, int]]


class SamplingResult(Protocol):
    """A result of a sampling job."""

    @abstractproperty
    def counts(self) -> SamplingCounts:
        """Measurement counts obtained by a sampling measurement."""
        ...


@dataclass(frozen=True)
class CompositeSamplingResult(SamplingResult):
    """A sampling result generated by merging multiple sampling results."""

    results: Collection[SamplingResult]

    @property
    def counts(self) -> SamplingCounts:
        total = Counter[int]()
        for r in self.results:
            total += Counter(r.counts)
        return total


class SamplingJob(Protocol):
    """A job for a sampling measurement."""

    @abstractmethod
    def result(self) -> SamplingResult:
        """Returns the result of the sampling job.

        If the job is not complete, this method waits until the job
        finishes.
        """
        ...


@dataclass(frozen=True)
class CompositeSamplingJob(SamplingJob):
    """A sampling job containing multiple sampling jobs."""

    jobs: Collection[SamplingJob]

    def result(self) -> SamplingResult:
        return CompositeSamplingResult(results=[job.result() for job in self.jobs])


class SamplingBackend(Protocol):
    """A quantum computing backend that can perform a sampling measurement."""

    @abstractmethod
    def sample(self, circuit: ImmutableQuantumCircuit, n_shots: int) -> SamplingJob:
        """Perform a sampling measurement of a circuit."""
        ...


class BackendError(Exception):
    """BackendError represents an error caused by a quantum computing
    backend."""

    pass
