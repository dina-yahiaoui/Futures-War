// Futures-War Image Generator Frontend

async function generateImage() {
    const promptInput = document.getElementById('prompt-input').value.trim();
    const errorDiv = document.getElementById('error-message');
    const successDiv = document.getElementById('success-message');
    const imageContainer = document.getElementById('image-container');
    
    // Clear previous messages
    errorDiv.innerHTML = '';
    successDiv.innerHTML = '';
    imageContainer.innerHTML = '';
    
    if (!promptInput) {
        errorDiv.innerHTML = '⚠️ Please enter a prompt';
        return;
    }
    
    try {
        const response = await fetch('/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ prompt: promptInput })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            // SFW validation failed
            if (data.error && data.error.includes('Content policy')) {
                errorDiv.innerHTML = `
                    <div style="color: #d32f2f; padding: 12px; border-radius: 4px; background-color: #ffebee; border-left: 4px solid #d32f2f;">
                        <strong>🚫 Content Policy Violation</strong><br>
                        ${data.error}
                        <br><small>Please ensure your prompt is Safe For Work (SFW)</small>
                    </div>
                `;
            } else {
                errorDiv.innerHTML = `<div style="color: #d32f2f;">❌ Error: ${data.error}</div>`;
            }
            return;
        }
        
        // Success
        successDiv.innerHTML = `
            <div style="color: #388e3c; padding: 12px; border-radius: 4px; background-color: #e8f5e9; border-left: 4px solid #388e3c;">
                ✅ Image generated successfully!<br>
                <small>Original: "${data.original_prompt}"</small>
            </div>
        `;
        
        // Display image
        if (data.image_path) {
            imageContainer.innerHTML = `
                <img src="${data.image_path}" alt="Generated image" style="max-width: 100%; border-radius: 8px; margin-top: 12px;">
                <p style="font-size: 0.9em; color: #666; margin-top: 8px;">
                    <strong>Final Prompt:</strong> ${data.prompt}
                </p>
            `;
        }
        
    } catch (error) {
        errorDiv.innerHTML = `<div style="color: #d32f2f;">❌ Network error: ${error.message}</div>`;
    }
}

// Allow Enter key to trigger generation
document.addEventListener('DOMContentLoaded', function() {
    const promptInput = document.getElementById('prompt-input');
    if (promptInput) {
        promptInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                generateImage();
            }
        });
    }
});
