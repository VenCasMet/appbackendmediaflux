import json
from pathlib import Path


class ReportGenerator:

    @staticmethod
    def generate(results, output_file="final_report.json"):

        report_data = []

        for job in results:

            report_data.append({

                "file_name": job.source_path.name,

                "output_file": job.output_path.name,

                "status": job.status,

                "original_size": job.original_size,

                "converted_size": job.converted_size,

                "reduction_bytes": job.reduction_bytes,

                "reduction_percent": job.reduction_percent,

                "processing_time": job.processing_time,

                "resolution": job.resolution,

                "error": job.error
            })

        with open(output_file, "w") as f:

            json.dump(report_data, f, indent=4)

        return Path(output_file)