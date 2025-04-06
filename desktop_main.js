document.addEventListener('DOMContentLoaded', () => {
    const qrcodeContainer = document.getElementById('qrcode');
    const connectionStatus = document.getElementById('connection-status');
    const fileStatus = document.getElementById('file-status');
    const filesList = document.getElementById('files');
    
    // Desktop upload elements
    const uploadFormDesktop = document.getElementById('upload-form-desktop');
    const fileInputDesktop = document.getElementById('file-input-desktop');
    const progressBarDesktop = document.getElementById('progress-desktop');
    const uploadStatusDesktop = document.getElementById('upload-status-desktop');
    
    // Set to track known files to avoid duplicate notifications
    const knownFiles = new Set();
    
    // Start polling for new files
    startPollingForFiles();
    
    // Generate QR code with the current URL
    generateQRCode();
    
    // Handle desktop file uploads
    if (uploadFormDesktop) {
        // Listen for file selection
        fileInputDesktop.addEventListener('change', () => {
            console.log('Desktop file selection changed');
            
            // Reset progress bar
            resetProgressBarDesktop();
            
            const files = fileInputDesktop.files;
            if (files.length === 0) {
                uploadStatusDesktop.textContent = 'No files selected';
                return;
            }
            
            // Show selected file name
            if (files.length === 1) {
                uploadStatusDesktop.textContent = `Selected: ${files[0].name} (${formatFileSize(files[0].size)})`;
            } else {
                uploadStatusDesktop.textContent = `Selected ${files.length} files`;
            }
        });
        
        // Handle form submission
        uploadFormDesktop.addEventListener('submit', (e) => {
            e.preventDefault();
            
            const files = fileInputDesktop.files;
            
            if (files.length === 0) {
                uploadStatusDesktop.textContent = 'Please select at least one file';
                return;
            }
            
            // Reset progress bar
            resetProgressBarDesktop();
            
            uploadStatusDesktop.textContent = `Preparing to upload ${files.length} file(s) to mobile...`;
            
            // Upload files one by one
            uploadFilesToMobile(Array.from(files));
        });
        
        function resetProgressBarDesktop() {
            // Reset the progress bar
            progressBarDesktop.style.width = '0%';
            // Force browser repaint
            void progressBarDesktop.offsetWidth;
            console.log('Desktop progress bar reset');
        }
        
        function uploadFilesToMobile(files, index = 0) {
            if (index >= files.length) {
                uploadStatusDesktop.textContent = 'All files uploaded successfully!';
                progressBarDesktop.style.width = '100%';
                return;
            }
            
            const file = files[index];
            uploadFileToMobile(file)
                .then(() => {
                    // Update progress
                    const progress = ((index + 1) / files.length) * 100;
                    progressBarDesktop.style.width = `${progress}%`;
                    
                    // Upload next file
                    uploadFilesToMobile(files, index + 1);
                })
                .catch(error => {
                    uploadStatusDesktop.textContent = `Error uploading ${file.name}: ${error.message}`;
                    console.error(error);
                });
        }
        
        function uploadFileToMobile(file) {
            return new Promise((resolve, reject) => {
                uploadStatusDesktop.textContent = `Uploading ${file.name} to mobile...`;
                
                // Read the file
                const reader = new FileReader();
                
                reader.onload = function(e) {
                    const fileData = e.target.result;
                    
                    // For small files (less than 10MB), upload directly
                    if (file.size < 10 * 1024 * 1024) {
                        // Convert ArrayBuffer to Base64
                        const base64Data = arrayBufferToBase64(fileData);
                        
                        // Create JSON payload
                        const payload = {
                            fileName: file.name,
                            fileType: file.type,
                            fileSize: file.size,
                            fileData: base64Data
                        };
                        
                        // Send via HTTP POST
                        fetch('/upload-to-mobile', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify(payload)
                        })
                        .then(response => {
                            if (!response.ok) {
                                throw new Error(`Server returned ${response.status}`);
                            }
                            return response.json();
                        })
                        .then(data => {
                            console.log('Upload to mobile successful:', data);
                            resolve();
                        })
                        .catch(error => {
                            console.error('Upload to mobile error:', error);
                            reject(error);
                        });
                    } else {
                        // File too large for this demo
                        uploadStatusDesktop.textContent = `File ${file.name} is too large (max 10MB)`;
                        reject(new Error('File too large (max 10MB)'));
                    }
                };
                
                reader.onerror = function() {
                    reject(new Error('Could not read the file'));
                };
                
                reader.readAsArrayBuffer(file);
            });
        }
    }
    
    function startPollingForFiles() {
        // Update the status
        connectionStatus.textContent = 'Server running. Scan QR code with your mobile device.';
        
        // Fetch files immediately and then start polling
        fetchFileList();
        
        // Poll for file updates every 3 seconds
        setInterval(fetchFileList, 3000);
    }
    
    function fetchFileList() {
        fetch('/api/files')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(files => {
                updateFileList(files);
                checkForNewFiles(files);
            })
            .catch(error => {
                console.error('Error fetching file list:', error);
            });
    }
    
    function checkForNewFiles(files) {
        // Check if there are any new files
        const newFiles = files.filter(file => !knownFiles.has(file.name));
        
        // Update the known files set
        files.forEach(file => knownFiles.add(file.name));
        
        // Notify about new files
        if (newFiles.length > 0) {
            const latestFile = newFiles[newFiles.length - 1];
            fileStatus.textContent = `Received: ${latestFile.name} (${formatFileSize(latestFile.size)})`;
            
            // Play notification sound if browser supports it
            try {
                const audio = new Audio('data:audio/mp3;base64,SUQzBAAAAAAAI1RTU0UAAAAPAAADTGF2ZjU4Ljc2LjEwMAAAAAAAAAAAAAAA//tQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAASW5mbwAAAA8AAAAeAAAjCAAKCgoKFxcXFxckJCQkJDExMTExPj4+Pj5LS0tLS1hYWFhYZWVlZWVyenp6enp6h4eHh5SUlJSUoaGhoaGurq6urru7u7u7yMjIyMjV1dXV1eLi4uLi7+/v7+/v/Pz8/PwjCAAjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjI//7UGQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEluZm8AAAAPAAAAHgAAIwgACgoKChcXFxcXJCQkJCQxMTExMT4+Pj4+S0tLS0tYWFhYWGVlZWVlcnp6enp6eoeHh4eUlJSUlKGhoaGhrq6urq67u7u7u8jIyMjI1dXV1dXi4uLi4u/v7+/v7/z8/PwjCAAjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjI//7UGQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=');
                audio.play();
            } catch (e) {
                console.log('Browser does not support audio notifications');
            }
        }
    }
    
    function generateQRCode() {
        // Get current URL and modify for upload page
        const currentUrl = window.location.href;
        const baseUrl = currentUrl.substring(0, currentUrl.lastIndexOf('/') + 1);
        const uploadUrl = `${baseUrl}mobile.html`;
        
        // For display purposes
        connectionStatus.textContent = `Server running at ${uploadUrl}`;
        
        // Generate QR code using qrcodejs library
        qrcodeContainer.innerHTML = ''; // Clear container first
        new QRCode(qrcodeContainer, {
            text: uploadUrl,
            width: 200,
            height: 200,
            colorDark: "#000000",
            colorLight: "#ffffff",
            correctLevel: QRCode.CorrectLevel.H
        });
    }
    
    function updateFileList(files) {
        // Clear the list
        filesList.innerHTML = '';
        
        // If no files, show a message
        if (files.length === 0) {
            const emptyMessage = document.createElement('p');
            emptyMessage.textContent = 'No files received yet';
            emptyMessage.className = 'empty-message';
            filesList.appendChild(emptyMessage);
            return;
        }
        
        // Add files to the list
        files.forEach(file => {
            addFileToList(file);
        });
    }
    
    function addFileToList(file) {
        // Create list item
        const li = document.createElement('li');
        li.dataset.fileId = file.name; // 用于更新倒计时
        
        // Create file info container
        const fileInfoContainer = document.createElement('div');
        fileInfoContainer.className = 'file-info';
        
        // Create file name element
        const fileName = document.createElement('span');
        fileName.className = 'file-name';
        fileName.textContent = `${file.name} (${formatFileSize(file.size)})`;
        
        // Create file date element
        const fileDate = document.createElement('span');
        fileDate.className = 'file-date';
        fileDate.textContent = file.created || 'Unknown date';
        
        // Create file expiry element
        const fileExpires = document.createElement('span');
        fileExpires.className = 'file-expires';
        fileExpires.dataset.expiresAt = file.timestamp + 300; // 5分钟后过期
        fileExpires.dataset.expiresIn = file.expiresIn;
        updateCountdown(fileExpires);
        
        // Add file info elements to container
        fileInfoContainer.appendChild(fileName);
        fileInfoContainer.appendChild(fileDate);
        fileInfoContainer.appendChild(fileExpires);
        
        // Create download link
        const downloadLink = document.createElement('a');
        downloadLink.href = `/received_files/${file.name}`;
        downloadLink.textContent = 'Download';
        downloadLink.download = file.name;
        
        // Add elements to the list item
        li.appendChild(fileInfoContainer);
        li.appendChild(downloadLink);
        
        // Add to the list
        filesList.appendChild(li);
    }
    
    // 更新所有倒计时
    function updateAllCountdowns() {
        const countdowns = document.querySelectorAll('.file-expires');
        countdowns.forEach(updateCountdown);
    }
    
    // 更新单个倒计时
    function updateCountdown(element) {
        if (!element) return;
        
        const expiresIn = parseInt(element.dataset.expiresIn) || 0;
        
        if (expiresIn <= 0) {
            element.textContent = `Expired`;
            return;
        }
        
        const minutes = Math.floor(expiresIn / 60);
        const seconds = expiresIn % 60;
        
        element.textContent = `Expires in ${minutes}:${seconds.toString().padStart(2, '0')}`;
        
        // If less than 30 seconds, add flashing effect
        if (expiresIn < 30) {
            element.classList.add('countdown-critical');
        } else {
            element.classList.remove('countdown-critical');
        }
        
        // Update remaining time
        element.dataset.expiresIn = expiresIn - 1;
    }
    
    // 每秒更新一次倒计时
    setInterval(updateAllCountdowns, 1000);
    
    // Helper function to convert ArrayBuffer to Base64
    function arrayBufferToBase64(buffer) {
        let binary = '';
        const bytes = new Uint8Array(buffer);
        const len = bytes.byteLength;
        
        for (let i = 0; i < len; i++) {
            binary += String.fromCharCode(bytes[i]);
        }
        
        return window.btoa(binary);
    }
    
    function formatFileSize(bytes) {
        if (bytes < 1024) return bytes + ' bytes';
        else if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
        else if (bytes < 1073741824) return (bytes / 1048576).toFixed(1) + ' MB';
        else return (bytes / 1073741824).toFixed(1) + ' GB';
    }
}); 