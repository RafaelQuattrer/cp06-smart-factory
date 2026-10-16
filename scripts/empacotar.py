"""Gera ZIP e manifesto SHA-256 dos entregáveis, sem caches ou dependências baixadas."""
import hashlib
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_DIRS = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", ".pio", "test-results"}


def deliverable(path):
    parts = path.relative_to(ROOT).parts
    return (path.is_file() and not any(p in EXCLUDED_DIRS for p in parts)
            and path.name not in {".env", "MANIFEST.sha256"}
            and path.suffix not in {".pyc", ".log", ".zip"})


def main():
    files = sorted(p for p in ROOT.rglob("*") if deliverable(p))
    manifest = ROOT/"MANIFEST.sha256"
    manifest.write_text("".join(
        hashlib.sha256(p.read_bytes()).hexdigest() + "  " + p.relative_to(ROOT).as_posix() + "\n"
        for p in files),encoding="utf-8")
    output = ROOT.parent/"CP06_Smart_Factory.zip"
    with zipfile.ZipFile(output,"w",zipfile.ZIP_DEFLATED) as archive:
        for path in [*files,manifest]:
            archive.write(path,Path(ROOT.name)/path.relative_to(ROOT))
    with zipfile.ZipFile(output) as archive:
        assert archive.testzip() is None
        assert len(archive.namelist()) == len(files)+1
        for path in files:
            assert archive.read(f"{ROOT.name}/{path.relative_to(ROOT).as_posix()}") == path.read_bytes()
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    output.with_suffix(".zip.sha256").write_text(f"{digest}  {output.name}\n",encoding="utf-8")
    print(f"ZIP: {output.name}\nArquivos: {len(files)+1}\nTamanho: {output.stat().st_size} bytes\nSHA256: {digest}")


if __name__ == "__main__":
    main()
