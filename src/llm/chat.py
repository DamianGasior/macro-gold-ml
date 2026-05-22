import logging

logger = logging.getLogger(__name__)


class Chat_history:
    def __init__(self):
        # self._saved_chats = {}
        self._conv_in_list = []

    # def expand_chat(self, key, value):

    #     self._saved_chats[key] = value
    #     logger.debug(f"'key' to : {key}, a 'value' to {value}")
    #     self.list_expansion(self._saved_chats)
    #     return self._saved_chats

    def list_expansion(self, item):
        self._conv_in_list.append(item)
        logger.debug(f"dlugosic list to {len(self._conv_in_list)}")
        return self._conv_in_list

    # @property
    # def users_input_text_validation(self):
    #     #dopisac tu tylko walidacje i bedzie gralo

    # @property
    # def return_dict_chat_history(self):
    #     for key, value in self._saved_chats.items():
    #         logger.debug(f"klucz to : {key}, a value to {value}")
    #     return self._saved_chats

    @property
    def return_list_chat_history(self):
        logger.debug(f"===========dlugosc list to=======\n : {len(self._conv_in_list)}")
        for i in self._conv_in_list:
            logger.debug(i)
        return self._conv_in_list
