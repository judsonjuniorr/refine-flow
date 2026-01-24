"""Input helpers for CLI."""

from prompt_toolkit import prompt
from prompt_toolkit.key_binding import KeyBindings


def get_multiline_input() -> str:
    """
    Get multi-line input from user.

    Returns:
        User input as string
    """
    print("Digite seu texto (Pressione ESC e depois Enter, ou Ctrl+D para finalizar):")

    bindings = KeyBindings()

    @bindings.add("escape", "enter")
    def _(event):  # type: ignore
        event.app.exit(result=event.app.current_buffer.text)

    try:
        result = prompt(
            "> ",
            multiline=True,
            key_bindings=bindings,
        )
        return result.strip()
    except (EOFError, KeyboardInterrupt):
        return ""
