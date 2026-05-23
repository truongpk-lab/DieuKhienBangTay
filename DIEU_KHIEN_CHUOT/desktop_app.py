from pathlib import Path


APP_TITLE = "ACV Gesture Control"


def frontend_index_path():
    repo_root = Path(__file__).resolve().parent.parent
    return repo_root / "frontend" / "dist" / "index.html"


def main():
    index_path = frontend_index_path()
    if not index_path.exists():
        raise FileNotFoundError(
            "Khong tim thay frontend/dist/index.html. "
            "Hay chay: cd frontend && npm run build"
        )

    try:
        import webview
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "Chua cai pywebview. Hay chay: "
            "pip install -r DIEU_KHIEN_CHUOT\\requirements.txt"
        ) from exc

    webview.create_window(
        APP_TITLE,
        index_path.as_uri(),
        width=1440,
        height=900,
        min_size=(1180, 760),
        background_color="#0A0A0C",
    )
    webview.start(debug=False)


if __name__ == "__main__":
    main()
