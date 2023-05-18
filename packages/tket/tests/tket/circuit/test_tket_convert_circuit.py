# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#      http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from collections.abc import Mapping
from typing import Callable, Type, cast

import numpy as np
from pytket import Circuit, OpType
from pytket.circuit import Unitary1qBox, Unitary2qBox, Unitary3qBox  # type: ignore
from scipy.stats import unitary_group

from quri_parts.circuit import QuantumCircuit, QuantumGate, gates
from quri_parts.tket.circuit import convert_circuit


def circuit_equal(c1: Circuit, c2: Circuit) -> bool:
    # Compare the matrix representation of the circuits, including the global phase.
    return cast(bool, np.all(c1.get_unitary() == c2.get_unitary()))


single_qubit_gate_mapping: Mapping[Callable[[int], QuantumGate], OpType] = {
    gates.Identity: OpType.noop,
    gates.X: OpType.X,
    gates.Y: OpType.Y,
    gates.Z: OpType.Z,
    gates.H: OpType.H,
    gates.S: OpType.S,
    gates.Sdag: OpType.Sdg,
    gates.T: OpType.T,
    gates.Tdag: OpType.Tdg,
    gates.SqrtX: OpType.SX,
    gates.SqrtXdag: OpType.SXdg,
}


def test_convert_single_qubit_gate() -> None:
    for qp_factory, tket_gate in single_qubit_gate_mapping.items():
        target_index = 7
        n_qubit = 8

        qp_gate = qp_factory(target_index)
        qp_circuit = QuantumCircuit(n_qubit)
        qp_circuit.add_gate(qp_gate)

        tket_circuit = Circuit(n_qubit)
        tket_circuit.add_gate(tket_gate, [target_index])

        converted = convert_circuit(qp_circuit)
        expected = tket_circuit
        assert circuit_equal(converted, expected)


single_qubit_sqrt_y_gate_mapping: Mapping[
    Callable[[int], QuantumGate], Unitary1qBox
] = {
    gates.SqrtY: Unitary1qBox(
        np.array([[0.5 + 0.5j, -0.5 - 0.5j], [0.5 + 0.5j, 0.5 + 0.5j]])
    ),
    gates.SqrtYdag: Unitary1qBox(
        np.array([[0.5 - 0.5j, 0.5 - 0.5j], [-0.5 + 0.5j, 0.5 - 0.5j]])
    ),
}


def test_convert_single_qubit_sgate() -> None:
    for qp_factory, tket_gate in single_qubit_sqrt_y_gate_mapping.items():
        target_index = 7
        n_qubit = 8

        qp_gate = qp_factory(target_index)
        qp_circuit = QuantumCircuit(n_qubit)
        qp_circuit.add_gate(qp_gate)

        tket_circuit = Circuit(n_qubit)
        tket_circuit.add_unitary1qbox(tket_gate, target_index)

        converted = convert_circuit(qp_circuit)
        expected = tket_circuit
        assert circuit_equal(converted, expected)


rotation_gate_mapping: Mapping[Callable[[int, float], QuantumGate], Type[OpType]] = {
    gates.RX: OpType.Rx,
    gates.RY: OpType.Ry,
    gates.RZ: OpType.Rz,
}


def test_convert_rotation_gate() -> None:
    for qp_factory, tket_gate in rotation_gate_mapping.items():
        target_index = 7
        n_qubit = 8

        qp_gate = qp_factory(7, 0.125)
        qp_circuit = QuantumCircuit(n_qubit)
        qp_circuit.add_gate(qp_gate)

        tket_circuit = Circuit(n_qubit)
        tket_circuit.add_gate(tket_gate, 0.125 / np.pi, [target_index])

        converted = convert_circuit(qp_circuit)
        expected = tket_circuit
        assert circuit_equal(converted, expected)


two_qubit_gate_mapping: Mapping[Callable[[int, int], QuantumGate], OpType] = {
    gates.CNOT: OpType.CX,
    gates.CZ: OpType.CZ,
    gates.SWAP: OpType.SWAP,
}


def test_convert_two_qubit_gate() -> None:
    for qp_factory, tket_gate in two_qubit_gate_mapping.items():
        target_index = 7
        control_index = 4
        n_qubit = 8

        qp_gate = qp_factory(control_index, target_index)
        qp_circuit = QuantumCircuit(n_qubit)
        qp_circuit.add_gate(qp_gate)

        tket_circuit = Circuit(n_qubit)
        tket_circuit.add_gate(tket_gate, [control_index, target_index])

        converted = convert_circuit(qp_circuit)
        expected = tket_circuit

        assert circuit_equal(converted, expected)


three_qubit_gate_mapping: Mapping[Callable[[int, int, int], QuantumGate], OpType] = {
    gates.TOFFOLI: OpType.CCX,
}


def test_convert_three_qubit_gate() -> None:
    for qp_factory, tket_gate in three_qubit_gate_mapping.items():
        target_index = 7
        control_index_1 = 4
        control_index_2 = 2
        n_qubit = 8

        qp_gate = qp_factory(control_index_1, control_index_2, target_index)
        qp_circuit = QuantumCircuit(n_qubit)
        qp_circuit.add_gate(qp_gate)

        tket_circuit = Circuit(n_qubit)
        tket_circuit.add_gate(
            tket_gate, [control_index_1, control_index_2, target_index]
        )

        converted = convert_circuit(qp_circuit)
        expected = tket_circuit

        assert circuit_equal(converted, expected)


def test_convert_unitary_matrix_1q_gate() -> None:
    umat = ((1, 0), (0, np.cos(np.pi / 4) + 1j * np.sin(np.pi / 4)))

    target_index = 7
    n_qubit = 8

    qp_gate = gates.UnitaryMatrix((7,), umat)
    qp_circuit = QuantumCircuit(n_qubit)
    qp_circuit.add_gate(qp_gate)

    tket_circuit = Circuit(n_qubit)
    tket_circuit.add_unitary1qbox(Unitary1qBox(umat), target_index)

    converted = convert_circuit(qp_circuit)
    expected = tket_circuit

    assert circuit_equal(converted, expected)


def test_convert_unitary_matrix_2q_gate() -> None:
    umat = unitary_group.rvs(4)

    target_indices = (4, 7)
    n_qubit = 8

    qp_gate = gates.UnitaryMatrix(target_indices, umat)
    qp_circuit = QuantumCircuit(n_qubit)
    qp_circuit.add_gate(qp_gate)

    tket_circuit = Circuit(n_qubit)
    tket_circuit.add_unitary2qbox(Unitary2qBox(umat), *target_indices)

    converted = convert_circuit(qp_circuit)
    expected = tket_circuit

    assert circuit_equal(converted, expected)


def test_convert_unitary_matrix_3q_gate() -> None:
    umat = unitary_group.rvs(8)

    target_indices = (4, 5, 7)
    n_qubit = 8

    qp_gate = gates.UnitaryMatrix(target_indices, umat)
    qp_circuit = QuantumCircuit(n_qubit)
    qp_circuit.add_gate(qp_gate)

    tket_circuit = Circuit(n_qubit)
    tket_circuit.add_unitary3qbox(Unitary3qBox(umat), *target_indices)

    converted = convert_circuit(qp_circuit)
    expected = tket_circuit

    assert circuit_equal(converted, expected)


def test_convert_u1_gate() -> None:
    lmd1 = 0.125

    target_index = 7
    n_qubit = 8

    qp_gate = gates.U1(lmd=lmd1, target_index=target_index)
    qp_circuit = QuantumCircuit(n_qubit)
    qp_circuit.add_gate(qp_gate)

    tket_circuit = Circuit(n_qubit)
    tket_circuit.add_gate(OpType.U1, [lmd1 / np.pi], [target_index])

    converted = convert_circuit(qp_circuit)
    expected = tket_circuit

    assert circuit_equal(converted, expected)


def test_convert_u2_gate() -> None:
    phi2, lmd2 = 0.125, -0.125

    target_index = 7
    n_qubit = 8

    qp_gate = gates.U2(lmd=lmd2, phi=phi2, target_index=target_index)
    qp_circuit = QuantumCircuit(n_qubit)
    qp_circuit.add_gate(qp_gate)

    tket_circuit = Circuit(n_qubit)
    tket_circuit.add_gate(OpType.U2, [phi2 / np.pi, lmd2 / np.pi], [target_index])

    converted = convert_circuit(qp_circuit)
    expected = tket_circuit

    assert circuit_equal(converted, expected)


def test_convert_u3_gate() -> None:
    theta3, phi3, lmd3 = 0.125, -0.125, 0.625
    target_index = 7
    n_qubit = 8

    qp_gate = gates.U3(lmd=lmd3, phi=phi3, theta=theta3, target_index=target_index)
    qp_circuit = QuantumCircuit(n_qubit)
    qp_circuit.add_gate(qp_gate)

    tket_circuit = Circuit(n_qubit)
    tket_circuit.add_gate(
        OpType.U3, [theta3 / np.pi, phi3 / np.pi, lmd3 / np.pi], [target_index]
    )

    converted = convert_circuit(qp_circuit)
    expected = tket_circuit

    assert circuit_equal(converted, expected)


def test_convert_circuit() -> None:
    circuit = QuantumCircuit(3)
    original_gates = [
        gates.X(1),
        gates.H(2),
        gates.CNOT(0, 2),
        gates.RX(0, 0.125),
    ]
    for gate in original_gates:
        circuit.add_gate(gate)

    converted = convert_circuit(circuit)
    assert converted.n_qubits == 3

    expected = Circuit(3)
    expected.X(1)
    expected.H(2)
    expected.CX(0, 2)
    expected.Rx(0.125 / np.pi, 0)

    assert circuit_equal(converted, expected)
