document.addEventListener('DOMContentLoaded', () => {
    const codeInput = document.getElementById('code-input');
    const purposeInput = document.getElementById('purpose-input');
    const explainButton = document.getElementById('explain-button');
    const explanationOutput = document.getElementById('explanation-output');
    const errorMessage = document.getElementById('error-message');
    const loadingSpinner = document.getElementById('loading-spinner');

    const FASTAPI_BACKEND_URL = "https://ai-algorithm-tutor-backend.onrender.com/explain/";

    const showLoading = () => {
        explainButton.disabled = true;
        explainButton.textContent = "Analyzing...";
        loadingSpinner.classList.remove('hidden');
        explanationOutput.innerHTML = '<p>AI is analyzing your code... Please wait.</p>'; 
        errorMessage.classList.add('hidden');
    };

    const hideLoading = () => {
        explainButton.disabled = false;
        explainButton.textContent = "✨ Explain Code";
        loadingSpinner.classList.add('hidden');
    };

    const displayError = (message) => {
        errorMessage.textContent = `Error: ${message}`;
        errorMessage.classList.remove('hidden');
        explanationOutput.innerHTML = '<p>An error occurred. Please try again or check your code/purpose.</p>';
    };

    const displayExplanation = (explanation) => {
        if (typeof marked !== 'undefined') {
            explanationOutput.innerHTML = marked.parse(explanation);
        } else {
            explanationOutput.innerHTML = `<pre><code>${explanation}</code></pre>`;
            console.error("marked.js is not loaded. Displaying raw Markdown.");
        }
        explanationOutput.scrollTop = 0;
    };

    explainButton.addEventListener('click', async () => {
        const code = codeInput.value.trim();
        const purpose = purposeInput.value.trim();

        if (!code) {
            displayError("Please enter some code to explain.");
            return;
        }

        showLoading();

        try {
            const payload = {
                code: code,
                purpose: purpose || null
            };

            const response = await fetch(FASTAPI_BACKEND_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            if (response.ok) {
                const data = await response.json();
                displayExplanation(data.explanation || "No explanation received.");
            } else {
                const errorData = await response.json();
                displayError(errorData.detail || `Server returned status ${response.status}`);
            }

        } catch (error) {
            console.error("Fetch error:", error);
            displayError("Could not connect to the analysis service. Is the backend running?");
        } finally {
            hideLoading();
        }
    });

    // Initial message on load
    explanationOutput.innerHTML = '<p>The explanation will appear here after you click the button.</p>';
});
