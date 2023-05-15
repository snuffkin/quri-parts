from dataclasses import dataclass
from typing import Optional, Sequence, TypeVar, Union, cast

import numpy as np

from quri_parts.circuit import LinearParameterMapping
from quri_parts.circuit.parameter_shift import ShiftedParameters
from quri_parts.core.estimator import (
    ConcurrentParametricQuantumEstimator,
    Estimatable,
    HessianEstimator,
    MatrixEstimates,
)
from quri_parts.core.state import (
    ParametricCircuitQuantumState,
    ParametricQuantumStateVector,
)

_ParametricStateT = TypeVar(
    "_ParametricStateT",
    bound=Union[ParametricCircuitQuantumState, ParametricQuantumStateVector],
)


@dataclass
class _MatrixEstimates:
    values: Sequence[Sequence[complex]]
    error_tensor: Optional[Sequence[Sequence[Sequence[Sequence[float]]]]]


def parameter_shift_hessian_estimates(
    op: Estimatable,
    state: _ParametricStateT,
    params: Sequence[float],
    estimator: ConcurrentParametricQuantumEstimator[_ParametricStateT],
) -> MatrixEstimates[complex]:
    # Function that returns energy hessian w.r.t. circuit parameters using
    # parameter shift rule
    param_circuit = state.parametric_circuit
    param_mapping = cast(LinearParameterMapping, param_circuit.param_mapping)
    parameter_shift = ShiftedParameters(param_mapping)
    derivatives = [
        derivs_i.get_derivatives() for derivs_i in parameter_shift.get_derivatives()
    ]
    shifted_params_and_coeffs_list = [
        [deriv.get_shifted_parameters_and_coef(params) for deriv in derivs]
        for derivs in derivatives
    ]
    raw_param_state = cast(_ParametricStateT, state.with_primitive_circuit())
    uniq_g_params = set()
    for shifted_params_and_coeffs in shifted_params_and_coeffs_list:
        for params_and_coefs in shifted_params_and_coeffs:
            for p, _ in params_and_coefs:
                uniq_g_params.add(p)
    uniq_g_params_list = list(uniq_g_params)

    # Estimate the expectation values
    estimates = estimator(op, raw_param_state, uniq_g_params_list)
    estimates_dict = dict(zip(uniq_g_params_list, estimates))

    # Sum up the expectation values with the coefficients multiplied
    hessian = np.zeros((len(derivatives), len(derivatives)))
    for i in range(len(derivatives)):
        for j in range(len(derivatives)):
            g = 0.0
            for p, c in shifted_params_and_coeffs_list[i][j]:
                g += estimates_dict[p].value.real * c
            hessian[i, j] = g

    return _MatrixEstimates(cast(list[list[complex]], hessian), None)


def create_parameter_shift_hessian_estimator(
    parametric_estimator: ConcurrentParametricQuantumEstimator[_ParametricStateT],
) -> HessianEstimator[_ParametricStateT]:
    def estimator(
        operator: Estimatable, state: _ParametricStateT, params: Sequence[float]
    ) -> MatrixEstimates[complex]:
        return parameter_shift_hessian_estimates(
            operator, state, params, parametric_estimator
        )

    return estimator
