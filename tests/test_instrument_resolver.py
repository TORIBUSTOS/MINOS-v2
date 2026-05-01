from src.services.market_data import resolve_symbol


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


def test_resolve_nyse_equity_bma():
    assert resolve_symbol("BMA", "NYSE", "EQUITY") == "BMA"


def test_resolve_nyse_equity_ypf():
    assert resolve_symbol("YPF", "NYSE", "EQUITY") == "YPF"
