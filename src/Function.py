from __future__ import annotations
from pydantic import Field, model_validator
from typing import Dict, List
from .Data import Data, DataType, SnakeCaseStr


class Function(Data):
    """Model that represent a fonction

    Attributes
    ----------
    fn_name : SnakeCaseStr
        The name of the function
    args_names : List[SnakeCaseStr]
        The list of arguments for the function
    args_types : Dict[SnakeCaseStr, DataType]
        The types of each arguments in format {argument_name: type}
    return_type : DataType
        The function type of return
    """

    fn_name: SnakeCaseStr = Field(min_length=1)
    args_names: List[SnakeCaseStr] = Field()
    args_types: Dict[SnakeCaseStr, DataType] = Field()
    return_type: DataType = Field()

    @model_validator(mode="after")
    def check_function(self) -> Function:
        """Check the function validity

        Returns
        -------
        Function
            This Function
        """

        if len(self.args_names) != len(set(self.args_names)):
            raise ValueError("arguments must be unique")
        for arg in self.args_names:
            if len(arg) == 0:
                raise ValueError("arg name cannot be empty")
            if arg not in self.args_types:
                raise ValueError(f"type of arg '{arg}' must be defined in"
                                 + " args_types")
        for arg in self.args_types:
            if arg not in self.args_names:
                raise ValueError(f"arg '{arg}' not in args_names")
        return self
