from enum import Enum
from app.localization import localization, get_text

class ErrorCode(Enum):
    NOT_FOUND = "not_found"
    INVALID_ITEM = "invalid_name"
    TIMEOUT = "timeout"
    JSON_DECODE_ERROR = "json_decode_error"
    INVALID_GAME = "invalid_game"
    ITEM_EXISTS = "item_exists"
    USER_NOT_FOUND = "user_not_found"
    EMPTY_FAVORITE = "empty_favorite"


ERROR_MESSAGES = {
    ErrorCode.NOT_FOUND: "Hmm, I couldn't find that item. Maybe it's from a different game? Double-check and give it another go!",
    ErrorCode.INVALID_ITEM: "It looks like I couldn't find that item. Could you check the details and try again?",
    ErrorCode.INVALID_GAME: "Oops! That item seems to belong to another game. Please try searching for it in the right one.",
    ErrorCode.TIMEOUT: "Sorry, it’s taking too long to respond. Please try again in a bit!",
    ErrorCode.JSON_DECODE_ERROR: "Oops, something went wrong while processing the data. Try again soon!",
    ErrorCode.ITEM_EXISTS: "🙃 This item is already in your favorites list. No need to add it again!",
    ErrorCode.USER_NOT_FOUND: "Hmm, I couldn't find that user. Maybe double-check the ID?",
    ErrorCode.EMPTY_FAVORITE: f"*Your favorites list is currently empty.*\n Add some items to track them!",
}


def get_error_message(error_code, **kwargs):
    message = ERROR_MESSAGES.get(error_code, "An unknown error occurred.")
    return message.format(**kwargs)
