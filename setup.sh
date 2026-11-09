PYTHON_VERSION="3.12.7"
WHISPER_COMMIT="1fe009caeda75f69bc864d6370b10674e45a92bd"

# 1. Detect OS and install dependencies
OS="$(uname)"
echo "Detected OS: $OS"

if [ "$OS" = "Darwin" ]; then
    if ! command -v brew >/dev/null 2>&1; then
        echo "Installing homebrew..."
        /bin/bash -c /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi

    brew install ffmpeg cmake pyenv poetry
elif [ "$OS" = "Linux" ]; then
    if [ -f /etc/os-release ]; then
        . /etc/os-release

        if [ "$ID" != "ubuntu" ]; then
            echo "Unsupported Linux distrobution detected."
            exit
        fi
    else 
        echo "Linux detected, but unable to identify distrobution."
        exit
    fi

    sudo apt update -y
    sudo apt install -y ffmpeg cmake pyenv python3-poetry
else
    echo "Unsupported Operating System: $OS"
    exit
fi

# 2. Setup python environment
if ! pyenv versions --bare | grep -qx "$PYTHON_VERSION"; then
    echo "Installing Python $PYTHON_VERSION..."
    pyenv install "$PYTHON_VERSION"
fi

poetry install
poetry env activate

# 3. Clone and buil Whisper.cpp
if [ ! -d "whisper.cpp" ]; then
    echo "Cloning whisper.cpp..."
    git clone https://github.com/ggerganov/whisper.cpp
fi

git checkout 1fe009caeda75f69bc864d6370b10674e45a92bd

cd whisper.cpp
cmake -B build
cmake --build build --config Release

if [ ! -f "models/ggml-large-v3.bin" ]; then
    echo "Downloading GGML large-v3 model..."
    ./models/download-ggml-model.sh large-v3
fi

if [ ! -f "models/ggml-silero-v6.2.0.bin" ]; then
    echo "Downloading Silero VAD model..."
    ./models/download-ggml-model.sh silero-v6.2.0
fi

echo "Initialization complete"