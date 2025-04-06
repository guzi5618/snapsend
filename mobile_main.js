document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('upload-form');
    const fileInput = document.getElementById('file-input');
    const uploadButton = document.getElementById('upload-button');
    const progressBar = document.getElementById('progress');
    const progressBarContainer = document.getElementById('progress-bar');
    const uploadStatus = document.getElementById('upload-status');
    
    // Shared files elements
    const sharedFilesList = document.getElementById('shared-files');
    const refreshButton = document.getElementById('refresh-button');
    
    // Initial fetch of shared files
    fetchSharedFiles();
    
    // Refresh button for shared files
    if (refreshButton) {
        refreshButton.addEventListener('click', () => {
            fetchSharedFiles();
        });
    }
    
    // Function to fetch shared files from desktop
    function fetchSharedFiles() {
        fetch('/api/shared-files')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(files => {
                updateSharedFilesList(files);
            })
            .catch(error => {
                console.error('Error fetching shared files:', error);
                if (sharedFilesList) {
                    sharedFilesList.innerHTML = '<li class="error">Error loading shared files. Please try again.</li>';
                }
            });
    }
    
    // Update the shared files list
    function updateSharedFilesList(files) {
        if (!sharedFilesList) return;
        
        sharedFilesList.innerHTML = '';
        
        if (files.length === 0) {
            const emptyMessage = document.createElement('li');
            emptyMessage.textContent = 'No files shared from desktop yet';
            emptyMessage.className = 'empty-message';
            sharedFilesList.appendChild(emptyMessage);
            return;
        }
        
        // Add files to the list
        files.forEach(file => {
            addSharedFileToList(file);
        });
    }
    
    // Add a shared file to the list
    function addSharedFileToList(file) {
        // Create list item
        const li = document.createElement('li');
        
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
        
        // Add file info elements to container
        fileInfoContainer.appendChild(fileName);
        fileInfoContainer.appendChild(fileDate);
        
        // Create download link
        const downloadLink = document.createElement('a');
        downloadLink.href = `/shared_files/${file.name}`;
        downloadLink.textContent = 'Download';
        downloadLink.download = file.name;
        
        // Add elements to the list item
        li.appendChild(fileInfoContainer);
        li.appendChild(downloadLink);
        
        // Add to the list
        sharedFilesList.appendChild(li);
    }
    
    // 监听文件选择，使用更强力的方式重置进度条
    fileInput.addEventListener('change', () => {
        console.log('文件选择改变了');
        
        // 强制重置进度条
        resetProgressBar();
        
        const files = fileInput.files;
        if (files.length === 0) {
            uploadStatus.textContent = '未选择任何文件';
            return;
        }
        
        // 显示选择的文件名
        if (files.length === 1) {
            uploadStatus.textContent = `已选择: ${files[0].name} (${formatFileSize(files[0].size)})`;
        } else {
            uploadStatus.textContent = `已选择 ${files.length} 个文件`;
        }
    });
    
    // 重置进度条的函数
    function resetProgressBar() {
        // 先移除进度条
        progressBar.style.width = '0%';
        // 强制浏览器重绘
        void progressBar.offsetWidth;
        console.log('进度条已重置');
    }
    
    // Handle form submission
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        
        const files = fileInput.files;
        
        if (files.length === 0) {
            uploadStatus.textContent = 'Please select at least one file';
            return;
        }
        
        // 重置进度条
        resetProgressBar();
        
        uploadStatus.textContent = `Preparing to upload ${files.length} file(s)...`;
        
        // Upload files one by one
        uploadFiles(Array.from(files));
    });
    
    function uploadFiles(files, index = 0) {
        if (index >= files.length) {
            uploadStatus.textContent = 'All files uploaded successfully!';
            progressBar.style.width = '100%';
            return;
        }
        
        const file = files[index];
        uploadFile(file)
            .then(() => {
                // Update progress
                const progress = ((index + 1) / files.length) * 100;
                progressBar.style.width = `${progress}%`;
                
                // Upload next file
                uploadFiles(files, index + 1);
            })
            .catch(error => {
                uploadStatus.textContent = `Error uploading ${file.name}: ${error.message}`;
                console.error(error);
            });
    }
    
    function uploadFile(file) {
        return new Promise((resolve, reject) => {
            uploadStatus.textContent = `Uploading ${file.name}...`;
            
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
                    fetch('/upload', {
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
                        console.log('Upload successful:', data);
                        resolve();
                    })
                    .catch(error => {
                        console.error('Upload error:', error);
                        reject(error);
                    });
                } else {
                    // File too large for this demo
                    uploadStatus.textContent = `File ${file.name} is too large (max 10MB)`;
                    reject(new Error('File too large (max 10MB)'));
                }
            };
            
            reader.onerror = function() {
                reject(new Error('Could not read the file'));
            };
            
            reader.readAsArrayBuffer(file);
        });
    }
    
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
    
    // 格式化文件大小
    function formatFileSize(bytes) {
        if (bytes < 1024) return bytes + ' bytes';
        else if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
        else if (bytes < 1073741824) return (bytes / 1048576).toFixed(1) + ' MB';
        else return (bytes / 1073741824).toFixed(1) + ' GB';
    }
    
    // Set up auto-refresh for shared files
    setInterval(fetchSharedFiles, 5000);
}); 