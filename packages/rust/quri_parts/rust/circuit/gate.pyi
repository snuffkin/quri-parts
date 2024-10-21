from typing import Any, Optional, Sequence, Tuple

class QuantumGate:
    def __init__(
        self,
        name: str,
        target_indices: Sequence[int],
        control_indices: Sequence[int] = [],
        classical_indices: Sequence[int] = [],
        params: Sequence[float] = [],
        pauli_ids: Sequence[int] = [],
        unitary_matrix: Optional[Sequence[Sequence[complex]]] = None,
    ) -> None: ...
    def __repr__(self) -> str: ...
    def __reduce__(self) -> Tuple[type, Any]: ...
    def __hash__(self) -> int: ...
    @property
    def name(self) -> str: ...
    @property
    def target_indices(self) -> Sequence[int]: ...
    @property
    def control_indices(self) -> Sequence[int]: ...
    @property
    def classical_indices(self) -> Sequence[int]: ...
    @property
    def params(self) -> Sequence[float]: ...
    @property
    def pauli_ids(self) -> Sequence[int]: ...
    @property
    def unitary_matrix(self) -> Sequence[Sequence[complex]]: ...

class ParametricQuantumGate:
    def __init__(
        self,
        name: str,
        target_indices: Sequence[int],
        control_indices: Sequence[int] = [],
        pauli_ids: Sequence[int] = [],
    ) -> None: ...
    def __repr__(self) -> str: ...
    def __reduce__(self) -> Tuple[type, Any]: ...
    def __hash__(self) -> int: ...
    @property
    def name(self) -> str: ...
    @property
    def target_indices(self) -> Sequence[int]: ...
    @property
    def control_indices(self) -> Sequence[int]: ...
    @property
    def pauli_ids(self) -> Sequence[int]: ...
