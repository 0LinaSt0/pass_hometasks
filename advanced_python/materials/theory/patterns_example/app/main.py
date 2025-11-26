# app/main.py

from fastapi import FastAPI, HTTPException
from factory.video_factory import VideoStreamHandlerFactory
from app.detectors import MotionDetector
from observer.notifier import ConsoleNotifier, EmailNotifier
from repository.movement_repository import global_repository
from adapter.email_service import ExternalEmailService
from utils.decorators import LoggingDetectorDecorator, FilterDetectorDecorator
from starlette.responses import StreamingResponse
import cv2

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Motion Detection API"}

@app.get("/video_feed")
def video_feed(stream_type: str = "Webcam", url: str = None, email: str = None):
    # Создание обработчика видеопотока через фабрику
    try:
        handler = VideoStreamHandlerFactory.create_handler(stream_type=stream_type, url=url)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    
    try:
        video = handler.get_stream()
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

    # Инициализация детектора движения с глобальным репозиторием
    detector = MotionDetector(repository=global_repository)
    
    # Применение декораторов
    detector = LoggingDetectorDecorator(detector)
    detector = FilterDetectorDecorator(detector, keyword="Motion")

    # Инициализация наблюдателей
    console_notifier = ConsoleNotifier()
    detector.attach(console_notifier)
    
    if email:
        # Инициализация реального email сервиса
        email_service = ExternalEmailService(
            smtp_server="smtp.example.com",
            smtp_port=587,
            username="your_username",
            password="your_password"
        )
        email_notifier = EmailNotifier(email_service=email_service, to_address=email)
        detector.attach(email_notifier)

    def frame_generator():
        try:
            while True:
                frame = video.get_frame()
                if frame is None:
                    break
                # Обработка кадра детектором движения с декораторами
                processed_frame = detector.process_frame(frame)
                ret, buffer = cv2.imencode('.jpg', processed_frame)
                if not ret:
                    continue
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        except Exception as e:
            print(f"Error during video processing: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")
        finally:
            video.release()

    return StreamingResponse(frame_generator(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/movements")
def get_movements():
    movements = global_repository.get_movements()
    return [{"timestamp": m.timestamp.isoformat(), "description": m.description} for m in movements]
