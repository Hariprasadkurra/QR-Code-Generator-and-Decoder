// Get elements
const mainPage = document.getElementById("mainPage");
const encodeForm = document.getElementById("encodeForm");
const decodeForm = document.getElementById("decodeForm");
const encodeButton = document.getElementById("encodeButton");
const decodeButton = document.getElementById("decodeButton");
const backButton = document.getElementById("backButton");
const backButtonDecode = document.getElementById("backButtonDecode");
const generateButton = document.getElementById("generateButton");
const qrImage = document.getElementById("qrImage");
const saveButton = document.getElementById("saveButton");
const decodeFileButton = document.getElementById("decodeFileButton");
const decodedText = document.getElementById("decodedText");
const fileInput = document.getElementById("fileInput");

// Navigation
encodeButton.addEventListener("click", () => {
    mainPage.classList.add("hidden");
    encodeForm.classList.remove("hidden");
});

decodeButton.addEventListener("click", () => {
    mainPage.classList.add("hidden");
    decodeForm.classList.remove("hidden");
});

backButton.addEventListener("click", () => {
    encodeForm.classList.add("hidden");
    mainPage.classList.remove("hidden");
});

backButtonDecode.addEventListener("click", () => {
    decodeForm.classList.add("hidden");
    mainPage.classList.remove("hidden");
});

// Generate QR Code
generateButton.addEventListener("click", async () => {
    const data = document.getElementById("dataInput").value;
    const size = document.getElementById("sizeInput").value;
    const color = document.getElementById("colorInput").value;
    const bgcolor = document.getElementById("bgColorInput").value;
    const format = document.getElementById("formatInput").value;
    const filename = document.getElementById("filenameInput").value;

    if (!data) {
        alert("Please enter data to encode.");
        return;
    }

    try {
        const response = await fetch("http://localhost:8000/generate_qr/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ data, size, color, bgcolor, format, filename }),
        });

        if (!response.ok) throw new Error("Failed to generate QR code.");

        const qrBlob = await response.blob();
        const qrUrl = URL.createObjectURL(qrBlob);
        qrImage.src = qrUrl;
        qrImage.classList.remove("hidden");
        saveButton.classList.remove("hidden");

        saveButton.addEventListener("click", () => {
            const a = document.createElement("a");
            a.href = qrUrl;
            a.download = `${filename}.${format}`;
            a.click();
        });
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
});

// Decode QR Code
decodeFileButton.addEventListener("click", async () => {
    const file = fileInput.files[0];
    if (!file) {
        alert("Please select a file.");
        return;
    }

    try {
        const formData = new FormData();
        formData.append("file", file);

        const response = await fetch("http://localhost:8000/decode_qr/", {
            method: "POST",
            body: formData,
        });

        if (!response.ok) throw new Error("Failed to decode QR code.");

        const result = await response.json();
        decodedText.textContent = `Decoded Data: ${result.decoded_data}`;
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
});
