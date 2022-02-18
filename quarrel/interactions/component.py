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

from typing import TYPE_CHECKING, Union

from .. import utils
from ..enums import ButtonStyle, ComponentType
from ..errors import CheckError
from ..missing import MISSING

__all__ = (
    "Component",
    "AllComponents",
    "ActionRow",
    "Button",
    "SelectMenu",
    "Grid",
    "SelectOption",
)

if TYPE_CHECKING:
    from typing import Any, Callable, Coroutine, Final, List, Optional, Tuple, TypeVar

    from ..missing import Missing
    from ..models.emoji import Emoji
    from ..types.interactions import ActionRow as ActionRowData
    from ..types.interactions import Button as ButtonData
    from ..types.interactions import Component as ComponentData
    from ..types.interactions import SelectMenu as SelectMenuData
    from ..types.interactions import SelectOption as SelectOptionData
    from .interaction import Interaction

    # something something indirect reference to itself, doesn't seem to break anything
    ButtonCheck = Callable[["Component", Interaction], Coroutine[Any, Any, Any]]  # type: ignore
    SelectMenuCheck = Callable[["Component", Interaction, Tuple[str]], Coroutine[Any, Any, Any]]  # type: ignore
    GridCheck = Callable[["Grid", "Component", Interaction, Tuple[str]], Coroutine[Any, Any, Any]]  # type: ignore

    BC = TypeVar("BC", bound=ButtonCheck)
    SC = TypeVar("SC", bound=SelectMenuCheck)
    GC = TypeVar("GC", bound=GridCheck)
    CH = TypeVar("CH", bound="Component")

Component = Union["Button", "SelectMenu"]
AllComponents = Union["ActionRow", Component]


class ActionRow:
    type: Final = ComponentType.ACTION_ROW

    __slots__ = ("components",)

    def __init__(self, *components: Component) -> None:
        self.components: List[Component] = list(components)

    def to_payload(self) -> ActionRowData:
        return {
            "type": self.type.value,
            "components": [component.to_payload() for component in self.components],
        }


class Button:
    WIDTH: Final = 1
    type: Final = ComponentType.BUTTON
    grid: Optional[Grid]
    checks: List[ButtonCheck]

    __slots__ = (
        "style",
        "label",
        "emoji",
        "custom_id",
        "url",
        "disabled",
        "row",
        "grid",
    )

    def __init__(
        self,
        *,
        style: Missing[ButtonStyle] = MISSING,
        label: Missing[str] = MISSING,
        emoji: Missing[Emoji] = MISSING,
        custom_id: Missing[str] = MISSING,
        url: Missing[str] = MISSING,
        disabled: Missing[bool] = MISSING,
        row: Missing[int] = MISSING,
    ) -> None:
        if custom_id is not MISSING and url is not MISSING:
            raise ValueError("Cannot specify both custom_id and url")
        self.style: ButtonStyle = style or (
            ButtonStyle.LINK if url else ButtonStyle.SECONDARY
        )
        self.label: Missing[str] = label
        self.emoji: Missing[Emoji] = emoji
        self.custom_id: Missing[str] = custom_id or (
            custom_id if url else utils.generate_custom_id(100)
        )
        self.url: Missing[str] = url
        self.disabled: Missing[bool] = disabled
        self.row: Missing[int] = row
        self.grid: Optional[Grid] = None

    def __init_subclass__(cls, *, checks: Missing[List[ButtonCheck]] = MISSING) -> None:
        cls.checks = checks or []

    async def run_component(self, interaction: Interaction) -> None:
        if self.grid is not None:
            for check in self.grid.checks:
                try:
                    if not await check(self.grid, self, interaction, tuple()):
                        return
                except Exception as e:
                    return await self.on_check_error(interaction, e)
        for check in self.checks:
            try:
                if not await check(self, interaction):
                    return
            except Exception as e:
                return await self.on_check_error(interaction, e)
        try:
            await self.callback(interaction)
        except Exception as e:
            return await self.on_error(interaction, e)

    async def callback(self, interaction: Interaction) -> Any:
        ...

    def to_payload(self) -> ButtonData:
        payload: ButtonData = {
            "type": ComponentType.BUTTON.value,
            "style": self.style.value,
        }
        if self.label is not MISSING:
            payload["label"] = self.label
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
    grid: Optional[Grid]
    checks: List[SelectMenuCheck]

    __slots__ = (
        "custom_id",
        "options",
        "placeholder",
        "min_values",
        "max_values",
        "disabled",
        "row",
        "grid",
    )

    def __init__(
        self,
        *,
        custom_id: Missing[str] = MISSING,
        options: Missing[List[SelectOption]],
        placeholder: Missing[str] = MISSING,
        min_values: Missing[int] = MISSING,
        max_values: Missing[int] = MISSING,
        disabled: Missing[bool] = MISSING,
        row: Missing[int] = MISSING,
    ) -> None:
        self.custom_id: str = custom_id or utils.generate_custom_id(100)
        self.options: List[SelectOption] = options or []
        self.placeholder: Missing[str] = placeholder
        self.min_values: Missing[int] = min_values
        self.max_values: Missing[int] = max_values
        self.disabled: Missing[bool] = disabled
        self.row: Missing[int] = row
        self.grid: Optional[Grid] = None

    def __init_subclass__(
        cls, *, checks: Missing[List[SelectMenuCheck]] = MISSING
    ) -> None:
        cls.checks = checks or []

    async def run_component(self, interaction: Interaction) -> None:
        # type: ignore to save using .get, if an interaction gets here
        # it will have values or there should be an error since the user
        # messed with something incorrectly
        values: Tuple[str] = tuple(interaction.data["values"])  # type: ignore
        if self.grid is not None:
            for check in self.grid.checks:
                try:
                    if not await check(self.grid, self, interaction, values):
                        return
                except Exception as e:
                    return await self.on_check_error(interaction, values, e)
        for check in self.checks:
            try:
                if not await check(self, interaction, values):
                    return
            except Exception as e:
                return await self.on_check_error(interaction, values, e)
        try:
            await self.callback(interaction, values)
        except Exception as e:
            return await self.on_error(interaction, values, e)

    async def callback(self, interaction: Interaction, values: Tuple[str]) -> Any:
        ...

    def to_payload(self) -> SelectMenuData:
        data: SelectMenuData = {
            "type": self.type.value,
            "custom_id": self.custom_id,
            "options": [i.to_payload() for i in self.options],
        }
        if self.placeholder is not MISSING:
            data["placeholder"] = self.placeholder
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


class Grid:
    checks: List[GridCheck]

    __slots__ = ("components", "timeout")

    def __init__(self, *, timeout: Optional[float] = 300) -> None:
        self.timeout: Optional[float] = timeout
        self.components: List[Component] = []

    def __init_subclass__(cls, *, checks: Missing[List[GridCheck]] = MISSING) -> None:
        cls.checks = checks or []

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
        if row is MISSING:
            return any(available[i] >= width for i in available)
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
                    if sum(k.WIDTH for k in j) > 5:
                        continue
                    j.append(i)
                    break
        return [ActionRow(*i).to_payload() for i in rows]


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
