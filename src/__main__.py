from argparse import ArgumentParser
from os import makedirs
from sys import stderr
from .Answer import Answer
from .Function import Function
from .Generator import Generator
from .Prompt import Prompt


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--functions_definition",
                        default="data/input/functions_definition.json")
    parser.add_argument("--input",
                        default="data/input/function_calling_tests.json")
    parser.add_argument("--output",
                        default="data/output/function_calling_output.json")
    args = parser.parse_args()
    try:
        functions = Function.from_file(args.functions_definition)
        prompts = Prompt.from_file(args.input)
        generator = Generator(functions)
        makedirs(args.output, exist_ok=True)
        Answer.to_file(args.output, [generator.generate(prompt)
                                     for prompt in prompts])
    except KeyboardInterrupt:
        stderr.write("Interrupted\n")
        exit(1)
    except Exception as e:
        stderr.write(f"Error: {e}\n")
        exit(1)
