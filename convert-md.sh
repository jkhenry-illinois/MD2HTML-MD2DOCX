#!/bin/bash

MD2HTML=~/md2html.py

echo ""
echo "What would you like to convert?"
echo "  1) A single file"
echo "  2) An entire directory of .md files"
echo ""
read -p "Enter 1 or 2: " choice

# ── Single file ────────────────────────────────────────────────────────────────
if [ "$choice" = "1" ]; then

    echo ""
    echo "Opening file chooser..."
    filepath=$(osascript -e 'POSIX path of (choose file with prompt "Select a Markdown file:")')

    if [ $? -ne 0 ] || [ -z "$filepath" ]; then
        echo "No file selected. Cancelled."
        exit 0
    fi

    filepath="${filepath%$'\n'}"

    if [ ! -f "$filepath" ]; then
        echo ""
        echo "Error: Cannot find a file at '$filepath'."
        exit 1
    fi

    output="${filepath%.md}.html"
    dir=$(dirname "$filepath")

    if [ -f "$output" ]; then
        echo ""
        echo "Warning: An HTML file already exists and will be overwritten:"
        echo "  $output"
        echo ""
        read -p "Are you sure you want to continue? (y/n): " confirm
        if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
            echo "Cancelled. Nothing was changed."
            exit 0
        fi
    fi

    echo ""
    python3 "$MD2HTML" "$filepath" -o "$output" --standalone --dir "$dir"
    echo ""
    echo "Done! Your HTML file is saved at:"
    echo "  $output"

# ── Entire directory ───────────────────────────────────────────────────────────
elif [ "$choice" = "2" ]; then

    echo ""
    echo "Opening folder chooser..."
    dirpath=$(osascript -e 'POSIX path of (choose folder with prompt "Select a folder containing Markdown files:")')

    if [ $? -ne 0 ] || [ -z "$dirpath" ]; then
        echo "No folder selected. Cancelled."
        exit 0
    fi

    dirpath="${dirpath%/}"
    dirpath="${dirpath%$'\n'}"

    if [ ! -d "$dirpath" ]; then
        echo ""
        echo "Error: Cannot find a directory at '$dirpath'."
        exit 1
    fi

    echo ""
    echo "Found directory: $dirpath"

    shopt -s nullglob
    md_files=("$dirpath"/*.md)
    shopt -u nullglob

    if [ ${#md_files[@]} -eq 0 ]; then
        echo "No .md files found in that directory. Nothing to convert."
        exit 0
    fi

    echo "Found ${#md_files[@]} Markdown file(s)."

    # Create timestamped output directory next to the source directory
    timestamp=$(date +"%Y-%m-%d_%H-%M-%S")
    parent=$(dirname "$dirpath")
    outdir="$parent/converted_$timestamp"
    mkdir -p "$outdir"

    echo ""
    converted=0
    for f in "${md_files[@]}"; do
        output="$outdir/$(basename "${f%.md}.html")"
        python3 "$MD2HTML" "$f" -o "$output" --standalone --dir "$dirpath" --nav
        converted=$((converted + 1))
    done

    echo ""
    echo "Done! Converted $converted file(s). HTML files are saved in:"
    echo "  $outdir"

# ── Invalid choice ─────────────────────────────────────────────────────────────
else
    echo ""
    echo "Invalid choice. Please run the script again and enter 1 or 2."
    exit 1
fi
