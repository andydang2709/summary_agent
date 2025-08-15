// Global variables
let allFiles = [];
let filteredFiles = [];
let currentTab = 'today';

// Initialize the dashboard when the page loads
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
});

// Initialize dashboard
function initializeDashboard() {
    refreshFiles();
    updateStats();
    
    // Debug: List available files to see what's accessible
    setTimeout(() => {
        listAvailableFiles();
    }, 2000); // Wait 2 seconds for files to load
}

// Refresh files list
async function refreshFiles() {
    const filesList = document.getElementById('filesList');
    
    // Show loading state
    filesList.innerHTML = `
        <div class="loading">
            <i class="fas fa-sync-alt"></i>
            <p>Loading files...</p>
        </div>
    `;
    
    try {
        // Discover real files from the email_summary/logs directory
        await discoverFiles();
        

        
    } catch (error) {
        console.error('Error refreshing files:', error);
        filesList.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-exclamation-triangle"></i>
                <p>Error loading files. Please try again.</p>
                <p style="font-size: 0.8rem; margin-top: 0.5rem;">${error.message}</p>
            </div>
        `;
    }
}

// Discover real files from the email_summary/logs directory
async function discoverFiles() {
    try {
        // Make a request to scan the logs directory
        const response = await fetch('/scan-logs');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const files = await response.json();
        console.log('Raw server response:', files);
        
        // Re-process all files through parseFileInfo to ensure correct filtering
        const processedFiles = [];
        for (const file of files) {
            // If the file already has content, use it; otherwise, we'd need to fetch it
            if (file.content) {
                const processedFile = parseFileInfo(file.name, file.content);
                if (processedFile) {
                    processedFiles.push(processedFile);
                }
            } else {
                // If no content, try to fetch it
                try {
                    const fileResponse = await fetch(`/logs/${file.name}`);
                    if (fileResponse.ok) {
                        const content = await fileResponse.text();
                        const processedFile = parseFileInfo(file.name, content);
                        if (processedFile) {
                            processedFiles.push(processedFile);
                        }
                    }
                } catch (fileError) {
                    console.warn(`Could not read file ${file.name}:`, fileError);
                }
            }
        }
        
        allFiles = processedFiles;
        console.log(`Processed ${files.length} files, ${processedFiles.length} accepted files`);
        console.log('Accepted file details:', allFiles.map(f => ({ name: f.name, date: f.date, path: f.path })));
        // Apply current filters after loading files
        applyCurrentFilters();
        
    } catch (error) {
        console.error('Error scanning logs directory:', error);
        
        // Fallback: try to read files directly from the logs directory
        try {
            const files = await scanLogsDirectory();
            console.log('Fallback raw files:', files);
            
            // The scanLogsDirectory function already processes files through parseFileInfo
            allFiles = files;
            console.log(`Fallback loaded ${files.length} files`);
            console.log('Fallback file details:', allFiles.map(f => ({ name: f.name, date: f.date, path: f.path })));
            // Apply current filters after loading files
            applyCurrentFilters();
        } catch (fallbackError) {
            console.error('Fallback scanning also failed:', fallbackError);
            throw new Error('Unable to scan logs directory. Please ensure the server is running and the logs directory exists.');
        }
    }
}

// Fallback function to scan logs directory
async function scanLogsDirectory() {
    const files = [];
    
    try {
        // Try to read the logs directory listing
        const response = await fetch('/logs/');
        if (response.ok) {
            const html = await response.text();
            // Parse the directory listing to extract file information
            const fileLinks = html.match(/href="([^"]+\.txt)"/g);
            
            if (fileLinks) {
                for (const link of fileLinks) {
                    const fileName = link.match(/href="([^"]+)"/)[1];
                    if (fileName.endsWith('.txt')) {
                        try {
                            // Read the file content
                            const fileResponse = await fetch(`/logs/${fileName}`);
                            if (fileResponse.ok) {
                                                            const content = await fileResponse.text();
                            const fileInfo = parseFileInfo(fileName, content);
                            if (fileInfo) { // Only add non-null files
                                files.push(fileInfo);
                            }
                            }
                        } catch (fileError) {
                            console.warn(`Could not read file ${fileName}:`, fileError);
                        }
                    }
                }
            }
        }
        

        
    } catch (error) {
        console.error('Error in fallback scanning:', error);
    }
    
    return files;
}

// Parse file information from filename and content
function parseFileInfo(fileName, content) {
    console.log(`Processing file: ${fileName}`);
    
    // Only include files with format YYYYMMDD_email_summary_report.txt
    if (!fileName.match(/^\d{8}_email_summary_report\.txt$/)) {
        console.log(`Rejecting file: ${fileName} - doesn't match pattern`);
        return null; // This will filter out all other files
    }
    
    console.log(`Accepting file: ${fileName} - matches pattern`);
    
    // Extract date from filename (format: YYYYMMDD_*)
    let date = 'Unknown';
    const dateMatch = fileName.match(/(\d{8})/);
    if (dateMatch) {
        const dateStr = dateMatch[1];
        date = `${dateStr.substring(0, 4)}-${dateStr.substring(4, 6)}-${dateStr.substring(6, 8)}`;
    }
    
    // Calculate file size
    const size = formatFileSize(new Blob([content]).size);
    
    // Determine path
    let path = `logs/${fileName}`;
    
    return {
        name: fileName,
        type: 'summary',
        size: size,
        date: date,
        path: path,
        content: content
    };
}

// Find the corresponding storytelling file for a given date
async function findStorytellingFile(targetDate) {
    try {
        // Convert date from YYYY-MM-DD to YYYYMMDD format
        const dateParts = targetDate.split('-');
        const dateStr = dateParts.join('');
        const storytellingFileName = `${dateStr}_storytelling_summary.txt`;
        
        console.log(`Looking for storytelling file: ${storytellingFileName}`);
        console.log(`Target date: ${targetDate}, Date parts: ${dateParts}, Date string: ${dateStr}`);
        
        // Try to fetch the storytelling file from logs directory
        const logsPath = `/logs/${storytellingFileName}`;
        console.log(`Trying to fetch from: ${logsPath}`);
        
        const response = await fetch(logsPath);
        console.log(`Response status: ${response.status}, Response ok: ${response.ok}`);
        
        if (response.ok) {
            const content = await response.text();
            console.log(`Found storytelling file: ${storytellingFileName}, Content length: ${content.length}`);
            return content;
        } else {
            console.log(`Storytelling file not found: ${storytellingFileName}, Status: ${response.status}`);
            
            // Try alternative paths
            const alternativePaths = [
                `/${storytellingFileName}`,
                `/email_summary/logs/${storytellingFileName}`,
                `/email_summary/${storytellingFileName}`
            ];
            
            for (const altPath of alternativePaths) {
                console.log(`Trying alternative path: ${altPath}`);
                try {
                    const altResponse = await fetch(altPath);
                    if (altResponse.ok) {
                        const altContent = await altResponse.text();
                        console.log(`Found storytelling file at alternative path: ${altPath}, Content length: ${altContent.length}`);
                        return altContent;
                    }
                } catch (altError) {
                    console.log(`Alternative path failed: ${altPath}, Error: ${altError.message}`);
                }
            }
            
            return null;
        }
    } catch (error) {
        console.error(`Error finding storytelling file for date ${targetDate}:`, error);
        return null;
    }
}

// List all available files in logs directory for debugging
async function listAvailableFiles() {
    try {
        console.log('=== DEBUGGING: Listing available files ===');
        
        // Try to list files from logs directory
        const response = await fetch('/logs/');
        if (response.ok) {
            const html = await response.text();
            console.log('Logs directory HTML:', html);
            
            // Extract file links
            const fileLinks = html.match(/href="([^"]+\.txt)"/g);
            if (fileLinks) {
                console.log('Found file links:', fileLinks);
                const files = fileLinks.map(link => link.match(/href="([^"]+)"/)[1]);
                console.log('Available files:', files);
                
                // Check for storytelling files specifically
                const storytellingFiles = files.filter(file => file.includes('storytelling'));
                console.log('Storytelling files found:', storytellingFiles);
            }
        } else {
            console.log('Could not access logs directory, status:', response.status);
        }
        
        // Also try to access email_summary/logs
        try {
            const altResponse = await fetch('/email_summary/logs/');
            if (altResponse.ok) {
                const altHtml = await altResponse.text();
                console.log('Email summary logs directory HTML:', altHtml);
            }
        } catch (altError) {
            console.log('Could not access email_summary/logs:', altError.message);
        }
        
        console.log('=== END DEBUGGING ===');
    } catch (error) {
        console.error('Error listing available files:', error);
    }
}

// Read a specific summary aloud by date
async function readSpecificSummary(targetDate) {
    const button = event.target.closest('.btn-read-aloud');
    const originalHTML = button.innerHTML;
    
    try {
        // Disable button and show loading state
        button.disabled = true;
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        
        // Try to find the corresponding storytelling file for better TTS experience
        const storytellingContent = await findStorytellingFile(targetDate);
        if (storytellingContent) {
            console.log(`Reading storytelling summary for ${targetDate}`);
            await readTextAloudSpecific(storytellingContent, button, originalHTML);
        } else {
            // Fallback to email summary content
            const emailSummary = allFiles.find(file => file.date === targetDate);
            if (emailSummary) {
                console.log(`Reading email summary for ${targetDate} (storytelling not found)`);
                await readTextAloudSpecific(emailSummary.content, button, originalHTML);
            } else {
                throw new Error(`No summary found for date ${targetDate}`);
            }
        }
        
    } catch (error) {
        console.error('Error reading specific summary:', error);
        button.innerHTML = '<i class="fas fa-exclamation-triangle"></i>';
        button.style.background = '#ef4444';
        
        // Re-enable button after error
        setTimeout(() => {
            button.disabled = false;
            button.innerHTML = originalHTML;
            button.style.background = '';
        }, 3000);
    }
}

// Display files in the UI
function displayFiles() {
    const filesList = document.getElementById('filesList');
    
    if (filteredFiles.length === 0) {
        filesList.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-folder-open"></i>
                <p>No files found matching the current filter.</p>
                <p style="font-size: 0.8rem; margin-top: 0.5rem;">Make sure the email_summary/logs directory contains .txt files.</p>
            </div>
        `;
        return;
    }
    
    const filesHTML = filteredFiles.map(file => createFileCard(file)).join('');
    filesList.innerHTML = filesHTML;
}

// Create a file card element
function createFileCard(file) {
    return `
        <div class="file-item">
            <div class="file-header" onclick="viewFile('${file.path}')">
                <div class="file-name">${file.date}</div>
                <span class="file-type summary">Summary Report</span>
            </div>
            <div class="file-meta">
                <span class="file-size">${file.size}</span>
                <span class="file-date">${file.date}</span>
                <button class="btn btn-read-aloud" onclick="readSpecificSummary('${file.date}')" data-date="${file.date}" title="Read this summary aloud">
                    <i class="fas fa-volume-up"></i>
                </button>
            </div>
        </div>
    `;
}

// Switch between tabs
function switchTab(tabName) {
    currentTab = tabName;
    
    // Update tab button states
    document.getElementById('tab-today').classList.remove('active');
    document.getElementById('tab-all').classList.remove('active');
    document.getElementById(`tab-${tabName}`).classList.add('active');
    
    // Apply current tab filter
    applyCurrentFilters();
}

// Apply current filters (tab + file type filter)
function applyCurrentFilters() {
    let filtered = [...allFiles];
    console.log(`Applying filters: currentTab=${currentTab}, total files=${allFiles.length}`);
    
    // Apply tab filter first
    if (currentTab === 'today') {
        const today = new Date().toISOString().split('T')[0];
        filtered = filtered.filter(file => file.date === today);
        console.log(`Today filter applied: ${filtered.length} files for date ${today}`);
    }
    
    // Then apply file type filter
    const filterValue = document.getElementById('fileTypeFilter').value;
    if (filterValue !== 'all') {
        filtered = filtered.filter(file => file.type === filterValue);
        console.log(`Type filter applied: ${filtered.length} files of type ${filterValue}`);
    }
    
    filteredFiles = filtered;
    console.log(`Final filtered files: ${filteredFiles.length}`);
    displayFiles();
    updateStats();
}

// Filter files based on type
function filterFiles() {
    applyCurrentFilters();
}

// View file content
function viewFile(filePath) {
    const file = allFiles.find(f => f.path === filePath);
    if (!file) return;
    
    const fileViewer = document.getElementById('fileViewer');
    const viewerTitle = document.getElementById('viewerTitle');
    const fileContent = document.getElementById('fileContent');
    
    viewerTitle.textContent = `Email Summary - ${file.date}`;
    fileContent.textContent = file.content;
    
    fileViewer.style.display = 'block';
    
    // Scroll to viewer
    fileViewer.scrollIntoView({ behavior: 'smooth' });
}

// Close file viewer
function closeViewer() {
    const fileViewer = document.getElementById('fileViewer');
    fileViewer.style.display = 'none';
}

// Update statistics
function updateStats() {
    const today = new Date().toISOString().split('T')[0];
    const todayFiles = allFiles.filter(file => file.date === today);
    
    document.getElementById('todayCount').textContent = todayFiles.length;
    document.getElementById('totalCount').textContent = allFiles.length;
    
    if (allFiles.length > 0) {
        const latestFile = allFiles.reduce((latest, current) => {
            return new Date(current.date) > new Date(latest.date) ? current : latest;
        });
        document.getElementById('latestUpdate').textContent = latestFile.date;
    } else {
        document.getElementById('latestUpdate').textContent = '-';
    }
}

// Format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// Search functionality (can be added later)
function searchFiles(query) {
    if (!query.trim()) {
        filteredFiles = [...allFiles];
    } else {
        filteredFiles = allFiles.filter(file => 
            file.date.toLowerCase().includes(query.toLowerCase()) ||
            file.content.toLowerCase().includes(query.toLowerCase())
        );
    }
    displayFiles();
}

// Export functionality (can be added later)
function exportFile(filePath) {
    const file = allFiles.find(f => f.path === filePath);
    if (!file) return;
    
    const blob = new Blob([file.content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${file.date}_email_summary_report.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeViewer();
    }
});

// Text-to-speech functionality
let speechSynthesis = window.speechSynthesis;
let currentUtterance = null;
let isPaused = false;
let pausedText = '';
let pausedPosition = 0;

// Read today's email summary aloud
async function readTodaysSummary() {
    const button = document.getElementById('readButton');
    const status = document.getElementById('readingStatus');
    const statusText = document.getElementById('statusText');
    
    try {
        // Disable button and show status
        button.disabled = true;
        status.style.display = 'flex';
        statusText.textContent = 'Finding today\'s summary...';
        
        // Find today's summary report
        const today = new Date().toISOString().split('T')[0];
        const todaysSummary = allFiles.find(file => 
            file.type === 'summary' && file.date === today
        );
        
        if (!todaysSummary) {
            // Try to find any summary report
            const anySummary = allFiles.find(file => file.type === 'summary');
            if (anySummary) {
                statusText.textContent = `Reading latest summary (${anySummary.date})...`;
                
                // Try to find the corresponding storytelling file for better TTS experience
                const storytellingContent = await findStorytellingFile(anySummary.date);
                if (storytellingContent) {
                    console.log('Using storytelling content for TTS');
                    await readTextAloud(storytellingContent, button, status, statusText);
                } else {
                    console.log('Storytelling file not found, using email summary content for TTS');
                    await readTextAloud(anySummary.content, button, status, statusText);
                }
            } else {
                throw new Error('No summary report found. Please generate a summary first.');
            }
        } else {
            statusText.textContent = 'Reading today\'s summary...';
            
            // Try to find the corresponding storytelling file for better TTS experience
            const storytellingContent = await findStorytellingFile(todaysSummary.date);
            if (storytellingContent) {
                console.log('Using storytelling content for TTS');
                await readTextAloud(storytellingContent, button, status, statusText);
            } else {
                console.log('Storytelling file not found, using email summary content for TTS');
                await readTextAloud(todaysSummary.content, button, status, statusText);
            }
        }
        
    } catch (error) {
        console.error('Error reading summary:', error);
        statusText.textContent = `Error: ${error.message}`;
        status.style.background = 'rgba(239, 68, 68, 0.1)';
        status.style.color = '#dc2626';
        
        // Re-enable button after error
        setTimeout(() => {
            button.disabled = false;
            status.style.display = 'none';
            status.style.background = 'rgba(59, 130, 246, 0.1)';
            status.style.color = '#1e40af';
        }, 3000);
    }
}

// Read text aloud using text-to-speech (for main button)
async function readTextAloud(text, button, status, statusText) {
    return new Promise((resolve, reject) => {
        try {
            // Cancel any existing speech
            if (currentUtterance) {
                speechSynthesis.cancel();
            }
            
            // Create new utterance
            currentUtterance = new SpeechSynthesisUtterance(text);
            
            // Configure speech settings for more expressive reading
            currentUtterance.rate = 0.85; // Slower for better punctuation handling
            currentUtterance.pitch = 1.1; // Slightly higher pitch for more expressiveness
            currentUtterance.volume = 1.0; // Full volume
            
            // Add pauses for punctuation to make it more expressive
            const enhancedText = addPunctuationPauses(text);
            currentUtterance.text = enhancedText;
            
            // Use Google US English voice specifically
            const voices = speechSynthesis.getVoices();
            const googleUSVoice = voices.find(voice => 
                voice.name.includes('Google US English') || 
                voice.name.includes('Google US English Female') ||
                voice.name.includes('Google US English Male')
            );
            
            if (googleUSVoice) {
                currentUtterance.voice = googleUSVoice;
                console.log('Using voice:', googleUSVoice.name);
            } else {
                console.log('Google US English voice not found, using default');
            }
            
            // Set up event handlers
            currentUtterance.onstart = () => {
                statusText.textContent = 'Reading aloud...';
                button.innerHTML = '<i class="fas fa-stop"></i> Stop Reading';
                button.onclick = stopReading;
                button.disabled = false; // Re-enable button so it can be clicked
            };
            
            currentUtterance.onend = () => {
                statusText.textContent = 'Finished reading!';
                button.innerHTML = '<i class="fas fa-volume-up"></i> Read Today\'s Email Summary';
                button.onclick = readTodaysSummary;
                button.disabled = false;
                
                setTimeout(() => {
                    status.style.display = 'none';
                }, 2000);
                
                resolve();
            };
            
            currentUtterance.onerror = (event) => {
                console.error('Speech synthesis error:', event);
                statusText.textContent = 'Error reading text';
                button.innerHTML = '<i class="fas fa-volume-up"></i> Read Today\'s Email Summary';
                button.onclick = readTodaysSummary;
                button.disabled = false;
                
                setTimeout(() => {
                    status.style.display = 'none';
                }, 2000);
                
                reject(new Error('Speech synthesis failed'));
            };
            
            // Start speaking
            speechSynthesis.speak(currentUtterance);
            
        } catch (error) {
            reject(error);
        }
    });
}

// Read text aloud using text-to-speech (for specific summary buttons)
async function readTextAloudSpecific(text, button, originalHTML) {
    return new Promise((resolve, reject) => {
        try {
            // Cancel any existing speech
            if (currentUtterance) {
                speechSynthesis.cancel();
            }
            
            // Create new utterance
            currentUtterance = new SpeechSynthesisUtterance(text);
            
            // Configure speech settings for more expressive reading
            currentUtterance.rate = 0.85; // Slower for better punctuation handling
            currentUtterance.pitch = 1.1; // Slightly higher pitch for more expressiveness
            currentUtterance.volume = 1.0; // Full volume
            
            // Add pauses for punctuation to make it more expressive
            const enhancedText = addPunctuationPauses(text);
            currentUtterance.text = enhancedText;
            
            // Use Google US English voice specifically
            const voices = speechSynthesis.getVoices();
            const googleUSVoice = voices.find(voice => 
                voice.name.includes('Google US English') || 
                voice.name.includes('Google US English Female') ||
                voice.name.includes('Google US English Male')
            );
            
            if (googleUSVoice) {
                currentUtterance.voice = googleUSVoice;
                console.log('Using voice:', googleUSVoice.name);
            } else {
                console.log('Google US English voice not found, using default');
            }
            
            // Set up event handlers
            currentUtterance.onstart = () => {
                button.innerHTML = '<i class="fas fa-stop"></i>';
                button.onclick = stopReading;
                button.disabled = false; // Re-enable button so it can be clicked
                console.log('Started reading specific summary');
            };
            
            currentUtterance.onend = () => {
                button.innerHTML = originalHTML;
                button.onclick = () => readSpecificSummary(button.getAttribute('data-date') || '');
                button.disabled = false;
                console.log('Finished reading specific summary');
                resolve();
            };
            
            currentUtterance.onerror = (event) => {
                console.error('Speech synthesis error:', event);
                button.innerHTML = originalHTML;
                button.onclick = () => readSpecificSummary(button.getAttribute('data-date') || '');
                button.disabled = false;
                reject(new Error('Speech synthesis failed'));
            };
            
            // Start speaking
            speechSynthesis.speak(currentUtterance);
            
        } catch (error) {
            reject(error);
        }
    });
}

// Add pauses for punctuation to make speech more expressive
function addPunctuationPauses(text) {
    // Add longer pauses for major punctuation
    let enhancedText = text
        .replace(/\./g, '... ') // Periods get longer pause
        .replace(/!/g, '!... ') // Exclamation marks get longer pause
        .replace(/\?/g, '?... ') // Question marks get longer pause
        .replace(/:/g, ':... ') // Colons get longer pause
        .replace(/;/g, ';... ') // Semicolons get longer pause
        .replace(/,/g, ',.. ') // Commas get shorter pause
        .replace(/ - /g, '... - ... ') // Dashes get longer pause
        .replace(/\n/g, '... ') // Line breaks get longer pause
        .replace(/\n\n/g, '... ... ') // Double line breaks get even longer pause;
    
    // Clean up multiple consecutive pauses
    enhancedText = enhancedText.replace(/\.{3,}/g, '...');
    
    return enhancedText;
}

// Pause reading
function pauseReading() {
    if (currentUtterance && speechSynthesis.speaking) {
        speechSynthesis.pause();
        isPaused = true;
        pausedText = currentUtterance.text;
        
        const button = event.target.closest('button');
        if (button) {
            button.innerHTML = '<i class="fas fa-play"></i> Resume';
            button.onclick = resumeReading;
        }
        
        console.log('Speech paused');
    }
}

// Resume reading
function resumeReading() {
    if (isPaused && currentUtterance) {
        speechSynthesis.resume();
        isPaused = false;
        
        const button = event.target.closest('button');
        if (button) {
            button.innerHTML = '<i class="fas fa-pause"></i> Pause';
            button.onclick = pauseReading;
        }
        
        console.log('Speech resumed');
    }
}

// Stop reading
function stopReading() {
    if (currentUtterance && (speechSynthesis.speaking || isPaused)) {
        speechSynthesis.cancel();
        currentUtterance = null;
        isPaused = false;
        pausedText = '';
        pausedPosition = 0;
        
        // Find the button that was clicked (could be main button or specific summary button)
        const mainButton = document.getElementById('readButton');
        const specificButtons = document.querySelectorAll('.btn-read-aloud');
        
        // Reset main button
        if (mainButton) {
            mainButton.innerHTML = '<i class="fas fa-volume-up"></i> Read Today\'s Email Summary';
            mainButton.onclick = readTodaysSummary;
            mainButton.disabled = false;
        }
        
        // Reset all specific summary buttons
        specificButtons.forEach(btn => {
            btn.innerHTML = '<i class="fas fa-volume-up"></i>';
            btn.disabled = false;
            btn.style.background = '';
        });
        
        // Hide status if it exists
        const status = document.getElementById('readingStatus');
        if (status) {
            status.style.display = 'none';
        }
        
        console.log('Speech stopped by user');
    }
}



// Auto-refresh every 5 minutes
setInterval(() => {
    refreshFiles();
}, 5 * 60 * 1000);
