"""
The MIT License (MIT)

Copyright (c) 2021-present Village

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Generic, TypeVar, Union

from .. import utils
from ..enums import ButtonStyle, ComponentType, TextInputStyle
from ..errors import CheckError
from ..missing import MISSING

__all__ = (
    "Component",
    "AllComponents",
    "ActionRow",
    "Button",
    "SelectMenu",
    "TextInput",
    "Modal",
    "Grid",
    "SelectOption",
)

if TYPE_CHECKING:
    from typing import (
        Any,
        Callable,
        Coroutine,
        Dict,
        Final,
        Generator,
        List,
        Optional,
        Tuple,
    )

    from ..bot import Bot
    from ..missing import Missing
    from ..models.emoji import Emoji
    from ..types.interactions import ActionRow as ActionRowData
    from ..types.interactions import Button as ButtonData
    from ..types.interactions import Component as ComponentData
    from ..types.interactions import SelectMenu as SelectMenuData
    from ..types.interactions import SelectOption as SelectOptionData
    from ..types.interactions import TextInput as TextInputData
    from .interaction import Interaction

    Groups = Dict[str, str]
    # something something indirect reference to itself, doesn't seem to break anything
    ButtonCheck = Callable[["Component", Interaction, Groups], Coroutine[Any, Any, Any]]
    SelectMenuCheck = Callable[
        ["Component", Interaction, Groups, Tuple[str]], Coroutine[Any, Any, Any]
    ]
    GridCheck = Callable[
        ["Grid", "Component", Interaction, Groups, Tuple[str]], Coroutine[Any, Any, Any]
    ]
    ModalCheck = Callable[
        ["Modal[M]", Interaction, Groups, "M"],
        Coroutine[Any, Any, Any],
    ]

    BC = TypeVar("BC", bound=Any)
    SC = TypeVar("SC", bound=Any)
    GC = TypeVar("GC", bound=Any)
    MC = TypeVar("MC", bound=Any)
    CH = TypeVar("CH", bound="Component")
    B = TypeVar("B", bound=Bot)

M = TypeVar("M")
Component = Union["Button", "SelectMenu"]
AllComponents = Union["ActionRow", Component, "TextInput"]


class ActionRow:
    type: Final = ComponentType.ACTION_ROW

    __slots__ = ("components",)

    def __init__(self, *components: AllComponents) -> None:
        self.components: List[AllComponents] = list(components)

    def to_payload(self) -> ActionRowData:
        return {
            "type": self.type.value,
            "components": [component.to_payload() for component in self.components],
        }


class Button:
    WIDTH: Final = 1
    type: Final = ComponentType.BUTTON
    checks: List[ButtonCheck]

    __slots__ = (
        "style",
        "label",
        "emoji",
        "custom_id",
        "url",
        "disabled",
        "row",
        "pattern",
        "grid",
    )

    def __init__(
        self,
        *,
        style: Missing[ButtonStyle] = MISSING,
        label: Missing[Any] = MISSING,
        emoji: Missing[Emoji] = MISSING,
        custom_id: Missing[str] = MISSING,
        url: Missing[str] = MISSING,
        disabled: Missing[bool] = MISSING,
        row: Missing[int] = MISSING,
        pattern: Missing[str] = MISSING,
    ) -> None:
        if custom_id is not MISSING and pattern is not MISSING and url is not MISSING:
            raise ValueError("Cannot specify both custom_id/pattern and url")
        self.style: ButtonStyle = style or (
            ButtonStyle.LINK if url else ButtonStyle.SECONDARY
        )
        self.label: Missing[Any] = label
        self.emoji: Missing[Emoji] = emoji
        self.custom_id: Missing[str] = custom_id or (
            custom_id if url else utils.generate_custom_id(100)
        )
        self.url: Missing[str] = url
        self.disabled: Missing[bool] = disabled
        self.row: Missing[int] = row
        self.pattern: Missing[re.Pattern[str]] = (
            pattern if pattern is MISSING else re.compile(pattern)
        )
        self.grid: Optional[Grid] = None

    def __init_subclass__(cls, *, checks: Missing[List[ButtonCheck]] = MISSING) -> None:
        cls.checks = [j for i in cls.__mro__ for j in getattr(i, "checks", [])] + (
            checks or []
        )

    async def run_component(self, interaction: Interaction, groups: Groups) -> None:
        if self.grid is not None:
            for check in self.grid.checks:
                try:
                    if not await check(self.grid, self, interaction, groups, tuple()):
                        return
                except Exception as e:
                    return await self.on_check_error(interaction, e)
        for check in self.checks:
            try:
                if not await check(self, interaction, groups):
                    return
            except Exception as e:
                return await self.on_check_error(interaction, e)
        try:
            await self.callback(interaction, groups)
        except Exception as e:
            return await self.on_error(interaction, e)

    async def callback(
        self, interaction: Interaction, groups: Missing[Dict[str, str]]
    ) -> Any:
        ...

    def to_payload(self) -> ButtonData:
        payload: ButtonData = {
            "type": ComponentType.BUTTON.value,
            "style": self.style.value,
        }
        if self.label is not MISSING:
            payload["label"] = str(self.label)
        if self.emoji is not MISSING:
            ...  # TODO: Implement emoji
        if self.custom_id is not MISSING:
            payload["custom_id"] = self.custom_id
        if self.url is not MISSING:
            payload["url"] = self.url
        if self.disabled is not MISSING:
            payload["disabled"] = self.disabled
        return payload

    async def on_error(self, interaction: Interaction, error: Exception) -> None:
        if isinstance(error, CheckError):
            utils.print_exception_with_header(
                f"Ignoring exception in check of component {self}:", error.error
            )
        else:
            utils.print_exception_with_header(
                f"Ignoring exception in component {self}:", error
            )

    async def on_check_error(self, interaction: Interaction, error: Exception) -> None:
        await self.on_error(interaction, CheckError(error))

    @classmethod
    def add_check(cls, check: ButtonCheck) -> None:
        cls.checks.append(check)

    @classmethod
    def check(cls, func: BC) -> BC:
        cls.add_check(func)
        return func


class SelectMenu:
    WIDTH: Final = 5
    type: Final = ComponentType.SELECT_MENU
    checks: List[SelectMenuCheck]

    __slots__ = (
        "custom_id",
        "options",
        "placeholder",
        "min_values",
        "max_values",
        "disabled",
        "row",
        "pattern",
        "grid",
    )

    def __init__(
        self,
        *,
        custom_id: Missing[str] = MISSING,
        options: Missing[List[SelectOption]] = MISSING,
        placeholder: Missing[Any] = MISSING,
        min_values: Missing[int] = MISSING,
        max_values: Missing[int] = MISSING,
        disabled: Missing[bool] = MISSING,
        row: Missing[int] = MISSING,
        pattern: Missing[str] = MISSING,
    ) -> None:
        self.custom_id: str = custom_id or utils.generate_custom_id(100)
        self.options: List[SelectOption] = options or []
        self.placeholder: Missing[Any] = placeholder
        self.min_values: Missing[int] = min_values
        self.max_values: Missing[int] = max_values
        self.disabled: Missing[bool] = disabled
        self.row: Missing[int] = row
        self.pattern: Missing[re.Pattern[str]] = (
            pattern if pattern is MISSING else re.compile(pattern)
        )
        self.grid: Optional[Grid] = None

    def __init_subclass__(
        cls, *, checks: Missing[List[SelectMenuCheck]] = MISSING
    ) -> None:
        cls.checks = [j for i in cls.__mro__ for j in getattr(i, "checks", [])] + (
            checks or []
        )

    async def run_component(self, interaction: Interaction, groups: Groups) -> None:
        # type: ignore to save using .get, if an interaction gets here
        # it will have values or there should be an error since the user
        # messed with something incorrectly
        values: Tuple[str] = tuple(interaction.data["values"])  # type: ignore
        if self.grid is not None:
            for check in self.grid.checks:
                try:
                    if not await check(self.grid, self, interaction, groups, values):
                        return
                except Exception as e:
                    return await self.on_check_error(interaction, values, e)
        for check in self.checks:
            try:
                if not await check(self, interaction, groups, values):
                    return
            except Exception as e:
                return await self.on_check_error(interaction, values, e)
        try:
            await self.callback(interaction, groups, values)
        except Exception as e:
            return await self.on_error(interaction, values, e)

    async def callback(
        self, interaction: Interaction, groups: Groups, values: Tuple[str]
    ) -> Any:
        ...

    def to_payload(self) -> SelectMenuData:
        data: SelectMenuData = {
            "type": self.type.value,
            "custom_id": self.custom_id,
            "options": [i.to_payload() for i in self.options],
        }
        if self.placeholder is not MISSING:
            data["placeholder"] = str(self.placeholder)
        if self.min_values is not MISSING:
            data["min_values"] = self.min_values
        if self.max_values is not MISSING:
            data["max_values"] = self.max_values
        if self.disabled is not MISSING:
            data["disabled"] = self.disabled
        return data

    async def on_error(
        self, interaction: Interaction, values: Tuple[str], error: Exception
    ) -> None:
        if isinstance(error, CheckError):
            utils.print_exception_with_header(
                f"Ignoring exception in check of component {self}:", error.error
            )
        else:
            utils.print_exception_with_header(
                f"Ignoring exception in component {self}:", error
            )

    async def on_check_error(
        self, interaction: Interaction, values: Tuple[str], error: Exception
    ) -> None:
        await self.on_error(interaction, values, CheckError(error))

    @classmethod
    def add_check(cls, check: SelectMenuCheck) -> None:
        cls.checks.append(check)

    @classmethod
    def check(cls, func: SC) -> SC:
        cls.add_check(func)
        return func


class TextInput:
    WIDTH: Final = 5
    type: Final = ComponentType.TEXT_INPUT

    __slots__ = (
        "name" "style",
        "label",
        "custom_id",
        "min_length",
        "max_length",
        "required",
        "value",
        "placeholder",
        "modal",
        "row",
        "pattern",
    )

    def __init__(
        self,
        name: str,
        *,
        style: TextInputStyle,
        label: str,
        custom_id: Missing[str] = MISSING,
        min_length: Missing[int] = MISSING,
        max_length: Missing[int] = MISSING,
        required: Missing[bool] = MISSING,
        value: Missing[str] = MISSING,
        placeholder: Missing[str] = MISSING,
        row: Missing[int] = MISSING,
    ) -> None:
        self.name: str = name
        self.style: TextInputStyle = style
        self.label: str = label
        self.custom_id: str = custom_id or utils.generate_custom_id(100)
        self.min_length: Missing[int] = min_length
        self.max_length: Missing[int] = max_length
        self.required: Missing[bool] = required
        self.value: Missing[str] = value
        self.placeholder: Missing[str] = placeholder
        self.modal: Optional[Modal[Any]] = None
        self.row: Missing[int] = row

    def to_payload(self) -> TextInputData:
        payload: TextInputData = {
            "type": self.type.value,
            "custom_id": self.custom_id,
            "style": self.style.value,
            "label": self.label,
        }
        if self.min_length is not MISSING:
            payload["min_length"] = self.min_length
        if self.max_length is not MISSING:
            payload["max_length"] = self.max_length
        if self.required is not MISSING:
            payload["required"] = self.required
        if self.value is not MISSING:
            payload["value"] = self.value
        if self.placeholder is not MISSING:
            payload["placeholder"] = self.placeholder
        return payload


class TextInputValue:
    __slots__ = ("value", "component")

    def __init__(self, value: str, component: TextInput) -> None:
        self.value: str = value
        self.component: TextInput = component

    @classmethod
    def from_payload(
        cls, modal: Modal[Any], value: str, custom_id: str
    ) -> TextInputValue:
        return cls(value, next(i for i in modal.components if i.custom_id == custom_id))


class ModalValues:
    @classmethod
    def from_generator(
        cls, generator: Generator[TextInputValue, None, None]
    ) -> ModalValues:
        self = cls()
        for value in generator:
            setattr(self, value.component.name, value.value)
        return self


class Modal(Generic[M]):
    checks: List[ModalCheck[M]]

    def __init__(
        self,
        *,
        title: str,
        custom_id: Missing[str] = MISSING,
        timeout: Optional[float] = 300,
        pattern: Missing[str] = MISSING,
    ) -> None:
        self.title: str = title
        self.custom_id: str = custom_id or utils.generate_custom_id(100)
        self.timeout: Optional[float] = timeout
        self.pattern: Missing[re.Pattern[str]] = (
            pattern if pattern is MISSING else re.compile(pattern)
        )
        self.components: List[TextInput] = []

    def __init_subclass__(
        cls, *, checks: Missing[List[ModalCheck[M]]] = MISSING
    ) -> None:
        cls.checks = [j for i in cls.__mro__ for j in getattr(i, "checks", [])] + (
            checks or []
        )

    def has_space(self, width: int, row: Missing[int] = MISSING) -> bool:
        available = [
            5 - sum(i.WIDTH for i in self.components if i.row == r) for r in range(1, 6)
        ]
        for i in self.components:
            if i.row is not MISSING:
                continue
            for i in range(5):
                if available[i] >= width:
                    available[i] -= width
                    break
        if row is MISSING:
            return any(i >= width for i in available)
        return available[row - 1] >= width

    def add_component(self, component: TextInput) -> Modal[M]:
        if not self.has_space(component.WIDTH, component.row):
            raise ValueError("No space available for this component.")
        component.modal = self
        self.components.append(component)
        return self

    @classmethod
    def add_check(cls, check: ModalCheck[M]) -> None:
        cls.checks.append(check)

    @classmethod
    def check(cls, func: MC) -> MC:
        cls.add_check(func)
        return func

    def to_payload(self) -> List[ComponentData]:
        rows: List[List[TextInput]] = [
            [i for i in self.components if i.row == r] for r in range(1, 6)
        ]
        for i in self.components:
            if i.row is MISSING:
                for j in rows:
                    if sum(k.WIDTH for k in j) >= 5:
                        continue
                    j.append(i)
                    break
        return [ActionRow(*i).to_payload() for i in rows if i]

    def store(self, bot: B) -> B:
        bot.add_modal(self)
        return bot

    def build_component(self, data: ComponentData) -> TextInputValue:
        if data["type"] == ComponentType.TEXT_INPUT.value:
            return TextInputValue.from_payload(self, data["value"], data["custom_id"])  # type: ignore
        raise ValueError(f"Unknown component type: {data['type']}")

    async def run_modal(self, interaction: Interaction, groups: Groups) -> None:
        # type: ignore to save using .get, if an interaction gets here
        # it will have values or there should be an error since the user
        # messed with something incorrectly
        values: M = ModalValues.from_generator(self.build_component(j) for i in interaction.data["components"] for j in i["components"])  # type: ignore
        for check in self.checks:
            try:
                if not await check(self, interaction, groups, values):
                    return
            except Exception as e:
                return await self.on_check_error(interaction, values, e)
        try:
            await self.callback(interaction, groups, values)
        except Exception as e:
            return await self.on_error(interaction, values, e)

    async def on_error(
        self, interaction: Interaction, values: M, error: Exception
    ) -> None:
        if isinstance(error, CheckError):
            utils.print_exception_with_header(
                f"Ignoring exception in check of modal {self}:", error.error
            )
        else:
            utils.print_exception_with_header(
                f"Ignoring exception in modal {self}:", error
            )

    async def on_check_error(
        self, interaction: Interaction, values: M, error: Exception
    ) -> None:
        await self.on_error(interaction, values, CheckError(error))

    async def callback(
        self,
        interaction: Interaction,
        groups: Missing[Dict[str, str]],
        values: M,
    ) -> Any:
        ...


class Grid:
    checks: List[GridCheck]

    __slots__ = ("components", "timeout")

    def __init__(self, *, timeout: Optional[float] = 300) -> None:
        self.timeout: Optional[float] = timeout
        self.components: List[Component] = []

    def __init_subclass__(cls, *, checks: Missing[List[GridCheck]] = MISSING) -> None:
        cls.checks = [j for i in cls.__mro__ for j in getattr(i, "checks", [])] + (
            checks or []
        )

    def has_space(self, width: int, row: Missing[int] = MISSING) -> bool:
        available = [
            5 - sum(i.WIDTH for i in self.components if i.row == r) for r in range(1, 6)
        ]
        for i in self.components:
            if i.row is not MISSING:
                continue
            for i in range(5):
                if available[i] >= width:
                    available[i] -= width
                    break
        if row is MISSING:
            return any(i >= width for i in available)
        return available[row - 1] >= width

    def add_component(self, component: Component) -> Grid:
        if not self.has_space(component.WIDTH, component.row):
            raise ValueError("No space available for this component.")
        component.grid = self
        self.components.append(component)
        return self

    @classmethod
    def add_check(cls, check: GridCheck) -> None:
        cls.checks.append(check)

    @classmethod
    def check(cls, func: GC) -> GC:
        cls.add_check(func)
        return func

    def to_payload(self) -> List[ComponentData]:
        rows: List[List[Component]] = [
            [i for i in self.components if i.row == r] for r in range(1, 6)
        ]
        for i in self.components:
            if i.row is MISSING:
                for j in rows:
                    if sum(k.WIDTH for k in j) >= 5:
                        continue
                    j.append(i)
                    break
        return [ActionRow(*i).to_payload() for i in rows if i]

    def store(self, bot: B) -> B:
        for i in self.components:
            bot.add_component(i)
        return bot


class SelectOption:
    __slots__ = ("label", "value", "description", "emoji", "default")

    def __init__(
        self,
        *,
        label: str,
        value: str,
        description: Missing[str] = MISSING,
        emoji: Missing[Emoji] = MISSING,
        default: Missing[bool] = MISSING,
    ) -> None:
        self.label: str = label
        self.value: str = value
        self.description: Missing[str] = description
        self.emoji: Missing[Emoji] = emoji
        self.default: Missing[bool] = default

    def to_payload(self) -> SelectOptionData:
        data: SelectOptionData = {"label": self.label, "value": self.value}
        if self.description is not MISSING:
            data["description"] = self.description
        if self.default is not MISSING:
            data["default"] = self.default
        return data
