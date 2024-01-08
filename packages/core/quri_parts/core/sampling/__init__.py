# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#      http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from collections import Counter
from typing import Callable, Collection, Iterable, Mapping, NamedTuple, Sequence, Union

import numpy as np
import numpy.typing as npt
from typing_extensions import TypeAlias

from quri_parts.backend import SamplingBackend
from quri_parts.circuit import NonParametricQuantumCircuit
from quri_parts.core.operator import CommutablePauliSet, Operator
from quri_parts.core.state import CircuitQuantumState, QuantumStateVector

#: MeasurementCounts represents count statistics of repeated measurements of a quantum
#: circuit. Keys are observed bit patterns encoded in integers and values are counts
#: of observation of the corresponding bit patterns.
MeasurementCounts: TypeAlias = Mapping[int, Union[int, float]]

#: Sampler represents a function that samples a specified (non-parametric) circuit by
#: a specified times and returns the count statistics. In the case of an ideal Sampler,
# the return value corresponds to probabilities multiplied by shot count.
Sampler: TypeAlias = Callable[[NonParametricQuantumCircuit, int], MeasurementCounts]

#: ConcurrentSampler represents a function that samples specified (non-parametric)
#: circuits concurrently.
ConcurrentSampler: TypeAlias = Callable[
    [Iterable[tuple[NonParametricQuantumCircuit, int]]], Iterable[MeasurementCounts]
]

#: StateSampler representes a function that samples a specific (non-parametric) state by
#: specified times and returns the count statistics. In the case of an ideal
#: StateSampler, the return value corresponds to probabilities multiplied by shot count.
StateSampler: TypeAlias = Callable[
    [Union[CircuitQuantumState, QuantumStateVector], int], MeasurementCounts
]


def sample_from_state_vector(
    state_vector: npt.NDArray[np.complex128], n_shots: int
) -> MeasurementCounts:
    """Perform sampling from a state vector."""
    n_qubits: float = np.log2(state_vector.shape[0])
    assert n_qubits.is_integer(), "Length of the state vector must be a power of 2."
    prob = np.abs(state_vector) ** 2
    return Counter(np.random.choice(range(len(state_vector)), size=n_shots, p=prob))


def ideal_sample_from_state_vector(
    state_vector: npt.NDArray[np.complex128], n_shots: int
) -> MeasurementCounts:
    """Perform ideal sampling from a state vector."""
    n_qubits: float = np.log2(state_vector.shape[0])
    assert n_qubits.is_integer(), "Length of the state vector must be a power of 2."
    if not np.isclose(np.linalg.norm(state_vector), 1):
        raise ValueError("probabilities do not sum to 1")

    prob = np.abs(state_vector) ** 2
    return {i: p * n_shots for i, p in enumerate(prob)}


def create_sampler_from_sampling_backend(backend: SamplingBackend) -> Sampler:
    """Create a simple :class:`~Sampler` using a :class:`~SamplingBackend`."""

    def sampler(
        circuit: NonParametricQuantumCircuit, n_shots: int
    ) -> MeasurementCounts:
        job = backend.sample(circuit, n_shots)
        return job.result().counts

    return sampler


def create_concurrent_sampler_from_sampling_backend(
    backend: SamplingBackend,
) -> ConcurrentSampler:
    """Create a simple :class:`~ConcurrentSampler` using a
    :class:`~SamplingBackend`."""

    def sampler(
        shot_circuit_pairs: Iterable[tuple[NonParametricQuantumCircuit, int]]
    ) -> Iterable[MeasurementCounts]:
        jobs = [
            backend.sample(circuit, n_shots) for circuit, n_shots in shot_circuit_pairs
        ]
        return map(lambda j: j.result().counts, jobs)

    return sampler


def create_sampler_from_concurrent_sampler(
    concurrent_sampler: ConcurrentSampler,
) -> Sampler:
    def sampler(circuit: NonParametricQuantumCircuit, shots: int) -> MeasurementCounts:
        return next(iter(concurrent_sampler([(circuit, shots)])))

    return sampler


class PauliSamplingSetting(NamedTuple):
    pauli_set: CommutablePauliSet
    n_shots: int


#: PauliSamplingShotsAllocator represents a function that distributes
#: a given number of sampling shots to each :class:`~CommutablePauliSet`.
PauliSamplingShotsAllocator: TypeAlias = Callable[
    [Operator, Collection[CommutablePauliSet], int], Collection[PauliSamplingSetting]
]


#: WeightedSamplingShotsAllocator represents a function that distributes
#: a given number of sampling shots based on a set of weights.
WeightedSamplingShotsAllocator: TypeAlias = Callable[
    [Sequence[complex], int], Sequence[int]
]


__all__ = [
    "MeasurementCounts",
    "Sampler",
    "ConcurrentSampler",
    "create_sampler_from_sampling_backend",
    "create_concurrent_sampler_from_sampling_backend",
    "create_sampler_from_concurrent_sampler",
    "PauliSamplingSetting",
    "PauliSamplingShotsAllocator",
    "WeightedSamplingShotsAllocator",
]
