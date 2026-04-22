import QuantLib as ql
import numpy as np
import pandas as pd


# =========================
# Base Instrument Interface
# =========================
class Instrument:
    def __init__(self, row, market_data, ql_env):
        self.row = row
        self.market_data = market_data
        self.ql_env = ql_env

    def price(self):
        raise NotImplementedError

    def greeks(self):
        raise NotImplementedError


# =========================
# Stock Instrument
# =========================
class StockInstrument(Instrument):

    def price(self):
        return self.row["Quantity"] * self.row["CurrentPrice"]

    def greeks(self):
        return {
            "Delta": self.row["Quantity"],
            "Gamma": 0.0,
            "Vega": 0.0,
            "Theta": 0.0,
            "Rho": 0.0
        }


# =========================
# FX Forward Instrument
# =========================
class FXForwardInstrument(Instrument):

    def price(self):
        spot = self.row["CurrentPrice"]
        strike = self.row["Strike"]
        quantity = self.row["Quantity"]

        maturity = self.row["Maturity"]

        ql_date = self.ql_env["valuation_date"]
        day_count = self.ql_env["day_count"]

        T = day_count.yearFraction(ql_date, maturity)

        domestic_df = self.ql_env["rate_curve"].discount(T)
        foreign_df = self.ql_env["foreign_curve"].discount(T)

        fwd = spot * foreign_df / domestic_df

        return quantity * (fwd - strike) * domestic_df

    def greeks(self):
        # Simple delta approximation
        spot = self.row["CurrentPrice"]
        bump = 0.0001 * spot

        self.row["CurrentPrice"] = spot + bump
        up = self.price()

        self.row["CurrentPrice"] = spot - bump
        down = self.price()

        self.row["CurrentPrice"] = spot

        delta = (up - down) / (2 * bump)

        return {
            "Delta": delta,
            "Gamma": 0.0,
            "Vega": 0.0,
            "Theta": 0.0,
            "Rho": 0.0
        }


# =========================
# European Option Instrument
# =========================
class EuropeanOptionInstrument(Instrument):

    def _build_option(self):
        row = self.row

        spot = row["CurrentPrice"]
        strike = row["Strike"]
        maturity = row["Maturity"]

        option_type = ql.Option.Call if row["OptionType"] == "Call" else ql.Option.Put

        payoff = ql.PlainVanillaPayoff(option_type, strike)
        exercise = ql.EuropeanExercise(
            ql.Date(maturity.day, maturity.month, maturity.year)
        )

        option = ql.VanillaOption(payoff, exercise)

        return option

    def _build_process(self):
        spot = self.row["CurrentPrice"]

        spot_handle = ql.QuoteHandle(ql.SimpleQuote(spot))

        process = ql.BlackScholesMertonProcess(
            spot_handle,
            self.ql_env["dividend_curve"],
            self.ql_env["rate_curve"],
            self.ql_env["vol_surface"]
        )

        return process

    def price(self):
        option = self._build_option()
        process = self._build_process()

        engine = ql.AnalyticEuropeanEngine(process)
        option.setPricingEngine(engine)

        npv = option.NPV()
        return npv * self.row["Quantity"]

    def greeks(self):
        option = self._build_option()
        process = self._build_process()

        engine = ql.AnalyticEuropeanEngine(process)
        option.setPricingEngine(engine)

        return {
            "Delta": option.delta() * self.row["Quantity"],
            "Gamma": option.gamma() * self.row["Quantity"],
            "Vega": option.vega() / 100.0 * self.row["Quantity"],
            "Theta": option.thetaPerDay() * self.row["Quantity"],
            "Rho": option.rho() / 100.0 * self.row["Quantity"]
        }


# =========================
# Factory
# =========================
def build_instrument(row, market_data, ql_env):
    instrument_type = row["InstrumentType"]

    if instrument_type == "Stock":
        return StockInstrument(row, market_data, ql_env)

    elif instrument_type == "FX Forward":
        return FXForwardInstrument(row, market_data, ql_env)

    elif instrument_type == "European Option":
        return EuropeanOptionInstrument(row, market_data, ql_env)

    else:
        raise ValueError(f"Unsupported instrument type: {instrument_type}")


# =========================
# Batch Processing
# =========================
def price_portfolio(df, market_data, ql_env):
    results = []

    for _, row in df.iterrows():
        inst = build_instrument(row, market_data, ql_env)

        price = inst.price()
        greeks = inst.greeks()

        result = {
            "PositionID": row["PositionID"],
            "NPV": price,
            **greeks
        }

        results.append(result)

    return pd.DataFrame(results)
