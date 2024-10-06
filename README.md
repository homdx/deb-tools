# Package Info Script

This Python script extracts information about installed packages on a Debian-based system using the `dpkg-query` command. It can display package names, their versions, and the latest change dates from their changelogs. 

## Features

- Optionally limits the number of displayed packages.
- Supports debug mode for detailed output.
- Allows fetching all package data while still limiting the displayed output.

## Requirements

- Python 3.x
- Necessary libraries: `dateutil` (you can install it via pip if it's not already installed):

  ```bash
  pip install python-dateutil

## Usage

To use the script, run it from the command line. Here are the available options:
`python3 latest-packages.py [OPTIONS]`

`--debug`: Enable debug output to show the first 500 characters of each changelog.

`--version`: Display the version information of the script.

`--limit <N>`: Limit the number of packages processed and displayed. (Default: 10)

`--all`: Process all installed packages regardless of the limit specified.

## Examples

Show version information:

```bash
python3 latest-packages.py --version
```

Limit output to the first 10 packages:

```bash
python3 latest-packages.py --limit 10
```

Fetch all installed packages:

```bash
python3 latest-packages.py --all
```

Fetch all packages but display only the first 20 results:

```bash
python3 latest-packages.py --all --limit 20
```

Enable debug output for the first 10 packages:

```bash
python3 latest-packages.py --debug --limit 10
```

## How It Works

1. **Retrieving Installed Packages**: The script retrieves all installed packages using `dpkg-query`.
2. **Extracting Information**: It then extracts the version and changelog date for each package.
3. **Processing Indicator**: While processing the packages, an animated symbol indicates ongoing activity.
4. **Displaying Results**: The results are displayed in a formatted table showing package name, version, and latest change date.
