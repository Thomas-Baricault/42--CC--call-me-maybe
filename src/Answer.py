from pydantic import Field
from typing import Any, Dict
from .Data import Data, SnakeCaseStr


class Answer(Data):
    """Model that represent an answer

    Attributes
    ----------
    prompt : str
        The prompt
    fn_name : SnakeCaseStr
        The name of the fonction to use
    args : Dict[SnakeCaseStr, Any]
        The arguments to use in format {arg_name: value}
    """

    prompt: str = Field()
    fn_name: SnakeCaseStr = Field()
    args: Dict[SnakeCaseStr, Any]
