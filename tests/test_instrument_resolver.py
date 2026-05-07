from src.services.market_data import resolve_symbol
from src.services.normalization import cedear_underlying, infer_asset_type


def test_resolve_byma_equity_bma():
    assert resolve_symbol("BMA", "BYMA", "EQUITY") == "BMA.BA"


def test_resolve_byma_equity_ypfd():
    assert resolve_symbol("YPFD", "BYMA", "EQUITY") == "YPFD.BA"


def test_resolve_byma_equity_ggal():
    assert resolve_symbol("GGAL", "BYMA", "EQUITY") == "GGAL.BA"


def test_resolve_byma_equity_pamp():
    assert resolve_symbol("PAMP", "BYMA", "EQUITY") == "PAMP.BA"


def test_resolve_byma_equity_supv():
    assert resolve_symbol("SUPV", "BYMA", "EQUITY") == "SUPV.BA"


def test_resolve_byma_equity_does_not_duplicate_ba_suffix():
    assert resolve_symbol("BMA.BA", "BYMA", "EQUITY") == "BMA.BA"


def test_resolve_byma_cedear_uses_ba_suffix():
    assert resolve_symbol("MELI", "BYMA", "CEDEAR") == "MELI.BA"


def test_resolve_nyse_equity_bma():
    assert resolve_symbol("BMA", "NYSE", "EQUITY") == "BMA"


def test_resolve_nyse_equity_ypf():
    assert resolve_symbol("YPF", "NYSE", "EQUITY") == "YPF"


def test_infer_asset_type_known_byma_equity():
    assert infer_asset_type("BMA") == "EQUITY"
    assert infer_asset_type("YPFD.BA") == "EQUITY"


def test_infer_asset_type_known_cedear():
    assert infer_asset_type("MELI") == "CEDEAR"
    assert infer_asset_type("NVDA.BA") == "CEDEAR"


def test_cedear_underlying_known_ticker():
    assert cedear_underlying("MELI") == "MercadoLibre Inc."
    assert cedear_underlying("SPY.BA") == "SPDR S&P 500 ETF"


def test_infer_asset_type_preserves_existing_type():
    assert infer_asset_type("AL30", "BOND") == "BOND"
