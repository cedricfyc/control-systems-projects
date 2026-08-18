from dataclasses import dataclass, field
from typing import Optional

from .simulation_engine import SimulationConfig

@dataclass
class Project:
    name: str = "Untitled Project"
    file_path: Optional[str] = None
    # default_factory ensures each instance gets a fresh copy rather than sharing a single object
    fmu_file_paths: list = field(default_factory=list)
    simulation_config: SimulationConfig = field(default_factory=SimulationConfig)
    is_modified: bool = False

    def mark_modified(self) -> None:
        """Marks unsaved changes before closing"""
        self.is_modified = True

class ProjectManager:
    def __init__(self):
        self.current_project: Project = Project()

    def new_project(self) -> Project:
        """Overwrite current project with new project"""
        self.current_project: Project = Project()
        return self.current_project

    def save_project(self, file_path: str) -> None:
        """
        Serialize self.current_project to disk.

        TODO: Implement serialization, e.g. to JSON:
              - Convert dataclasses to dict (dataclasses.asdict).
              - Write to file_path.
              - Update self.current_project.file_path and is_modified.
        """
        raise NotImplementedError

    def load_project(self, file_path: str) -> Project:
        """
        Load a project file from disk and set it as the current project.

        TODO: Implement deserialization matching save_project's format.
        """
        raise NotImplementedError