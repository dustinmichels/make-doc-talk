import argparse
import os
import sys
from docling.document_converter import DocumentConverter
from rich.console import Console
from rich.panel import Panel

console = Console()


def extract_pdf(path):
    console.print(
        f"[bold blue]Stage 1:[/bold blue] Extracting text from [cyan]{path}[/cyan] with Docling..."
    )

    # Initialize Docling converter
    # This will automatically handle model downloads if needed on the first run
    converter = DocumentConverter()
    result = converter.convert(path)

    # Export to markdown as it preserves structure better than plain text
    return result.document.export_to_markdown()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Stage 1: Extract text from PDF (using Docling)"
    )
    parser.add_argument("pdf_path", help="Path to the input PDF file")
    args = parser.parse_args()

    # Validate input file
    if not os.path.exists(args.pdf_path):
        console.print(
            f"[bold red]Error:[/bold red] The file '[yellow]{args.pdf_path}[/yellow]' does not exist."
        )
        sys.exit(1)

    # Determine output directory based on PDF filename
    pdf_name = os.path.splitext(os.path.basename(args.pdf_path))[0]
    output_dir = os.path.join("out", pdf_name)
    os.makedirs(output_dir, exist_ok=True)

    try:
        # Perform extraction
        raw_content = extract_pdf(args.pdf_path)

        # Save output
        # Using 'extracted.txt' to maintain compatibility with 2-refine-text.py
        output_path = os.path.join(output_dir, "extracted.txt")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(raw_content)

        console.print(
            Panel(
                f"[green]Success![/green] Extracted text saved to [bold]{output_path}[/bold]",
                title="Extraction Complete",
                border_style="green",
            )
        )

    except Exception as e:
        console.print(f"[bold red]An error occurred during extraction:[/bold red] {e}")
        console.print_exception()
        sys.exit(1)
