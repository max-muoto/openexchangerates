from __future__ import annotations

import datetime as dt
from collections.abc import Iterable
from typing import Any, cast

import aiohttp

from oxr import responses
from oxr._base import BaseClient
from oxr._types import Currency, Endpoint, Period


def _encode_params(params: dict[str, Any]) -> dict[str, Any]:
    """yarl does not encode booleans as strings."""
    return {
        key: "true" if value is True else "false" if value is False else value
        for key, value in params.items()
    }


class Client(BaseClient):
    """A asynchronous client for the Open Exchange Rates API."""

    async def _get(
        self,
        endpoint: Endpoint,
        query_params: dict[str, Any],
        path_params: list[str] | None = None,
    ) -> dict[str, Any]:
        url = self._prepare_url(endpoint, path_params)
        async with aiohttp.ClientSession() as session, session.get(
            url,
            params=_encode_params({"app_id": self._app_id, **query_params}),
        ) as response:
            response.raise_for_status()
            return await response.json()

    async def currencies(self) -> responses.Currencies:
        """Get a list of available currencies."""
        return cast(responses.Currencies, await self._get("currencies", {}))

    async def latest(
        self,
        base: str | None = None,
        symbols: Iterable[Currency] | None = None,
        show_alternative: bool = False,
    ) -> responses.Rates:
        """Get the latest exchange rates.

        Args:
            base: The base currency.
            symbols: The target currencies.
            show_alternative: Whether to show alternative currencies.
                Such as black market and digital currency rates.
        """
        params = {
            "app_id": self._app_id,
            "base": base or self._base,
            "show_alternative": show_alternative,
        }
        if symbols is not None:
            params["symbols"] = ",".join(symbols)
        return cast(responses.Rates, await self._get("latest", params))

    async def historical(
        self,
        date: dt.date,
        base: str | None = None,
        symbols: Iterable[Currency] | None = None,
        show_alternative: bool = False,
    ) -> responses.Rates:
        """Get historical exchange rates.

        Args:
            date: The date of the rates.
            base: The base currency.
            symbols: The target currencies.
            show_alternative: Whether to show alternative currencies.
                Such as black market and digital currency rates.
        """
        params = {
            "base": base or self._base,
            "show_alternative": show_alternative,
        }
        if symbols is not None:
            params["symbols"] = ",".join(symbols)
        return cast(
            responses.Rates, await self._get("historical", params, path_params=[date.isoformat()])
        )

    async def convert(
        self,
        amount: float,
        from_: str,
        to: str,
    ) -> responses.Conversion:
        """Convert an amount between two currencies.

        Args:
            amount: The amount to convert.
            from_: The source currency.
            to: The target currency.
            date: The date of the rates to use.
        """
        params = {"from": from_, "to": to, "amount": amount}
        return cast(responses.Conversion, await self._get("convert", params))

    async def time_series(
        self,
        start: dt.date,
        end: dt.date,
        symbols: Iterable[Currency] | None = None,
        base: str | None = None,
        show_alternative: bool = False,
    ) -> responses.TimeSeries:
        """Get historical exchange rates for a range of dates.

        Args:
            start: The start date of the range.
            end: The end date of the range.
            symbols: The target currencies.
            base: The base currency.
            show_alternative: Whether to show alternative currencies.
                Such as black market and digital currency rates.
        """
        params = {
            "start": start.isoformat(),
            "end": end.isoformat(),
            "show_alternative": show_alternative,
        }
        params["base"] = base or self._base
        if symbols is not None:
            params["symbols"] = ",".join(symbols)
        return cast(responses.TimeSeries, await self._get("time-series", params))

    async def ohlc(
        self,
        start_time: dt.datetime,
        period: Period,
        base: str | None = None,
        symbols: Iterable[Currency] | None = None,
        show_alternative: bool = False,
    ) -> responses.OHLC:
        """Get the latest open, low, high, and close rates for a currency.

        Args:
            base: The base currency.
            symbols: The target currencies.
            show_alternative: Whether to show alternative currencies.
                Such as black market and digital currency rates.
        """
        params = {
            "start_time": start_time.isoformat(),
            "period": period,
            "show_alternative": show_alternative,
        }
        params["base"] = base or self._base
        if symbols is not None:
            params["symbols"] = ",".join(symbols)
        return cast(responses.OHLC, await self._get("ohlc", params))

    async def usage(self) -> dict[str, Any]:
        """Get the usage statistics for the API key."""
        return await self._get("usage", {})
