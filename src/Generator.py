from abc import ABC, abstractmethod
from json import dumps
from llm_sdk import Small_LLM_Model
from re import compile
from typing import Any, List, Tuple
from .Answer import Answer
from .Function import Function
from .Prompt import Prompt


class Generator:
    """Class that allow to generate answers from prompts

    Methods
    -------
    generate(prompt) -> Answer
        Generate an answer for a given prompt
    """

    class Processor(ABC):
        """Base class for generate data with the LLM

        Methods
        -------
        generate(llm, answer) -> str
            Generate the next value of the answer
        convert(s) -> Any
            Convert a string to the processor data type
        """

        def generate(self, llm: Small_LLM_Model, answer: Answer) -> str:
            """Generate the next value of the answer

            Parameters
            ----------
            llm : Small_LLM_Model
                The llm to use
            answer : Answer
                The answer

            Returns
            -------
            str
                The generated value
            """

            if len(answer.args) == 0:
                data = answer.model_dump()
                del data["args"]
                s = dumps(data)
            else:
                s = answer.model_dump_json()
            while s[-1] == '}':
                s = s[:-1]
            if s[-1] == '"':
                s = s[:-1]
            res = ""
            finished = False
            while not finished:
                res, finished = self._predicate(llm, s + res, res)
            return res

        def _predicate(self, llm: Small_LLM_Model, input: str,
                       current: str | None) -> Tuple[str, bool]:
            if current is None:
                current = ""
            input_ids = llm._encode(input).squeeze(0).tolist()
            logits = llm.get_logits_from_input_ids(input_ids)
            best_logit = float("-inf")
            best_consumed = None
            best_finished = False
            for token, logit in enumerate(logits):
                if logit > best_logit:
                    consumed, finished = self._validate(current,
                                                        llm._decode([token]))
                    if consumed is not None:
                        best_logit = logit
                        best_consumed = consumed
                        best_finished = finished
            if best_consumed is None:
                raise RuntimeError("no valid token found")
            return current + best_consumed, best_finished

        @abstractmethod
        def _validate(self, current: str,
                      to_add: str) -> Tuple[str | None, bool]:
            ...

        @abstractmethod
        def convert(self, s: str) -> Any:
            ...

    class NameProcessor(Processor):
        """Processor that handle limited list of possible strings

        Methods
        -------
        convert(s) -> Any
            Convert a string to the processor data type
        """

        def __init__(self, availables: List[str]) -> None:
            """
            Parameters
            ----------
            availables : List[str]
                The availables strings
            """

            self._availables = availables

        def _validate(self, current: str,
                      to_add: str) -> Tuple[str | None, bool]:
            if len(to_add) == 0:
                return None, False
            current = current + to_add
            if current in self._availables:
                return to_add, True
            for s in self._availables:
                if s.startswith(current):
                    return to_add, False
            return None, False

        def convert(self, s: str) -> Any:
            return s

    class BoolProcessor(NameProcessor):
        """Processor that handle booleans

        Methods
        -------
        convert(s) -> Any
            Convert a string to the processor data type
        """

        def __init__(self) -> None:
            super().__init__(["false", "true"])

        def convert(self, s: str) -> Any:
            return s == "true"

    class RegexProcessor(Processor, ABC):
        """Base class for processors which use Regex"""

        _REGEX = compile(r"")

        def _validate(self, current: str,
                      to_add: str) -> Tuple[str | None, bool]:
            if len(to_add) == 0:
                return None, False
            s = current + to_add
            m = self._REGEX.match(s)
            if m is None:
                return None, False
            return to_add[:m.end() - len(current)], m.end() < len(s)

    class FloatProcessor(RegexProcessor):
        """Processor that handle floats

        Methods
        -------
        convert(s) -> Any
            Convert a string to the processor data type
        """

        _REGEX = compile(r"^-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?")

        def convert(self, s: str) -> Any:
            return float(s)

    class IntProcessor(RegexProcessor):
        """Processor that handle integers

        Methods
        -------
        convert(s) -> Any
            Convert a string to the processor data type
        """

        _REGEX = compile(r"^-?(0|[1-9]\d*)")

        def convert(self, s: str) -> Any:
            return int(s)

    class StrProcessor(RegexProcessor):
        """Processor that handle strings

        Methods
        -------
        convert(s) -> Any
            Convert a string to the processor data type
        """

        _REGEX = compile(r'^[^"\}\n,]*')

        def convert(self, s: str) -> Any:
            return s

    def __init__(self, functions: List[Function]) -> None:
        """
        Parameters
        ----------
        functions : List[Function]
            A list of available functions
        """

        self._functions = functions
        self._llm = Small_LLM_Model()

    def generate(self, prompt: Prompt) -> Answer:
        """Generate an answer for a given prompt

        Parameters
        ----------
        prompt : Prompt
            The prompt

        Returns
        -------
        Answer
            The answer
        """

        answer = Answer(prompt=prompt.prompt, fn_name="", args={})
        fn_names = [function.fn_name for function in self._functions]
        answer.fn_name = Generator.NameProcessor(fn_names).generate(
            self._llm, answer)
        function = self._functions[fn_names.index(answer.fn_name)]
        for arg in function.args_names:
            answer.args[arg] = ""
            processor: Generator.Processor = {
                "bool": Generator.BoolProcessor(),
                "float": Generator.FloatProcessor(),
                "int": Generator.IntProcessor(),
                "str": Generator.StrProcessor(),
            }[function.args_types[arg]]
            answer.args[arg] = processor.convert(processor.generate(
                self._llm, answer))
        return answer
