# bifurc2midi

## macOS installation instructions

### Pre-requisites

- Python 3: this should already be installed by default
- pip: This is a package manager for Python. It should already be installed by default.

### Download the source code

#### Option 1: Clone the repository using git

- Pre-requisites:
    - git: This is a version control system. It can be installed by going to the App Store and installing Xcode.

1. Open a terminal window and navigate to the directory where you want to download the source code.
2. Clone the repository:
```bash
git clone https://github.com/jjsymes/bifurc2midi.git
```
3. Navigate to the newly created `bifurc2midi` directory:
```bash
cd bifurc2midi
```

#### Option 2: Download the source code as a zip file

- Download the source code from the [GitHub repository](https://github.com/jjsymes/bifurc2midi) and unzip it to a directory of your choice.

- In the terminal, navigate to the directory where you unzipped the source code e.g.
```bash
cd ~/Downloads/bifurc2midi
```

### Install the package

#### Option 1: Install onto your system

1. Make sure pip is up to date:
```bash
python3 -m pip install --upgrade pip
```

2. Go to the `bifurc2midi` directory e.g.
```bash
cd ~/User/bifurc2midi
```

3. Install package from source code:
```bash
pip3 install .
```

At this point you should be able to run the application from the command line e.g.
```bash
bifurc2midi --version
```

#### Option 2: Install into a virtual environment

1. Go to the `bifurc2midi` directory e.g.
```bash
cd ~/User/bifurc2midi
```

2. Create a virtual environment:
```bash
make virtualenv
```

3. Download and install project dependencies:
```bash
make install
```

4. Run the application:
```bash
make run EXTRA_ARGS=""
```

The `EXTRA_ARGS` variable can be used to pass additional arguments to the application e.g.
```bash
make run EXTRA_ARGS="--help"
```

Alternatively, run the application directly:
```bash
./venv/bin/python3 bifurc2midi --help
```
or
```bash
source venv/bin/activate
bifurc2midi --version
```
