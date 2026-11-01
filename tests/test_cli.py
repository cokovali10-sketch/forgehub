import subprocess, sys, json, os
from pathlib import Path

ENV = dict(os.environ)
ENV["PYTHONPATH"] = str(Path(__file__).resolve().parents[1])


def test_list():
    p = subprocess.run([sys.executable, "-m", "forgehub.cli", "list"], capture_output=True, text=True, env=ENV)
    assert p.returncode == 0
    assert "solar" in p.stdout.lower()
    assert "forge" in p.stdout.lower()


def test_search():
    p = subprocess.run([sys.executable, "-m", "forgehub.cli", "search", "compress"], capture_output=True, text=True, env=ENV)
    assert p.returncode == 0
    assert "solar" in p.stdout.lower() or "compress" in p.stdout.lower()


def test_context():
    p = subprocess.run([sys.executable, "-m", "forgehub.cli", "context"], capture_output=True, text=True, env=ENV)
    assert p.returncode == 0
    assert "ForgeHub" in p.stdout


def test_show():
    p = subprocess.run([sys.executable, "-m", "forgehub.cli", "show", "prompt-compression"], capture_output=True, text=True, env=ENV)
    assert p.returncode == 0
    assert "Compress prompts" in p.stdout


def test_describe():
    p = subprocess.run([sys.executable, "-m", "forgehub.cli", "describe", "solar"], capture_output=True, text=True, env=ENV)
    assert p.returncode == 0
    assert "SOLAR" in p.stdout
