from concurrent.futures import thread
from pathlib import Path
import shutil
import uuid
from core.job_registry import JobRegistry
import threading
from fastapi import (
    FastAPI,
    UploadFile,
    File,
    Form
)

from fastapi.middleware.cors import (
    CORSMiddleware
)
from fastapi.staticfiles import StaticFiles
from core.manager import ConversionManager
from core.job import ConversionJob

app = FastAPI()


# =========================
# CORS
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# DIRECTORIES
# =========================

UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("outputs")

UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
app.mount(
    "/uploads",
    StaticFiles(directory="uploads"),
    name="uploads",
)

app.mount(
    "/outputs",
    StaticFiles(directory="outputs"),
    name="outputs",
)
# =========================
# MANAGER
# =========================

manager = ConversionManager()
job_registry = JobRegistry()
# =========================
# HOME
# =========================

@app.get("/")
def home():

    return {
        "message": "MediaFlux API Running"
    }

# =========================
# UPLOAD + OPTIMIZE
# =========================
def process_batch_job(
    job_id,
    jobs,
    auto_mode,
    format,
    quality
):

    final_results = []

    processed = 0
    failed = 0

    for single_job in jobs:

        def live_progress_callback(updated_job):

            print(
                updated_job.progress,
                updated_job.current_stage
            )

            job_registry.update_job(

            job_id,

            {

                "status": "processing",

                "progress":
                    updated_job.progress,

                "current_stage":
                    updated_job.current_stage,

                "processed_files":
                    processed,

                "failed_files":
                    failed
            }
        )

        result = manager.process_job(

            single_job,

            progress_callback=live_progress_callback
        )
        if result is None:
            failed += 1
            continue

        job_registry.update_job(

            job_id,

            {

                "status": "processing",

                "processed_files":
                    processed,

                "failed_files":
                    failed,

                "progress": int(
                    ((processed + failed + 1) / len(jobs)) * 100
                ),

                "current_stage":
                    result.current_stage
            }
        )
        # job_registry.update_job(

        #     job_id,

        #     {

        #         "status": "processing",

        #         "processed_files": processed,

        #         "failed_files": failed,

        #         "progress": int(
        #            (
        #                 (processed + failed)
        #                 / len(results)
        #             ) * 100
        #         )
        #     }
        # )

        if result.status == "completed":

            processed += 1

            final_results.append({

                "filename":
                    result.source_path.name,

                "original_file":
                    str(result.source_path),

                "optimized_file":
                    str(result.output_path),

                "original_size_kb":
                    round(
                        result.original_size / 1024,
                        2
                    ),

                "optimized_size_kb":
                    round(
                        result.converted_size / 1024,
                        2
                    ),

                "saved_percent":
                    round(
                        result.reduction_percent,
                        2
                    ),

                "ssim":
                    round(
                        result.ssim_score,
                        4
                    ),

                "format":
                    result.output_format.upper(),

                "quality":
                    result.quality,

                "resolution":
                    result.resolution,

                "progress":
                    result.progress,

                "current_stage":
                    result.current_stage,

                "heatmap":
                    result.heatmap_path,

                "comparison":
                    result.comparison_path,

                "target_size_kb":
                    result.target_size_kb,
                
                "target_size_enabled":
                    result.target_size_enabled
                
                
            })

        else:

            failed += 1

    job_registry.update_job(

        job_id,

        {

            "status": "completed",

            "progress": 100,

            "results": final_results,

            "processed_files": processed,

            "failed_files": failed
        }
    )
@app.post("/upload")
async def upload_images(

    files: list[UploadFile] = File(...),

    format: str = Form("webp"),

    quality: int = Form(85),

    auto_mode: bool = Form(False),

    target_size_kb: int = Form(0),

    target_size_enabled: bool = Form(False),

    resize_enabled: bool = Form(False),

    resize_width: int = Form(0),

    resize_height: int = Form(0),

    keep_aspect_ratio: bool = Form(True)
):

    batch_job_id = str(uuid.uuid4())

    job_registry.create_job(batch_job_id)

    jobs = []

    for file in files:

        unique_name = (
            str(uuid.uuid4())
            + "_"
            + file.filename
        )

        save_path = (
            UPLOAD_DIR / unique_name
        )

        with open(save_path, "wb") as buffer:

            shutil.copyfileobj(
                file.file,
                buffer
            )

        if auto_mode:

            benchmark_result = (
                manager
                .benchmark_engine
                .benchmark(save_path)
            )

            if benchmark_result:

                best = benchmark_result["best"]

                selected_format = (
                    best.output_format
                )

            else:

                selected_format = "webp"

        else:

            selected_format = (
                format.lower()
            )

        output_path = (

            OUTPUT_DIR /

            f"optimized_{unique_name}.{selected_format}"
        )

        job = ConversionJob(

            source_path=save_path,

            output_format=selected_format,

            quality=quality,

            method=6,

            output_path=output_path,

            target_size_kb=target_size_kb,

            target_size_enabled=target_size_enabled,

            resize_enabled=resize_enabled,

            resize_width=resize_width,

            resize_height=resize_height,

            keep_aspect_ratio=keep_aspect_ratio,
        )

        jobs.append(job)

    job_registry.update_job(

        batch_job_id,

        {
            "status": "processing",
            "progress": 10,
            "total_files": len(jobs)
        }
    )

    thread = threading.Thread(

    target=process_batch_job,

    args=(
        batch_job_id,
        jobs,
        auto_mode,
        format,
        quality
    ),

    daemon=True
)

    thread.start()
    return {

    "success": True,

    "job_id": batch_job_id,

    "message": "Batch processing started",

    "target_size_enabled":
        target_size_enabled,

    "target_size_kb":
        target_size_kb

}
@app.get("/job/{job_id}")
def get_job_status(job_id: str):

    job = job_registry.get_job(job_id)

    if not job:

        return {
            "success": False,
            "message": "Job not found"
        }

    return {
        "success": True,
        "job": job
    }