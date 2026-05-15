from pathlib import Path
import shutil
import uuid

from typing import List
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

@app.post("/upload")
async def upload_images(

    files: List[UploadFile] = File(...),

    format: str = Form("webp"),

    quality: int = Form(85),

    auto_mode: bool = Form(False)
):

    print("\n========== REQUEST ==========")
    print("FORMAT:", format)
    print("QUALITY:", quality)
    print("AUTO MODE:", auto_mode)
    print("=============================\n")

    jobs = []

    # =========================
    # CREATE JOBS
    # =========================

    for file in files:

        unique_name = (

            str(uuid.uuid4())
            + "_"
            + file.filename
        )

        save_path = (
            UPLOAD_DIR / unique_name
        )

        # SAVE ORIGINAL FILE

        with open(save_path, "wb") as buffer:

            shutil.copyfileobj(
                file.file,
                buffer
            )

        # =========================
        # AUTO MODE
        # =========================

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

        print(
            f"Selected format for "
            f"{file.filename}: "
            f"{selected_format}"
        )

        # =========================
        # OUTPUT PATH
        # =========================

        output_path = (

            OUTPUT_DIR /

            f"optimized_{unique_name}.{selected_format}"
        )

        # =========================
        # CREATE CONVERSION JOB
        # =========================

        job = ConversionJob(

            source_path=save_path,

            output_format=selected_format,

            quality=quality,

            method=6,

            output_path=output_path
        )

        jobs.append(job)

    # =========================
    # PROCESS ALL JOBS
    # =========================

    results = manager.process_batch(jobs)

    final_results = []

    # =========================
    # FORMAT RESPONSE
    # =========================

    for result in results:

        if result.status == "completed":

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
                    result.quality
            })

    # =========================
    # RETURN RESPONSE
    # =========================

    return {

        "success": True,

        "count": len(final_results),

        "auto_mode": auto_mode,

        "selected_format":
            format.upper(),

        "quality":
            quality,

        "results":
            final_results
    }
