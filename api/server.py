import time
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
from concurrent.futures import (
    ThreadPoolExecutor,
    as_completed
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

TEMP_DIR = Path("temp")

TEMP_DIR.mkdir(exist_ok=True)
app.mount(
    "/temp",
    StaticFiles(directory="temp"),
    name="temp",
)
# =========================
# MANAGER
# =========================

manager = ConversionManager()
job_registry = JobRegistry()

def cleanup_old_temp_folders(max_age_minutes=10):

    now = time.time()

    for folder in TEMP_DIR.iterdir():

        if folder.is_dir():

            folder_age = (
                now - folder.stat().st_mtime
            )

            age_minutes = (
                folder_age / 60
            )

            if age_minutes > max_age_minutes:

                try:

                    shutil.rmtree(folder)

                    print(
                        f"Deleted old temp folder: {folder}"
                    )

                except Exception as e:

                    print(
                        f"Cleanup failed for {folder}: {e}"
                    )
def cleanup_worker():

    while True:

        cleanup_old_temp_folders(
            max_age_minutes=10
        )

        time.sleep(120)

cleanup_thread = threading.Thread(
    target=cleanup_worker,
    daemon=True
)

cleanup_thread.start()
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
def process_single_job(single_job):

    result = manager.process_job(
        single_job
    )

    return result


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

    total_jobs = len(jobs)

    job_registry.update_job(

        job_id,

        {

            "status": "processing",

            "progress": 0,

            "processed_files": 0,

            "failed_files": 0,

            "current_stage":
                 f"Preparing {total_jobs} images for optimization..."
        }
    )

    with ThreadPoolExecutor(
        max_workers=2
    ) as executor:

        future_to_job = {

            executor.submit(
                process_single_job,
                single_job
            ): single_job

            for single_job in jobs
        }

        for future in as_completed(
            future_to_job
        ):

            try:

                result = future.result()

                if result is None:

                    failed += 1

                elif result.status == "completed":

                    processed += 1

                    final_results.append({

                        "filename":
                            result.source_path.name,

                        "original_file":
                            str(result.source_path).replace("\\", "/"),

                        "optimized_file":
                            str(result.output_path).replace("\\", "/"),

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
                            100,

                        "current_stage":
                            "completed",

                        "heatmap":
                            result.heatmap_path.replace("\\", "/"),

                        "comparison":
                            result.comparison_path.replace("\\", "/"),

                        "target_size_kb":
                            result.target_size_kb,

                        "target_size_enabled":
                            result.target_size_enabled
                    })

                else:

                    failed += 1

            except Exception as e:

                print(
                    f"Worker failed: {e}"
                )

                failed += 1

            current_image = processed + failed

            current_stage_message = (
    f"Optimizing image "
    f"{current_image} of {total_jobs}"
)

            batch_progress = int(

                (
                    (processed + failed)
                    / total_jobs
                ) * 100
            )

            job_registry.update_job(

    job_id,

    {

        "status": "processing",

        "progress":
            batch_progress,

        "processed_files":
            processed,

        "failed_files":
            failed,

        "results":
            final_results,

        "current_stage":
            current_stage_message
    }
)

    job_registry.update_job(

        job_id,

        {

            "status": "completed",

            "progress": 100,

            "results": final_results,

            "processed_files":
                processed,

            "failed_files":
                failed,

            "current_stage":
                f"{processed} images optimized successfully"
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

    request_dir = TEMP_DIR / batch_job_id

    request_dir.mkdir(
        parents=True,
        exist_ok=True
)

    job_registry.create_job(batch_job_id)

    jobs = []

    for file in files:

        unique_name = (
            str(uuid.uuid4())
            + "_"
            + file.filename
        )

        save_path = (
            request_dir / unique_name
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
            request_dir /
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
            "total_files": len(jobs),
            "request_dir": str(request_dir).replace("\\", "/")
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