"""Application error types and FastAPI handlers."""

from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    def __init__(self, message: str, status_code: int = 400, code: str = "app_error"):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code


class ModelNotFoundError(AppError):
    def __init__(self, message: str | None = None):
        super().__init__(
            message
            or "AI model not found. Please download/configure the model. See models/README.md.",
            status_code=503,
            code="model_not_found",
        )


class InvalidFileError(AppError):
    def __init__(self, message: str):
        super().__init__(message, status_code=400, code="invalid_file")


class InferenceError(AppError):
    def __init__(self, message: str):
        super().__init__(message, status_code=500, code="inference_error")


async def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": True, "code": exc.code, "message": exc.message},
    )


async def unhandled_error_handler(_request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "code": "internal_error",
            "message": f"An unexpected error occurred: {exc}",
        },
    )
