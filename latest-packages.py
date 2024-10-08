import subprocess
import os
import gzip
import re
import argparse
import dateutil.parser
import time
import sys

# Global variable for animation control
animation_symbol = '⣾'  # Start with the first symbol
symbols = ['⣾', '⣷', '⣯', '⣟', '⡿', '⢿', '⣻', '⣽']

# Function to get the list of installed packages using dpkg-query
def get_installed_packages():
    try:
        result = subprocess.run(
            ['dpkg-query', '-W', '-f=${binary:Package}\n'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True
        )
        return result.stdout.splitlines()  # Split the result into a list of packages
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running dpkg-query: {e}")
        return []

# Function to extract the date from the changelog file
def extract_changelog_date(pkg_name, debug):
    changelog_path = f"/usr/share/doc/{pkg_name}/changelog.Debian.gz"
    
    if os.path.exists(changelog_path):
        try:
            with gzip.open(changelog_path, 'rt') as f:  # Open the changelog file
                content = f.read()
                
                if debug:
                    print(f"First 500 characters of changelog for {pkg_name}:")
                    print(content[:500])

                # Improved regex to capture date patterns with day of the week
                date_pattern = re.compile(r'(\w{3}, \d{1,2} \w{3} \d{4} \d{2}:\d{2}:\d{2} [\+\-]\d{4})')
                match = date_pattern.search(content)
                
                if match:
                    raw_date = match.group(1)
                    
                    # Parse and format the date
                    parsed_date = dateutil.parser.parse(raw_date)
                    formatted_date = parsed_date.strftime("%Y-%m-%d %H:%M:%S %z")
                    return formatted_date  # Return formatted date
                else:
                    return "N/A"  # No valid date found

        except (OSError, IOError) as e:
            return "N/A"  # Return N/A for read errors
    else:
        return "N/A"  # Return N/A for missing changelog

# Main function to loop through installed packages and process them
def process_packages(limit=10, debug=False, all_packages=False):
    global animation_symbol
    start_time = time.time()  # Store the start time for animation
    symbol_change_time = start_time  # Track when the symbol was last changed

    installed_packages = get_installed_packages()
    
    if not installed_packages:
        print("No packages found or error occurred while fetching installed packages.")
        return

    # Store package data as a list of tuples (pkg, version, change_date)
    package_data = []

    # Set the limit of packages to process
    if all_packages or limit <= 0:
        limit = len(installed_packages)  # Process all packages if limit is 0 or --all flag is used

    count = 0
    max_length = max(len(pkg) for pkg in installed_packages)  # Find the max length of package names
    output_length = max_length + 43  # Calculate output length including package info and dots

    while count < limit:
        pkg = installed_packages[count]
        
        # Get the version using dpkg-query
        try:
            version_result = subprocess.run(
                ['dpkg-query', '-W', '-f=${Version}\n', pkg],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
                text=True
            )
            version = version_result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"Error occurred while fetching version for {pkg}: {e}")
            version = "N/A"  # Fallback for version retrieval errors

        # Extract changelog date
        change_date = extract_changelog_date(pkg, debug)

        # Store the package info in a tuple
        package_data.append((pkg, version, change_date))

        # Check if half a second has passed to update the animation symbol
        current_time = time.time()
        if current_time - symbol_change_time >= 0.5:
            symbol_change_time = current_time
            animation_symbol = symbols[(symbols.index(animation_symbol) + 1) % len(symbols)]

        # Prepare output with fixed width
        output_line = f'\r{animation_symbol} Processing package: {pkg:<{max_length}} ... '
        sys.stdout.write(output_line)
        sys.stdout.flush()

        # Clear any leftover characters
        sys.stdout.write(' ' * (output_length - len(output_line)))
        sys.stdout.flush()

        count += 1

    # Clear the line after processing
    sys.stdout.write('\r' + ' ' * output_length + '\r')  # Clear the line
    print('Latest updated packages.')  # Print completion message

    # Separate packages with valid dates and those with "N/A"
    valid_packages = [pkg for pkg in package_data if pkg[2] != "N/A"]
    na_packages = [pkg for pkg in package_data if pkg[2] == "N/A"]

    # Sort valid packages by change date in descending order
    valid_packages.sort(key=lambda x: x[2], reverse=True)

    # Combine valid packages and "N/A" packages
    sorted_packages = valid_packages + na_packages

    # Prepare output header
    print(f"{'Package':<40} {'Version':<40} {'Latest Change Date'}")
    print('-' * 120)

    # Print the collected package info
    for pkg, version, change_date in sorted_packages:
        print(f"{pkg:<40} {version:<40} {change_date}")

# Function to print version information
def print_version():
    print("Package Info Script Version 1.0")

# Run the package processing
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract latest upgraded package information from changelog ( by HomDX )")
    parser.add_argument('--debug', action='store_true', help="Enable debug output.")
    parser.add_argument('--version', action='store_true', help="Show version information.")
    parser.add_argument('--limit', type=int, default=10, help="Limit the number of packages to process (0 for all).")
    parser.add_argument('--all', action='store_true', help="Process all packages regardless of the limit.")
    
    args = parser.parse_args()
    
    if args.version:
        print_version()
    else:
        process_packages(limit=args.limit, debug=args.debug, all_packages=args.all)
