ROL_MODEL = "rol-model/"
LEVELS = "levels/"


def create_context(
    selected_english_level: str, user_name: str, user_message: str, model: str
) -> str:
    """
    Creates the full context for Gemini

    Parameters:
        selected_english_level (str): The selected English level of the user.
        user_name (str): The name of the user.
        user_message (str): The message of the user.
        model (str): The model used for processing the message.

    Returns:
        str: The full context for Gemini.
    """
    rol_english_level = read_level_file(selected_english_level)
    model_context = read_rol_model(model)

    if model == "pro":
        return f"{rol_english_level} {model_context}the user named {user_name}, says: '{user_message}'"
    elif model == "pro_vision":
        return f"{rol_english_level} {model_context}the user named {user_name} shares the image: {user_message}"

    else:
        print(f"Model not found: {model}, try 'pro' or 'pro_vision'")
        return ""


def read_level_file(selected_english_level: str) -> str:
    """
    Reads the content of a level file for the selected English level.

    Args:
        selected_english_level (str): The selected English level.

    Returns:
        str: The content of the level file.
    """
    level_path = f"{LEVELS}{selected_english_level}.txt"
    try:
        with open(level_path, "r") as file:
            return file.read()
    except FileNotFoundError as e:
        print(f"Error reading level file: {e}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None


def read_rol_model(role: str) -> str:
    """
    Reads the content of a Gemini's role model file.
    (gemini pro or gemini pro vision)

    Args:
        role (str): The name of the Gemini's role model.
        "pro" or "pro_vision"

    Returns:
        str: The content of the Gemini's role model file.
    """
    role_path = f"{ROL_MODEL}{role}.txt"
    try:
        with open(role_path, "r") as file:
            return file.read()
    except FileNotFoundError as e:
        print(f"Error reading role model: {e}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None
