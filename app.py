import os

from achados import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("ACHADOS_PORT", os.environ.get("CAMPUSLAB_PORT", "5057"))), debug=False)
