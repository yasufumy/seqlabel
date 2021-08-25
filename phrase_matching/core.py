from abc import abstractmethod
from dataclasses import dataclass
from typing import Iterator, List, Tuple, Union

from tokenizations import get_alignments


class StringSequence:
    @abstractmethod
    def validate_offset(self, start_offset: int, end_offset: int) -> bool:
        pass

    @abstractmethod
    def align_offset(self, start_offset: int, end_offset: int) -> Tuple[int, int]:
        pass

    def __repr__(self) -> str:
        return str(self)

    @abstractmethod
    def __str__(self) -> str:
        pass

    @abstractmethod
    def __getitem__(self, index: Union[int, slice]) -> Union[str, List[str]]:
        pass

    @abstractmethod
    def __iter__(self) -> Iterator[str]:
        pass


class Text(StringSequence):
    def __init__(self, text: str) -> None:
        self._text = text

    def validate_offset(self, start_offset: int, end_offset: int) -> bool:
        return 0 <= start_offset <= end_offset < len(self._text)

    def align_offset(self, start_offset: int, end_offset: int) -> Tuple[int, int]:
        return start_offset, end_offset

    def __str__(self) -> str:
        return self._text

    def __getitem__(self, index: Union[int, slice]) -> Union[str, List[str]]:
        return self._text[index]

    def __iter__(self) -> Iterator[str]:
        yield from self._text


class TokenizedText(StringSequence):
    def __init__(self, tokens: List[str], space_after: List[bool]) -> None:
        self._tokens = tokens
        self._space_after = space_after

        mapping, _ = get_alignments(tokens, str(self))
        start_boundaries = {}
        end_boundaries = {}
        for i, indices in enumerate(mapping):
            start_boundaries[indices[0]] = i
            end_boundaries[indices[-1]] = i
        self._start_boundaries = start_boundaries
        self._end_boundaries = end_boundaries

    def validate_offset(self, start_offset: int, end_offset: int) -> bool:
        return (
            start_offset <= end_offset and start_offset in self._start_boundaries and end_offset in self._end_boundaries
        )

    def align_offset(self, start_offset: int, end_offset: int) -> Tuple[int, int]:
        if not self.validate_offset(start_offset, end_offset):
            raise ValueError("Invalid offset")
        return self._start_boundaries[start_offset], self._end_boundaries[end_offset]

    def __str__(self) -> str:
        string = []
        for token, is_space in zip(self._tokens, self._space_after):
            string.append(token)
            if is_space:
                string.append(" ")
        return "".join(string)

    def __getitem__(self, index: Union[int, slice]) -> Union[str, List[str]]:
        return self._tokens[index]

    def __iter__(self) -> Iterator[str]:
        yield from self._tokens


@dataclass
class Entity:
    start_offset: int
    end_offset: int
    label: str

    def __len__(self) -> int:
        return self.end_offset - self.start_offset + 1
