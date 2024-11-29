from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import StreamingResponse
from io import BytesIO
import qrcode
from PIL import Image
from pydantic import BaseModel
from pyzbar.pyzbar import decode
import os

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["chrome-extension://mdkllijhcehjeibgoplgdehhoegeogcj"],  # Replace with your extension ID
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Rest of your FastAPI code...

class QRCodeRequest(BaseModel):
    data: str  # The data to encode (URL or text)
    size: int = 200  # The size of the QR code
    color: str = "black"  # Foreground color of the QR code
    bgcolor: str = "white"  # Background color of the QR code
    format: str = "png"  # Format of the QR code image (png, jpeg)
    filename: str = "qr_code"  # Filename for the QR code (default is "qr_code")


def validate_color(color_name: str) -> bool:
    """Validate the color name by attempting to create an image."""
    try:
        Image.new("RGB", (10, 10), color_name)
        return True
    except ValueError:
        return False


@app.post("/generate_qr/")
async def generate_qr(request: QRCodeRequest):
    try:
        # Validate colors
        if not validate_color(request.color):
            raise HTTPException(status_code=400, detail=f"Invalid color: {request.color}")
        if not validate_color(request.bgcolor):
            raise HTTPException(status_code=400, detail=f"Invalid background color: {request.bgcolor}")

        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(request.data)
        qr.make(fit=True)

        # Create an image from the QR code
        img = qr.make_image(fill_color=request.color, back_color=request.bgcolor)

        # Save the image to a file (server side saving)
        file_path = f"{request.filename}.{request.format.lower()}"
        img.save(file_path)

        # Save the image to a BytesIO object for download as well
        img_io = BytesIO()
        img.save(img_io, format=request.format.upper())
        img_io.seek(0)

        # Return the image as a downloadable response with the custom filename
        return StreamingResponse(
            img_io,
            media_type=f"image/{request.format.lower()}",
            headers={
                "Content-Disposition": f"attachment; filename={request.filename}.{request.format.lower()}"
            },
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating QR code: {str(e)}")


@app.post("/decode_qr/")
async def decode_qr(file: UploadFile = File(...)):
    try:
        # Open the uploaded image file
        img = Image.open(file.file)

        # Decode the QR code in the image
        decoded_objects = decode(img)

        if decoded_objects:
            # Extract the data from the decoded QR code
            data = decoded_objects[0].data.decode("utf-8")
            return {"decoded_data": data}
        else:
            raise HTTPException(status_code=400, detail="No QR code found in the image")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error decoding QR code: {str(e)}")
