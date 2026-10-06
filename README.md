*This project has been created as part of the curriculum by tbaricau*

# call me maybe

## Description

The goal of this project is to create a program that take a file containing prompts and use a given LLM to generate a structured JSON that give informations to call a specific function.

To do that, we will use constrained decoding.

For example if the given prompt is ``Substitute the digits in the string 'Hello 34 I'm 233 years old' with 'NUMBERS'``, the output could be:
```JSON
{
    "prompt": "Substitute the digits in the string 'Hello 34 I'm 233 years old' with 'NUMBERS'",
    "fn_name": "fn_substitute_string_with_regex",
    "args": {
        "source_string": "Hello 34 I'm 233 years old",
        "regex": "/[0-9]+/g",
        "replacement": "NUMBERS"
    }
}
```

## Features

- Custom input file
- Custom output file

## Instructions

Install all the dependencies
```Shell
make install
```

Enter the virtual environment
```Shell
source .venv/bin/activate
```

Run using the default input and output files
```Shell
make run
```

Run using custom input and output files
```Shell
uv run python -m src [--input <input_file>] [--output <output_file>]
```

Run in debug mode
```Shell
make debug
```

Clean cached files
```Shell
make clean
```

Check the norm and the typing
```Shell
make lint
make lint-strict
```

## Resources

I use AI to get some guidance on how to orient the constraint decoding.

## Algorithm explanation

To garantee valid JSON, we need to contrain the decoding process. So at each decoding step, we only keep logits that don't break the JSON structure and the needed format.

For example, to generate the name of the function to use, we will give to the model the incomplete JSON like that:
```JSON
{"prompt": "Reverse the string 'hello'","fn_name": "fn_re
```
And then we only keep logits that build an existant function name.

## Design decisions

I choose to represent each type of data we extract or we write into a pydantic model.

I create a Generator class to encapsulate the entire generation process.

To validate tokens for float, int or strings I use regular expressions because they offer a certain level of reliability and allow for concise code.

## Performance analysis

With the test set, I get an accuracy of 80%. Even when the model doesn't choose the correct function, the rest of the generation process still follows the expected path, even if the result isn't quite right.

The generation process is rather slow, but it depends on the host machine; I've tried to optimize it as much as possible.

## Challenges faced

The biggest difficulty was finding the correct format to provide the JSON to the model in order to obtain a consistent result. I tried with different variations (providing the complete JSON but with the values ​​to be completed set to null, truncating the end of the JSON, etc...).

A second difficulty was the code for selecting valid tokens, and I finally succeeded thanks to regex.

## Testing strategy

I validate my implementation with the testing set.

## Example usage

In ``data/input`` you need to have the following 2 files:

``functions_definition.json``, a file that contains a list a function definitions
```JSON
[
    {
        "fn_name": "fn_add_numbers",
        "args_names": [
            "a",
            "b"
        ],
        "args_types": {
            "a": "float",
            "b": "float"
        },
        "return_type": "float"
    },
    {
        "fn_name": "fn_get_square_root",
        "args_names": [
            "a"
        ],
        "args_types": {
            "a": "float"
        },
        "return_type": "float"
    },
...
]
```

``function_calling_tests.json``, a list of prompt to process
```JSON
[
    {
        "prompt": "Reverse the string 'hello'"
    },
    {
        "prompt": "Reverse the string 'world'"
    },
    {
        "prompt": "Substitute the digits in the string 'Hello 34 I'm 233 years old' with 'NUMBERS'"
    },
...
]
```

Then run the program with ``make run``. After few time of processing, you will have a new file in ``data/output`` formatted as follow:

``function_calling_output.json``
```JSON
[
    {
        "prompt": "Reverse the string 'hello'",
        "fn_name": "fn_reverse_string",
        "args": {
            "s": "hello"
        }
    },
    {
        "prompt": "Reverse the string 'world'",
        "fn_name": "fn_reverse_string",
        "args": {
            "s": "world"
        }
    },
    {
        "prompt": "Substitute the digits in the string 'Hello 34 I'm 233 years old' with 'NUMBERS'",
        "fn_name": "fn_substitute_string_with_regex",
        "args": {
            "source_string": "Hello 34 I'm 233 years old",
            "regex": "/[0-9]+/g",
            "replacement": "NUMBERS"
        }
    },
...
]
```
