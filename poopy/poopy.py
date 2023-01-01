from core.constant import PROMPT, INTRO, OUTRO, OOPSIE_POOPSIE
from core.run import Run
from argparse import ArgumentParser

from prompt_toolkit import prompt
from prompt_toolkit.styles import Style

poop_style = Style.from_dict({
    "rprompt": "bg:#A08679 #ffffff",
})
def get_poop_prompt():
    return f"\U0001F4A9poopy\U0001F4A9"

parser = ArgumentParser()
parser.add_argument("--file", required= False)
args = parser.parse_args()

if args.file:
    file = args.file

    with open(file, "r") as f:
        text = f.read()

    try:
        result, error = Run().run(file, text, mode = "File")
        if error:
            print(error.as_string())
        elif result !=" ":
            print(repr(result)) 
    except Exception as e:
        print(e)
        print(OOPSIE_POOPSIE)

if not args.file:
    print(INTRO)
    try:
        while True:
            text = prompt(PROMPT, rprompt=get_poop_prompt, style=poop_style)
            if text == "":
                continue
            result, error = Run().run("<STD_IN>", text, mode="Terminal")
            if error:
                print(error.as_string())
            elif result !="None":
                print(repr(result))
    except KeyboardInterrupt:
        print(OUTRO)
    except Exception as e:
        print(e)
        print(OOPSIE_POOPSIE)
