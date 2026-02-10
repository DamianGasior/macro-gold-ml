from abc import ABC, abstractmethod

# thanks to abstrac class , methods needs to be implemented in each class, so we avoid a situation where a crucial class is missed


class BaseAPIProvider(ABC):
    def __init__(self, symbol: str):
        self.symbol = symbol
    # in the class __init__
    # include parametres required  by the api provider, like symbol, interval, api_key , etc

    @abstractmethod
    def to_dict_params(self) -> dict[str, str]:
        # an example what will be required in this, helpful to create  pass the details to requets.get(url,params=params)
        # params={"symbol": self.symbol,
        # "interval": self.interval,etc}
        pass

    @abstractmethod
    def api_request(self):
        # request itself to the api provider, it makes sense to build another new  method outside of the class
        # which can be later on cached by streamlit or other frameowrk
        # def api_request_cached(parameters):
        # include here requests.get(url, params=parameters)
        pass

    @abstractmethod
    def execute_full_request(self):
        # full request execution, an orchestrator within the specific file
        pass

    @abstractmethod
    def response_from_api(self):
        # important method, which is used to refer , pass the reposne ( hence caching is needed)
        # later to the next abstract class so called transformer
        pass

    @abstractmethod
    def to_dict(self):
        # method which will be not used always,  api response is build to a dict and passed when requested
        pass
