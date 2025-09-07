import pathlib
from common import load_inventory, render_device, OUT_DIR

def test_render_all():
    devs = load_inventory()
    for name, vars in devs.items():
        p = render_device(name, vars)
        assert p.exists()
        text = p.read_text().strip()
        assert "set system host-name" in text

def test_r1_contains_expected_networks():
    p = OUT_DIR / "R1.set"
    if not p.exists():
        # allow running after deploy_async.py --generate-only
        return
    text = p.read_text()
    assert "10.10.10.0/24" in text
