from dataclasses import dataclass, field
from typing import Optional


@dataclass
class FmuVariable:
    name: str
    value_reference: int
    causality: str
    variability: str = ""
    data_type: str = ""
    unit: str = ""
    start_value: Optional[float] = None
    description: str = ""

@dataclass
class FmuModel:
    """
    Represents a single loaded FMU and its metadata.
    """
    fmu_id: str  # unique identifier used internally (e.g. filepath or UUID)
    file_path: str  # path to the .fmu file on disk
    model_name: str = ""  # human-readable model name from modelDescription.xml
    fmi_version: str = ""  # e.g. "2.0", "3.0"
    variables: list = field(default_factory=list)  # list[FMUVariable]

class FmuManager:
    """
    Manages the lifecycle of FMUs loaded into the application.
    """

    def __init__(self):
        # Internal registry of loaded FMUs, keyed by fmu_id.
        self._loaded_fmus: dict[str, FmuModel] = {}

    def load_fmu(self, file_path: str) -> FmuModel:
        pass