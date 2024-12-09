from pydantic import dataclasses, computed_field

@dataclasses
class Script_File():
    file_path: str

    @computed_field
    @property
    def file_content(self)->str:
        with open(self.file_path, 'r') as f:
            return f.read()