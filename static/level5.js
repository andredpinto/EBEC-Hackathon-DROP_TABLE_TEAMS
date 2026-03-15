async function uploadLevel5CSV() {
    const fileInput = document.getElementById('level5CsvFile');
    const file = fileInput && fileInput.files ? fileInput.files[0] : null;

    if (!file) {
        alert('Please select a CSV file to upload.');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/level5/upload', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const result = await response.json();
            window.location.href = '/level5/results?filename=' + encodeURIComponent(result.filename);
        } else {
            const error = await response.json().catch(() => ({ detail: 'Upload failed' }));
            alert('Error: ' + (error.detail || 'Upload failed'));
        }
    } catch (err) {
        console.error('Upload error:', err);
        alert('Error uploading file. Please try again.');
    }
}
