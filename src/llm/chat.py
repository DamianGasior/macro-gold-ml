import logging

logger = logging.getLogger(__name__)


class Chat_history:
    def __init__(self):
        self._saved_chats = {}
        self._conv_in_list = []

    def expand_chat_with_id(self, key):

        self._saved_chats[key] = self._conv_in_list
        logger.debug(f"'key' to : {key}, a 'value' to {self._conv_in_list}")

    def list_expansion(self, item):
        self._conv_in_list.append(item)
        logger.debug(f"dlugosic list to {len(self._conv_in_list)}")
        return self._conv_in_list

    def return_list_chat(self):
        logger.debug(f"self._conv_in_list is {self._conv_in_list}")
        logger.debug(f"self._conv_in_list type is: {type(self._conv_in_list)}")
        return self._conv_in_list

    def return_chat_history_based_on_id(self, key):
        conv_hisotry = self._saved_chats[key]
        return conv_hisotry

    def return_list_chat_history(self):
        logger.debug(f"===========dlugosc list to=======\n : {len(self._conv_in_list)}")
        for i in self._conv_in_list:
            logger.debug(i)
        return self._conv_in_list
