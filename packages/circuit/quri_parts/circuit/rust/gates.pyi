from .gate import QuantumGate

def X(target_index: int) -> QuantumGate: ...
def Y(target_index: int) -> QuantumGate: ...
def Z(target_index: int) -> QuantumGate: ...
def H(target_index: int) -> QuantumGate: ...
def S(target_index: int) -> QuantumGate: ...
def Sdag(target_index: int) -> QuantumGate: ...
def SqrtX(target_index: int) -> QuantumGate: ...
def SqrtXdag(target_index: int) -> QuantumGate: ...
def SqrtY(target_index: int) -> QuantumGate: ...
def SqrtYdag(target_index: int) -> QuantumGate: ...
def T(target_index: int) -> QuantumGate: ...
def Tdag(target_index: int) -> QuantumGate: ...
