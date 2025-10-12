def export_to_pdf(drawio_file_path, output_pdf_path):
    """
    Экспорт диаграммы в PDF (требуется установленный draw.io desktop)
    Альтернативно: используйте браузерную версию draw.io для экспорта
    """
    import subprocess
    import os
    
    # Путь к draw.io desktop (измените на ваш)
    drawio_executable = "/Applications/draw.io.app/Contents/MacOS/draw.io"
    
    if os.path.exists(drawio_executable):
        subprocess.run([
            drawio_executable,
            "--export",
            "--format", "pdf",
            "--output", output_pdf_path,
            drawio_file_path
        ])
        print(f"PDF экспортирован: {output_pdf_path}")
    else:
        print("Draw.io desktop не найден. Экспортируйте через веб-версию.")

# Использование
# export_to_pdf('diagram_gantt.drawio', 'gantt_diagram.pdf')