# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#      http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytest

from quri_parts.chem.utils.excitations import excitations
from quri_parts.circuit import LinearMappedUnboundParametricQuantumCircuit
from quri_parts.core.operator import Operator, pauli_label
from quri_parts.openfermion.ansatz.uccsd import (
    TrotterSingletUCCSD,
    _add_excitation_circuit,
    _construct_circuit,
    _create_operator,
)
from quri_parts.openfermion.transforms import (
    bravyi_kitaev,
    jordan_wigner,
    symmetry_conserving_bravyi_kitaev,
)


class TestCreateOperator:
    def test_create_operator_single_excitation_jw(self) -> None:
        jw_mapper = jordan_wigner.get_of_operator_mapper()

        s_exc = (0, 2)
        op = _create_operator(s_exc, jw_mapper)
        expected_op = Operator(
            {pauli_label("X0 Z1 Y2"): -0.5j, pauli_label("Y0 Z1 X2"): 0.5j}
        )
        assert op == expected_op

        s_exc = (1, 3)
        op = _create_operator(s_exc, jw_mapper)
        expected_op = Operator(
            {pauli_label("X1 Z2 Y3"): -0.5j, pauli_label("Y1 Z2 X3"): 0.5j}
        )
        assert op == expected_op

    def test_create_operator_single_excitation_bk(self) -> None:
        bk_mapper = bravyi_kitaev.get_of_operator_mapper()

        s_exc = (0, 2)
        op = _create_operator(s_exc, bk_mapper)
        expected_op = Operator(
            {pauli_label("X0 Y1 X2"): 0.5j, pauli_label("Y0 Y1 Y2"): 0.5j}
        )
        assert op == expected_op

        s_exc = (1, 3)
        op = _create_operator(s_exc, bk_mapper)
        expected_op = Operator(
            {pauli_label("Z0 Y1 Z2"): 0.5j, pauli_label("Y1 Z3"): -0.5j}
        )
        assert op == expected_op

    def test_create_operator_single_excitation_scbk(self) -> None:
        n_sorbs = 4
        n_elecs = 2
        scbk_mapper = symmetry_conserving_bravyi_kitaev.get_of_operator_mapper(
            n_sorbs, n_elecs
        )

        s_exc = (0, 2)
        op = _create_operator(s_exc, scbk_mapper)
        expected_op = Operator({pauli_label("Y0"): 1.0j})
        assert op == expected_op

        s_exc = (1, 3)
        op = _create_operator(s_exc, scbk_mapper)
        expected_op = Operator({pauli_label("Y1"): 1.0j})
        assert op == expected_op

    def test_create_operator_double_excitation_jw(self) -> None:
        jw_mapper = jordan_wigner.get_of_operator_mapper()

        d_exc = (0, 1, 2, 3)
        op = _create_operator(d_exc, jw_mapper)
        expected_op = Operator(
            {
                pauli_label("X0 X1 X2 Y3"): 0.125j,
                pauli_label("X0 X1 Y2 X3"): 0.125j,
                pauli_label("X0 Y1 X2 X3"): -0.125j,
                pauli_label("X0 Y1 Y2 Y3"): 0.125j,
                pauli_label("Y0 X1 X2 X3"): -0.125j,
                pauli_label("Y0 X1 Y2 Y3"): 0.125j,
                pauli_label("Y0 Y1 X2 Y3"): -0.125j,
                pauli_label("Y0 Y1 Y2 X3"): -0.125j,
            }
        )
        assert op == expected_op

        d_exc = (0, 3, 4, 7)
        op = _create_operator(d_exc, jw_mapper)
        expected_op = Operator(
            {
                pauli_label("X0 Z1 Z2 X3 X4 Z5 Z6 Y7"): 0.125j,
                pauli_label("X0 Z1 Z2 X3 Y4 Z5 Z6 X7"): 0.125j,
                pauli_label("X0 Z1 Z2 Y3 X4 Z5 Z6 X7"): -0.125j,
                pauli_label("X0 Z1 Z2 Y3 Y4 Z5 Z6 Y7"): 0.125j,
                pauli_label("Y0 Z1 Z2 X3 X4 Z5 Z6 X7"): -0.125j,
                pauli_label("Y0 Z1 Z2 X3 Y4 Z5 Z6 Y7"): 0.125j,
                pauli_label("Y0 Z1 Z2 Y3 X4 Z5 Z6 Y7"): -0.125j,
                pauli_label("Y0 Z1 Z2 Y3 Y4 Z5 Z6 X7"): -0.125j,
            }
        )
        assert op == expected_op

    def test_create_operator_double_excitation_bk(self) -> None:
        bk_mapper = bravyi_kitaev.get_of_operator_mapper()

        d_exc = (0, 1, 2, 3)
        op = _create_operator(d_exc, bk_mapper)
        expected_op = Operator(
            {
                pauli_label("X0 Y2"): 0.125j,
                pauli_label("X0 Z1 Y2"): 0.125j,
                pauli_label("Y0 X2"): -0.125j,
                pauli_label("Y0 Z1 X2"): -0.125j,
                pauli_label("Y0 Z1 X2 Z3"): -0.125j,
                pauli_label("Y0 X2 Z3"): -0.125j,
                pauli_label("X0 Z1 Y2 Z3"): 0.125j,
                pauli_label("X0 Y2 Z3"): 0.125j,
            }
        )
        assert op == expected_op

        d_exc = (0, 3, 4, 7)
        op = _create_operator(d_exc, bk_mapper)
        expected_op = Operator(
            {
                pauli_label("Y0 Y1 Z2 X4 Y5 Z6"): -0.125j,
                pauli_label("X0 X1 Z3 X4 Y5 Z6"): 0.125j,
                pauli_label("X0 Y1 Z2 Y4 Y5 Z6"): 0.125j,
                pauli_label("Y0 X1 Z3 Y4 Y5 Z6"): 0.125j,
                pauli_label("X0 Y1 Z2 Z3 X4 X5 Z7"): -0.125j,
                pauli_label("Y0 X1 X4 X5 Z7"): -0.125j,
                pauli_label("Y0 Y1 Z2 Z3 Y4 X5 Z7"): -0.125j,
                pauli_label("X0 X1 Y4 X5 Z7"): 0.125j,
            }
        )
        assert op == expected_op

    def test_create_operator_double_excitation_scbk(self) -> None:
        scbk_mapper = symmetry_conserving_bravyi_kitaev.get_of_operator_mapper(4, 2)

        d_exc = (0, 1, 2, 3)
        op = _create_operator(d_exc, scbk_mapper)
        expected_op = Operator(
            {
                pauli_label("X0 Y1"): -0.5j,
                pauli_label("Y0 X1"): -0.5j,
            }
        )
        assert op == expected_op

        scbk_mapper = symmetry_conserving_bravyi_kitaev.get_of_operator_mapper(8, 2)
        d_exc = (0, 3, 4, 7)
        op = _create_operator(d_exc, scbk_mapper)
        expected_op = Operator(
            {
                pauli_label("Y0 Y1 X2 Z3 Y4 Z5"): 0.125j,
                pauli_label("X0 Y1 X2 X4 Z5"): -0.125j,
                pauli_label("X0 Y1 Y2 Z3 Y4 Z5"): -0.125j,
                pauli_label("Y0 Y1 Y2 X4 Z5"): -0.125j,
                pauli_label("X0 Y1 X2 Z3 X4"): -0.125j,
                pauli_label("Y0 Y1 X2 Y4"): 0.125j,
                pauli_label("Y0 Y1 Y2 Z3 X4"): -0.125j,
                pauli_label("X0 Y1 Y2 Y4"): -0.125j,
            }
        )
        assert op == expected_op


class TestAddExcitationCircuit:
    def test_add_excitation_circuit_trotter1_jw(self) -> None:
        n_spin_orbitals = 4
        excitation_indices = [(0, 2)]
        jw_mapper = jordan_wigner.get_of_operator_mapper()

        circuit = LinearMappedUnboundParametricQuantumCircuit(n_spin_orbitals)
        param = circuit.add_parameter("param")
        _add_excitation_circuit(
            circuit, excitation_indices, [param], jw_mapper, trotter_number=1
        )
        expected_circuit = LinearMappedUnboundParametricQuantumCircuit(n_spin_orbitals)
        param = expected_circuit.add_parameter("param")
        expected_circuit.add_ParametricPauliRotation_gate(
            (0, 1, 2), (2, 3, 1), {param: -1.0}
        )
        expected_circuit.add_ParametricPauliRotation_gate(
            (0, 1, 2), (1, 3, 2), {param: 1.0}
        )
        assert circuit.parameter_count == expected_circuit.parameter_count
        assert circuit._circuit.gates == expected_circuit._circuit.gates
        param_vals = [0.1 * (i + 1) for i in range(circuit.parameter_count)]
        bound_circuit = circuit.bind_parameters(param_vals)
        expected_bound_circuit = expected_circuit.bind_parameters(param_vals)
        assert bound_circuit == expected_bound_circuit

    def test_add_excitation_circuit_trotter2_jw(self) -> None:
        n_spin_orbitals = 4
        excitation_indices = [(0, 2)]
        jw_mapper = jordan_wigner.get_of_operator_mapper()
        circuit = LinearMappedUnboundParametricQuantumCircuit(n_spin_orbitals)
        param = circuit.add_parameter("param")
        _add_excitation_circuit(
            circuit, excitation_indices, [param], jw_mapper, trotter_number=2
        )
        expected_circuit = LinearMappedUnboundParametricQuantumCircuit(n_spin_orbitals)
        param = expected_circuit.add_parameter("param")
        expected_circuit.add_ParametricPauliRotation_gate(
            (0, 1, 2), (2, 3, 1), {param: -0.5}
        )
        expected_circuit.add_ParametricPauliRotation_gate(
            (0, 1, 2), (1, 3, 2), {param: 0.5}
        )
        assert circuit.parameter_count == expected_circuit.parameter_count
        assert circuit._circuit.gates == expected_circuit._circuit.gates
        param_vals = [0.1 * (i + 1) for i in range(circuit.parameter_count)]
        bound_circuit = circuit.bind_parameters(param_vals)
        expected_bound_circuit = expected_circuit.bind_parameters(param_vals)
        assert bound_circuit == expected_bound_circuit

    def test_add_excitation_circuit_trotter1_bk(self) -> None:
        n_spin_orbitals = 4
        excitation_indices = [(0, 2)]
        bk_mapper = bravyi_kitaev.get_of_operator_mapper()

        circuit = LinearMappedUnboundParametricQuantumCircuit(n_spin_orbitals)
        param = circuit.add_parameter("param")
        _add_excitation_circuit(
            circuit, excitation_indices, [param], bk_mapper, trotter_number=1
        )
        expected_circuit = LinearMappedUnboundParametricQuantumCircuit(n_spin_orbitals)
        param = expected_circuit.add_parameter("param")
        expected_circuit.add_ParametricPauliRotation_gate(
            (0, 1, 2), (1, 2, 1), {param: -1.0}
        )
        expected_circuit.add_ParametricPauliRotation_gate(
            (0, 1, 2), (2, 2, 2), {param: -1.0}
        )
        assert circuit.parameter_count == expected_circuit.parameter_count
        assert circuit._circuit.gates == expected_circuit._circuit.gates
        param_vals = [0.1 * (i + 1) for i in range(circuit.parameter_count)]
        bound_circuit = circuit.bind_parameters(param_vals)
        expected_bound_circuit = expected_circuit.bind_parameters(param_vals)
        assert bound_circuit == expected_bound_circuit

    def test_add_excitation_circuit_trotter1_scbk(self) -> None:
        n_spin_orbitals = 4
        excitation_indices = [(0, 2)]
        scbk_mapper = symmetry_conserving_bravyi_kitaev.get_of_operator_mapper(
            n_spin_orbitals, 2
        )

        n_qubits = symmetry_conserving_bravyi_kitaev.n_qubits_required(n_spin_orbitals)
        circuit = LinearMappedUnboundParametricQuantumCircuit(n_qubits)
        param = circuit.add_parameter("param")
        _add_excitation_circuit(circuit, excitation_indices, [param], scbk_mapper, 1)
        expected_circuit = LinearMappedUnboundParametricQuantumCircuit(n_qubits)
        param = expected_circuit.add_parameter("param")
        expected_circuit.add_ParametricPauliRotation_gate((0,), (2,), {param: -2.0})
        assert circuit.parameter_count == expected_circuit.parameter_count
        assert circuit._circuit.gates == expected_circuit._circuit.gates
        param_vals = [0.1 * (i + 1) for i in range(circuit.parameter_count)]
        bound_circuit = circuit.bind_parameters(param_vals)
        expected_bound_circuit = expected_circuit.bind_parameters(param_vals)
        assert bound_circuit == expected_bound_circuit

    def test_add_excitation_circuit_doubles(self) -> None:
        n_spin_orbitals = 6
        excitation_indices = [(0, 1, 4, 5)]
        jw_mapper = jordan_wigner.get_of_operator_mapper()

        circuit = LinearMappedUnboundParametricQuantumCircuit(n_spin_orbitals)
        param = circuit.add_parameter("param")
        _add_excitation_circuit(
            circuit, excitation_indices, [param], jw_mapper, trotter_number=1
        )
        expected_circuit = LinearMappedUnboundParametricQuantumCircuit(n_spin_orbitals)
        param = expected_circuit.add_parameter("param")
        expected_circuit.add_ParametricPauliRotation_gate(
            (0, 1, 5, 4), (1, 1, 1, 2), {param: -0.25}
        )
        expected_circuit.add_ParametricPauliRotation_gate(
            (0, 1, 5, 4), (2, 2, 1, 2), {param: 0.25}
        )
        expected_circuit.add_ParametricPauliRotation_gate(
            (1, 0, 4, 5), (1, 2, 1, 1), {param: 0.25}
        )
        expected_circuit.add_ParametricPauliRotation_gate(
            (0, 1, 4, 5), (1, 2, 1, 1), {param: 0.25}
        )
        expected_circuit.add_ParametricPauliRotation_gate(
            (1, 0, 4, 5), (1, 2, 2, 2), {param: -0.25}
        )
        expected_circuit.add_ParametricPauliRotation_gate(
            (0, 1, 4, 5), (1, 2, 2, 2), {param: -0.25}
        )
        expected_circuit.add_ParametricPauliRotation_gate(
            (0, 1, 4, 5), (1, 1, 1, 2), {param: -0.25}
        )
        expected_circuit.add_ParametricPauliRotation_gate(
            (0, 1, 4, 5), (2, 2, 1, 2), {param: 0.25}
        )
        assert circuit.parameter_count == expected_circuit.parameter_count
        assert circuit._circuit.gates == expected_circuit._circuit.gates
        param_vals = [0.1 * (i + 1) for i in range(circuit.parameter_count)]
        bound_circuit = circuit.bind_parameters(param_vals)
        expected_bound_circuit = expected_circuit.bind_parameters(param_vals)
        assert bound_circuit == expected_bound_circuit


class TestConstructCircuit:
    def test_construct_circuit_w_singles_trotter1(self) -> None:
        n_spin_orbitals = 4
        n_electrons = 2
        fermion_qubit_mapping = jordan_wigner
        trotter_number = 1
        use_singles = True

        circuit = _construct_circuit(
            n_spin_orbitals,
            n_electrons,
            fermion_qubit_mapping,
            trotter_number,
            use_singles,
        )
        expected_circuit = LinearMappedUnboundParametricQuantumCircuit(n_spin_orbitals)
        params = expected_circuit.add_parameters("param1", "param2", "param3")
        op_mapper = fermion_qubit_mapping.get_of_operator_mapper()
        s_excs, d_excs = excitations(n_spin_orbitals, n_electrons)
        _add_excitation_circuit(
            expected_circuit, d_excs, [params[-1]], op_mapper, trotter_number
        )
        _add_excitation_circuit(
            expected_circuit, s_excs, params[:-1], op_mapper, trotter_number
        )
        assert circuit.parameter_count == expected_circuit.parameter_count
        assert circuit._circuit.gates == expected_circuit._circuit.gates
        param_vals = [0.1 * (i + 1) for i in range(circuit.parameter_count)]
        bound_circuit = circuit.bind_parameters(param_vals)
        expected_bound_circuit = expected_circuit.bind_parameters(param_vals)
        assert bound_circuit == expected_bound_circuit

    def test_construct_circuit_wo_singles_trotter1(self) -> None:
        n_spin_orbitals = 4
        n_electrons = 2
        fermion_qubit_mapping = jordan_wigner
        trotter_number = 1
        use_singles = False

        circuit = _construct_circuit(
            n_spin_orbitals,
            n_electrons,
            fermion_qubit_mapping,
            trotter_number,
            use_singles,
        )
        expected_circuit = LinearMappedUnboundParametricQuantumCircuit(n_spin_orbitals)
        param = expected_circuit.add_parameter("param")
        op_mapper = fermion_qubit_mapping.get_of_operator_mapper()
        _, d_excs = excitations(n_spin_orbitals, n_electrons)
        _add_excitation_circuit(
            expected_circuit, d_excs, [param], op_mapper, trotter_number
        )
        assert circuit.parameter_count == expected_circuit.parameter_count
        assert circuit._circuit.gates == expected_circuit._circuit.gates
        param_vals = [0.1 * (i + 1) for i in range(circuit.parameter_count)]
        bound_circuit = circuit.bind_parameters(param_vals)
        expected_bound_circuit = expected_circuit.bind_parameters(param_vals)
        assert bound_circuit == expected_bound_circuit

    def test_construct_circuit_w_singles_trotter2_scbk(self) -> None:
        n_spin_orbitals = 4
        n_electrons = 2
        fermion_qubit_mapping = symmetry_conserving_bravyi_kitaev
        use_singles = True
        trotter_number = 2

        circuit = _construct_circuit(
            n_spin_orbitals,
            n_electrons,
            fermion_qubit_mapping,
            trotter_number,
            use_singles,
        )
        n_qubits = fermion_qubit_mapping.n_qubits_required(n_spin_orbitals)
        op_mapper = fermion_qubit_mapping.get_of_operator_mapper(
            n_spin_orbitals, n_electrons
        )
        expected_circuit = LinearMappedUnboundParametricQuantumCircuit(n_qubits)
        params = expected_circuit.add_parameters("param1", "param2", "param3")
        s_excs, d_excs = excitations(n_spin_orbitals, n_electrons)
        _add_excitation_circuit(
            expected_circuit, d_excs, [params[-1]], op_mapper, trotter_number
        )
        _add_excitation_circuit(
            expected_circuit, s_excs, params[:-1], op_mapper, trotter_number
        )
        _add_excitation_circuit(
            expected_circuit, d_excs, [params[-1]], op_mapper, trotter_number
        )
        _add_excitation_circuit(
            expected_circuit, s_excs, params[:-1], op_mapper, trotter_number
        )
        assert circuit.parameter_count == expected_circuit.parameter_count
        assert circuit._circuit.gates == expected_circuit._circuit.gates
        param_vals = [0.1 * (i + 1) for i in range(circuit.parameter_count)]
        bound_circuit = circuit.bind_parameters(param_vals)
        expected_bound_circuit = expected_circuit.bind_parameters(param_vals)
        assert bound_circuit == expected_bound_circuit


class TestTrotterSingletUCCSD:
    def test_trotter_singlet_uccsd_w_singles_jw(self) -> None:
        n_spin_orbitals = 4
        n_electrons = 2
        trotter_number = 1
        ansatz = TrotterSingletUCCSD(
            n_spin_orbitals, n_electrons, trotter_number=trotter_number
        )
        expected_ansatz = _construct_circuit(
            n_spin_orbitals,
            n_electrons,
            jordan_wigner,
            trotter_number=trotter_number,
            use_singles=True,
        )
        assert ansatz.parameter_count == expected_ansatz.parameter_count
        assert ansatz._circuit.gates == expected_ansatz._circuit.gates
        param_vals = [0.1 * (i + 1) for i in range(ansatz.parameter_count)]
        bound_ansatz = ansatz.bind_parameters(param_vals)
        expected_bound_ansatz = expected_ansatz.bind_parameters(param_vals)
        assert bound_ansatz == expected_bound_ansatz

    def test_trotter_singlet_uccsd_wo_singles_bk(self) -> None:
        n_spin_orbitals = 4
        n_electrons = 2
        trotter_number = 1
        ansatz = TrotterSingletUCCSD(
            n_spin_orbitals,
            n_electrons,
            bravyi_kitaev,
            trotter_number=trotter_number,
            use_singles=False,
        )
        expected_ansatz = _construct_circuit(
            n_spin_orbitals,
            n_electrons,
            bravyi_kitaev,
            trotter_number=trotter_number,
            use_singles=False,
        )
        assert ansatz.parameter_count == expected_ansatz.parameter_count
        assert ansatz._circuit.gates == expected_ansatz._circuit.gates
        param_vals = [0.1 * (i + 1) for i in range(ansatz.parameter_count)]
        bound_ansatz = ansatz.bind_parameters(param_vals)
        expected_bound_ansatz = expected_ansatz.bind_parameters(param_vals)
        assert bound_ansatz == expected_bound_ansatz

    def test_trotter_singlet_uccsd_scbk_trotter2(self) -> None:
        n_spin_orbitals = 4
        n_electrons = 2
        trotter_number = 2
        ansatz = TrotterSingletUCCSD(
            n_spin_orbitals,
            n_electrons,
            symmetry_conserving_bravyi_kitaev,
            trotter_number=trotter_number,
        )
        expected_ansatz = _construct_circuit(
            n_spin_orbitals,
            n_electrons,
            symmetry_conserving_bravyi_kitaev,
            trotter_number=trotter_number,
            use_singles=True,
        )
        assert ansatz.parameter_count == expected_ansatz.parameter_count
        assert ansatz._circuit.gates == expected_ansatz._circuit.gates
        param_vals = [0.1 * (i + 1) for i in range(ansatz.parameter_count)]
        bound_ansatz = ansatz.bind_parameters(param_vals)
        expected_bound_ansatz = expected_ansatz.bind_parameters(param_vals)
        assert bound_ansatz == expected_bound_ansatz

    def test_singlet_uccsd_invalid_input(self) -> None:
        with pytest.raises(ValueError):
            TrotterSingletUCCSD(4, 3)
        with pytest.raises(ValueError):
            TrotterSingletUCCSD(4, 4)