from abc import ABC
from json import dump, load
from pydantic import BaseModel, StringConstraints
from typing import Annotated, List, Literal
from typing_extensions import Self

DataType = Literal["bool", "float", "int", "str"]
SnakeCaseStr = Annotated[str, StringConstraints(pattern=r"^[a-z_]*$")]


class Data(BaseModel, ABC):
    """Base model for data objets manipulated in the project

    Class Methods
    -------------
    from_file(path) -> List[Self]
        Opens a JSON file containing a list of objects of the class
    to_file(path, data) -> None
        Write a list of objects of the class into a JSON file
    """

    class Config:
        extra = "forbid"

    @classmethod
    def from_file(cls, path: str) -> List[Self]:
        """Opens a JSON file containing a list of objects of the class

        Parameters
        ----------
        path : str
            The path of the file

        Returns
        -------
        List[Self]
            The objects read
        """

        with open(path, encoding="utf8") as file:
            return [cls(**data) for data in load(file)]

    @classmethod
    def to_file(cls, path: str, data: List[Self]) -> None:
        """Write a list of objects of the class into a JSON file

        Parameters
        ----------
        path : str
            The path of the file
        data : List[Self]
            The objects to write
        """

        with open(path, "w", encoding="utf8") as file:
            dump([e.model_dump() for e in data], file, indent=4)
