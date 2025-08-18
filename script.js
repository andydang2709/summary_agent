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
    console.log('🚀 Initializing dashboard...');
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
    
    console.log('🔄 Refreshing files...');
    
    // Show loading state
    filesList.innerHTML = `
        <div class="loading">
            <i class="fas fa-sync-alt"></i>
            <p>Loading files...</p>
        </div>
    `;
    
    try {
        // Discover real files from the static file index (GitHub Pages compatible)
        await discoverFiles();
        
        console.log('✅ Files refreshed successfully');
        
    } catch (error) {
        console.error('❌ Error refreshing files:', error);
        filesList.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-exclamation-triangle"></i>
                <p>Error loading files. Please try again.</p>
                <p style="font-size: 0.8rem; margin-top: 0.5rem;">${error.message}</p>
            </div>
        `;
    }
}

// Discover real files from the data repository (GitHub Pages deployment)
async function discoverFiles() {
    try {
        // Configuration for data repository
        const DATA_REPO_URL = 'https://andydang2709.github.io/email-summary-data';
        
        console.log(`🔍 Attempting to load from data repository: ${DATA_REPO_URL}`);
        
        // Try to load from the data repository file index first
        const response = await fetch(`${DATA_REPO_URL}/file_index.json`);
        if (response.ok) {
            const data = await response.json();
            console.log('✅ Loaded from data repository file index:', data);
            
            // Process files from the index
            const processedFiles = [];
            for (const file of data.files) {
                // Files from the index already have content, so we can use them directly
                const processedFile = parseFileInfo(file.name, file.content);
                if (processedFile) {
                    processedFiles.push(processedFile);
                }
            }
            
            allFiles = processedFiles;
            console.log(`📁 Processed ${data.files.length} files from data repository, ${processedFiles.length} accepted files`);
            console.log('✅ Accepted file details:', allFiles.map(f => ({ name: f.name, date: f.date, path: f.path })));
            
            // Apply current filters after loading files
            applyCurrentFilters();
            return;
        }
        
        // Fallback: try to read files directly from the data repository
        console.log('⚠️ Data repository file index not found, trying direct file access...');
        const files = await scanDataRepository();
        console.log('📁 Fallback raw files:', files);
        
        // The scanDataRepository function already processes files through parseFileInfo
        allFiles = files;
        console.log(`📊 Fallback loaded ${files.length} files`);
        console.log('📋 Fallback file details:', allFiles.map(f => ({ name: f.name, date: f.date, path: f.path })));
        
        // Apply current filters after loading files
        applyCurrentFilters();
        
    } catch (error) {
        console.error('❌ Error discovering files:', error);
        throw new Error('Unable to load files from data repository. Please ensure the email-summary-data repository is set up and accessible.');
    }
}

// Fallback function to scan data repository (GitHub Pages compatible)
async function scanDataRepository() {
    const files = [];
    const DATA_REPO_URL = 'https://andydang2709.github.io/email-summary-data';
    
    try {
        console.log(`🔍 Scanning data repository: ${DATA_REPO_URL}`);
        
        // Try to read individual files from the data repository (excluding storytelling files)
        const knownFiles = [
            'logs/20250817_email_summary_report.txt',
            'logs/20250816_email_summary_report.txt',
            'logs/20250815_email_summary_report.txt',
            'logs/20250814_email_summary_report.txt',
            'latest/today_email_summary_report.txt',
            'latest/executive_summary.txt'
        ];
        
        for (const filePath of knownFiles) {
            try {
                // Try to read the file content from data repository
                const fileResponse = await fetch(`${DATA_REPO_URL}/${filePath}`);
                if (fileResponse.ok) {
                    const content = await fileResponse.text();
                    const fileName = filePath.split('/').pop(); // Extract filename from path
                    const fileInfo = parseFileInfo(fileName, content);
                    if (fileInfo) {
                        files.push(fileInfo);
                        console.log(`✅ Successfully loaded from data repo: ${filePath}`);
                    }
                } else {
                    console.log(`⚠️ File not accessible from data repo: ${filePath} (${fileResponse.status})`);
                }
            } catch (fileError) {
                console.warn(`❌ Could not read file ${filePath} from data repo:`, fileError);
            }
        }
        
        // Also try latest directory for current files
        const latestFiles = ['latest/today_email_summary_report.txt', 'latest/executive_summary.txt'];
        for (const filePath of latestFiles) {
            try {
                const fileResponse = await fetch(`${DATA_REPO_URL}/${filePath}`);
                if (fileResponse.ok) {
                    const content = await fileResponse.text();
                    const fileName = filePath.split('/').pop();
                    const fileInfo = parseFileInfo(fileName, content);
                    if (fileInfo) {
                        files.push(fileInfo);
                        console.log(`✅ Successfully loaded latest file: ${fileName}`);
                    }
                }
            } catch (fileError) {
                console.warn(`❌ Could not read latest file ${filePath}:`, fileError);
            }
        }
        
    } catch (error) {
        console.error('❌ Error scanning data repository:', error);
    }
    
    return files;
}

// Parse file information from filename and content
function parseFileInfo(fileName, content) {
    console.log(`🔍 Processing file: ${fileName}`);
    
    // Accept all .txt files, not just email summary reports
    if (!fileName.endsWith('.txt')) {
        console.log(`❌ Rejecting file: ${fileName} - not a .txt file`);
        return null;
    }
    
    // Hide storytelling summary files from the main display
    if (fileName.includes('storytelling')) {
        console.log(`🚫 Hiding storytelling file: ${fileName} - not shown in main list`);
        return null;
    }
    
    console.log(`✅ Accepting file: ${fileName} - is a .txt file`);
    
    // Extract date from filename (format: YYYYMMDD_*)
    let date = 'Unknown';
    const dateMatch = fileName.match(/(\d{8})/);
    if (dateMatch) {
        const dateStr = dateMatch[1];
        date = `${dateStr.substring(0, 4)}-${dateStr.substring(4, 6)}-${dateStr.substring(6, 8)}`;
    } else if (fileName === 'today_email_summary_report.txt' || fileName === 'executive_summary.txt') {
        // Use today's date for current files
        date = new Date().toISOString().split('T')[0];
    }
    
    // Determine file type based on filename
    let fileType = 'summary';
    if (fileName.includes('executive')) {
        fileType = 'executive';
    }
    
    // Calculate file size
    const size = formatFileSize(new Blob([content]).size);
    
    // Determine path
    let path = fileName;
    if (date !== 'Unknown' && !fileName.includes('today_') && !fileName.includes('executive')) {
        path = `logs/${fileName}`;
    }
    
    console.log(`📁 File info: ${fileName} | Type: ${fileType} | Date: ${date} | Size: ${size}`);
    
    return {
        name: fileName,
        type: fileType,
        size: size,
        date: date,
        path: path,
        content: content
    };
}

// Find the corresponding storytelling file for a given date (GitHub Pages compatible)
async function findStorytellingFile(targetDate) {
    try {
        // Convert date from YYYY-MM-DD to YYYYMMDD format
        const dateParts = targetDate.split('-');
        const dateStr = dateParts.join('');
        const storytellingFileName = `${dateStr}_storytelling_summary.txt`;
        
        console.log(`Looking for storytelling file: ${storytellingFileName}`);
        console.log(`Target date: ${targetDate}, Date parts: ${dateParts}, Date string: ${dateStr}`);
        
        // Try to fetch the storytelling file from logs directory (GitHub Pages compatible)
        const logsPath = `./logs/${storytellingFileName}`;
        console.log(`Trying to fetch from: ${logsPath}`);
        
        const response = await fetch(logsPath);
        console.log(`Response status: ${response.status}, Response ok: ${response.ok}`);
        
        if (response.ok) {
            const content = await response.text();
            console.log(`Found storytelling file: ${storytellingFileName}, Content length: ${content.length}`);
            return content;
        } else {
            console.log(`Storytelling file not found: ${storytellingFileName}, Status: ${response.status}`);
            
            // Try alternative paths for GitHub Pages
            const alternativePaths = [
                `./${storytellingFileName}`,
                `./email_summary/logs/${storytellingFileName}`,
                `./email_summary/${storytellingFileName}`
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
    console.log(`🔍 Applying filters: currentTab=${currentTab}, total files=${allFiles.length}`);
    console.log(`📁 All files:`, allFiles.map(f => ({ name: f.name, date: f.date, type: f.type })));
    
    // Apply tab filter first
    if (currentTab === 'today') {
        const today = new Date().toISOString().split('T')[0];
        filtered = filtered.filter(file => file.date === today);
        console.log(`📅 Today filter applied: ${filtered.length} files for date ${today}`);
    }
    
    // Then apply file type filter
    const filterValue = document.getElementById('fileTypeFilter').value;
    if (filterValue !== 'all') {
        filtered = filtered.filter(file => file.type === filterValue);
        console.log(`🏷️ Type filter applied: ${filtered.length} files of type ${filterValue}`);
    }
    
    filteredFiles = filtered;
    console.log(`✅ Final filtered files: ${filteredFiles.length}`);
    console.log(`📋 Filtered files:`, filteredFiles.map(f => ({ name: f.name, date: f.date, type: f.type })));
    
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
