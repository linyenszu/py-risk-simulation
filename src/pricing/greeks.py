import QuantLib as ql

def price_european_option(spot, strike, maturity, vol, rate):
    payoff = ql.PlainVanillaPayoff(ql.Option.Call, strike)
    exercise = ql.EuropeanExercise(maturity)

    option = ql.VanillaOption(payoff, exercise)

    spot_handle = ql.QuoteHandle(ql.SimpleQuote(spot))
    rate_handle = ql.YieldTermStructureHandle(
        ql.FlatForward(0, ql.TARGET(), rate, ql.Actual365Fixed())
    )
    vol_handle = ql.BlackVolTermStructureHandle(
        ql.BlackConstantVol(0, ql.TARGET(), vol, ql.Actual365Fixed())
    )

    process = ql.BlackScholesProcess(spot_handle, rate_handle, vol_handle)
    option.setPricingEngine(ql.AnalyticEuropeanEngine(process))

    return {
        "NPV": option.NPV(),
        "Delta": option.delta(),
        "Gamma": option.gamma(),
        "Vega": option.vega()
    }
