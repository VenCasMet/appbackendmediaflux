from pathlib import Path
import uuid

from core.job import ConversionJob
from core.settings import FORMAT_CONFIG


class FormatTester:

    @staticmethod
    def create_temp_output(format_name):

        temp_dir = Path("temp")

        temp_dir.mkdir(exist_ok=True)

        filename = f"{uuid.uuid4()}{FORMAT_CONFIG[format_name]['extension']}"

        return temp_dir / filename

    @staticmethod
    def build_test_job(source_path, format_name):

        output_path = (
            FormatTester.create_temp_output(format_name)
        )

        return ConversionJob(
            source_path=source_path,
            output_format=format_name,
            quality=85,
            method=6,
            output_path=output_path,
            is_benchmark=True
        )