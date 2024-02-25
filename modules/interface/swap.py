import abc

from modules.starknet import Starknet


class SwapInterface(Starknet, metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return hasattr(subclass, "swap") and callable(subclass.swap)

    @abc.abstractmethod
    async def swap(self,
             from_token: str,
             to_token: str,
             min_amount: float,
             max_amount: float,
             decimal: int,
             slippage: float,
             all_amount: bool,
             min_percent: int,
             max_percent: int) -> None:
        """Swap tokens"""
        raise NotImplementedError
