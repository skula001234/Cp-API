document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('decodeForm').addEventListener('submit', handleDecodeSubmit);
    document.getElementById('drmForm').addEventListener('submit', handleDrmSubmit);
});

async function handleDecodeSubmit(e) {
    e.preventDefault();
    const form = e.target;
    const responseDiv = document.getElementById('decodeResponse');
    const responseContent = document.getElementById('decodeResponseContent');
    const submitBtn = form.querySelector('button[type="submit"]');
    
    setLoading(submitBtn, true);
    hideResponse(responseDiv);
    hidePlayer();

    try {
        const payload = {
            token: document.getElementById('token').value,
            encrypted_url: document.getElementById('encryptedUrl').value,
        };
        const response = await makeApiCall('/api/decode', 'POST', payload);
        
        showResponse(responseDiv, responseContent, response, response.success);

        if (response.success && response.url) {
            playVideo(response.url);
            // Auto-fill new token in DRM form
            if (response.new_token_info && response.new_token_info.token) {
                document.getElementById('drmToken').value = response.new_token_info.token;
            }
        }
    } catch (error) {
        showResponse(responseDiv, responseContent, { error: error.message }, false);
    } finally {
        setLoading(submitBtn, false);
    }
}

async function handleDrmSubmit(e) {
    e.preventDefault();
    const form = e.target;
    const responseDiv = document.getElementById('drmResponse');
    const responseContent = document.getElementById('drmResponseContent');
    const submitBtn = form.querySelector('button[type="submit"]');

    setLoading(submitBtn, true);
    hideResponse(responseDiv);

    try {
        const payload = {
            token: document.getElementById('drmToken').value,
            video_url: document.getElementById('videoUrl').value,
        };
        const response = await makeApiCall('/api/get-keys', 'POST', payload);
        
        // Format keys in better format
        if(response.success && response.data) {
            const formattedResponse = `MPD URL:\n${response.mpd_url}\n\nKEYS:\n${response.data.join('\n')}`;
            showResponse(responseDiv, responseContent, formattedResponse, true);
        } else {
            showResponse(responseDiv, responseContent, response, false);
        }

    } catch (error) {
        showResponse(responseDiv, responseContent, { error: error.message }, false);
    } finally {
        setLoading(submitBtn, false);
    }
}

function playVideo(url) {
    const videoContainer = document.getElementById('videoContainer');
    const videoPlayer = document.getElementById('videoPlayer');
    
    if (Hls.isSupported() && url.includes('.m3u8')) {
        const hls = new Hls();
        hls.loadSource(url);
        hls.attachMedia(videoPlayer);
        hls.on(Hls.Events.MANIFEST_PARSED, () => {
            videoPlayer.play();
            videoContainer.style.display = 'block';
        });
    } else {
        videoPlayer.src = url;
        videoPlayer.play();
        videoContainer.style.display = 'block';
    }
}

function hidePlayer() {
    const videoContainer = document.getElementById('videoContainer');
    videoContainer.style.display = 'none';
    const videoPlayer = document.getElementById('videoPlayer');
    videoPlayer.pause();
    videoPlayer.src = "";
}

async function makeApiCall(endpoint, method = 'POST', data = null) {
    const options = { 
        method, 
        headers: { 'Content-Type': 'application/json' }, 
        body: data ? JSON.stringify(data) : null 
    };
    const response = await fetch(window.location.origin + endpoint, options);
    const responseData = await response.json();
    if (!response.ok) {
        throw new Error(responseData.error || responseData.details || `HTTP Error: ${response.status}`);
    }
    return responseData;
}

function setLoading(button, loading) {
    if (loading) {
        button.disabled = true;
        button.dataset.originalText = button.innerHTML;
        button.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Processing...';
    } else {
        button.disabled = false;
        button.innerHTML = button.dataset.originalText;
    }
}

function showResponse(responseDiv, contentEl, data, isSuccess) {
    contentEl.textContent = typeof data === 'string' ? data : JSON.stringify(data, null, 2);
    responseDiv.className = `mt-4 p-3 rounded ${isSuccess ? 'bg-success-subtle text-success-emphasis' : 'bg-danger-subtle text-danger-emphasis'}`;
    responseDiv.style.display = 'block';
}

function hideResponse(responseDiv) {
    responseDiv.style.display = 'none';
}
