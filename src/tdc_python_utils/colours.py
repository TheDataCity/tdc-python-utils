from colorama import Fore, Style, init

init(autoreset=True)

colors = {
        "red": Fore.RED,
        "green": Fore.GREEN,
        "yellow": Fore.YELLOW,
        "blue": Fore.BLUE,
        "magenta": Fore.MAGENTA,
        "cyan": Fore.CYAN,
        "white": Fore.WHITE
    }

def highlight_text(message:str, text:str, color:str = "cyan"):
    """Return `message` with all occurrences of `text` wrapped in ANSI
    colour codes.

    Parameters
    ----------
    message : str
        The full message in which to highlight `text`.
    text : str
        The substring to highlight. Matching is literal and case-sensitive.
    color : str, optional
        Name of the colour to use (default ``"cyan"``). Supported values
        are: red, green, yellow, blue, magenta, cyan, white.

    Returns
    -------
    str
        A new string where every occurrence of `text` is wrapped with the
        corresponding ANSI colour code and a reset code.

    Notes
    -----
    The function coerces inputs to strings before matching. If the
    specified colour is not found the terminal default (no colour) is
    used.
    """
    message = str(message)
    text = str(text)
    
    color_code = colors.get(color.lower(), Fore.RESET)
    return message.replace(text, f"{color_code}{text}{Style.RESET_ALL}")

def highlight_all(message:str, color:str = "cyan"):
    color_code = colors.get(color.lower(), Fore.RESET)
    return message.replace(message, f"{color_code}{message}{Style.RESET_ALL}")