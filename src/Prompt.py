from pydantic import Field
from .Data import Data


class Prompt(Data):
    """Model that represent a prompt

    Attributes
    ----------
    prompt : str
        The prompt
    """

    prompt: str = Field()
