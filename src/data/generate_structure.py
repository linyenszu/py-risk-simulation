import pandas as pd

def generate_structure():
    """
    Generates organizational hierarchy mapping:
    Portfolio → Trading Desk → Business Unit

    This mirrors how risk is aggregated in systems like Murex.
    """

    data = {
        "Portfolio": [
            "P1_EqUS",
            "P2_FXMaj",
            "P3_OptEq",
            "P4_OptSpec"
        ],
        "TradingDesk": [
            "Equity Desk",
            "FX Desk",
            "Options Desk",
            "Options Desk"
        ],
        "Unit": [
            "Trading Unit A",
            "Trading Unit A",
            "Trading Unit B",
            "Trading Unit B"
        ]
    }

    df = pd.DataFrame(data)
    return df


if __name__ == "__main__":
    # For standalone testing / CSV export
    structure_df = generate_structure()
    print(structure_df)

    # Optional: save to CSV (mimics Murex extract)
    structure_df.to_csv("structure.csv", index=False)
