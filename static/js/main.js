let currentSessionId = null;
let currentData = null;

// File input handling
document.getElementById('fileInput').addEventListener('change', handleFileSelect);
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const fileInfo = document.getElementById('fileInfo');
const fileName = document.getElementById('fileName');
const processBtn = document.getElementById('processBtn');

// Drag and drop
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    const files = e.dataTransfer.files;
    if (files.length > 0 && files[0].type === 'application/pdf') {
        handleFile(files[0]);
    } else {
        alert('Please drop a PDF file');
    }
});

uploadArea.addEventListener('click', () => {
    fileInput.click();
});

function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        handleFile(file);
    }
}

function handleFile(file) {
    if (file.type !== 'application/pdf') {
        alert('Please select a PDF file');
        return;
    }

    // Upload file
    const formData = new FormData();
    formData.append('file', file);

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
            return;
        }

        currentSessionId = data.session_id;
        fileName.textContent = data.filename;
        fileInfo.classList.remove('hidden');
        uploadArea.classList.add('hidden');
        processBtn.disabled = false;
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error uploading file');
    });
}

function removeFile() {
    fileInput.value = '';
    fileInfo.classList.add('hidden');
    uploadArea.classList.remove('hidden');
    processBtn.disabled = true;
    currentSessionId = null;
    hideResults();
}

// Process button
processBtn.addEventListener('click', processDocument);

function processDocument() {
    if (!currentSessionId) {
        alert('Please upload a file first');
        return;
    }

    // Show progress
    document.getElementById('progressSection').classList.remove('hidden');
    processBtn.disabled = true;
    updateProgress(10, 'Uploading file...');

    fetch('/process', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            session_id: currentSessionId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert('Error: ' + data.error);
            hideProgress();
            processBtn.disabled = false;
            return;
        }

        updateProgress(100, 'Processing complete!');
        currentData = data.data;
        
        setTimeout(() => {
            hideProgress();
            displayResults(data.data);
        }, 500);
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error processing document');
        hideProgress();
        processBtn.disabled = false;
    });
}

function updateProgress(percent, text) {
    document.getElementById('progressFill').style.width = percent + '%';
    document.getElementById('progressText').textContent = text;
}

function hideProgress() {
    document.getElementById('progressSection').classList.add('hidden');
}

function displayResults(data) {
    document.getElementById('resultsSection').classList.remove('hidden');
    
    // Summary
    document.getElementById('summaryText').textContent = data.summary || 'No summary available';
    document.getElementById('docType').textContent = data.document_type || 'N/A';
    
    // Education Levels
    const eduLevels = document.getElementById('educationLevels');
    eduLevels.innerHTML = '';
    if (data.education_levels && data.education_levels.length > 0) {
        data.education_levels.forEach(level => {
            const tag = document.createElement('span');
            tag.className = 'tag';
            tag.textContent = level;
            eduLevels.appendChild(tag);
        });
    } else {
        eduLevels.innerHTML = '<span style="color: #757575;">No education levels found</span>';
    }
    
    // States
    const states = document.getElementById('statesMentioned');
    states.innerHTML = '';
    if (data.states_mentioned && data.states_mentioned.length > 0) {
        data.states_mentioned.forEach(state => {
            const tag = document.createElement('span');
            tag.className = 'tag';
            tag.textContent = state;
            states.appendChild(tag);
        });
    } else {
        states.innerHTML = '<span style="color: #757575;">No states mentioned</span>';
    }
    
    // Entities
    const entitiesList = document.getElementById('entitiesList');
    entitiesList.innerHTML = '';
    if (data.named_entities && data.named_entities.length > 0) {
        data.named_entities.forEach(entity => {
            const card = document.createElement('div');
            card.className = 'entity-card';
            card.innerHTML = `
                <div class="entity-text">${entity.text || 'N/A'}</div>
                <div class="entity-label">${entity.label || 'N/A'}</div>
            `;
            entitiesList.appendChild(card);
        });
    } else {
        entitiesList.innerHTML = '<p style="color: #757575;">No entities found</p>';
    }
    
    // Statistics
    const statsList = document.getElementById('statisticsList');
    statsList.innerHTML = '';
    if (data.key_statistics && data.key_statistics.length > 0) {
        data.key_statistics.forEach(stat => {
            const card = document.createElement('div');
            card.className = 'stat-card';
            card.innerHTML = `
                <div class="stat-metric">${stat.metric || 'N/A'}</div>
                <div class="stat-value">${stat.value || 'N/A'}</div>
                <div class="stat-context">${stat.context || ''}</div>
            `;
            statsList.appendChild(card);
        });
    } else {
        statsList.innerHTML = '<p style="color: #757575;">No statistics found</p>';
    }
    
    // Tables
    const tablesList = document.getElementById('tablesList');
    tablesList.innerHTML = '';
    if (data.tables && data.tables.length > 0) {
        data.tables.forEach((table, index) => {
            const container = document.createElement('div');
            container.innerHTML = `<h4 style="margin-bottom: 15px; color: #1a237e;">${table.title || `Table ${index + 1}`}</h4>`;
            
            const tableDiv = document.createElement('div');
            tableDiv.className = 'table-container';
            
            if (Array.isArray(table.data) && table.data.length > 0) {
                const tableEl = document.createElement('table');
                const thead = document.createElement('thead');
                const tbody = document.createElement('tbody');
                
                // Headers
                const headers = Object.keys(table.data[0]);
                const headerRow = document.createElement('tr');
                headers.forEach(header => {
                    const th = document.createElement('th');
                    th.textContent = header;
                    headerRow.appendChild(th);
                });
                thead.appendChild(headerRow);
                
                // Rows
                table.data.forEach(row => {
                    const tr = document.createElement('tr');
                    headers.forEach(header => {
                        const td = document.createElement('td');
                        td.textContent = row[header] || '';
                        tr.appendChild(td);
                    });
                    tbody.appendChild(tr);
                });
                
                tableEl.appendChild(thead);
                tableEl.appendChild(tbody);
                tableDiv.appendChild(tableEl);
            } else {
                tableDiv.innerHTML = '<p style="color: #757575; padding: 20px;">No table data available</p>';
            }
            
            container.appendChild(tableDiv);
            tablesList.appendChild(container);
        });
    } else {
        tablesList.innerHTML = '<p style="color: #757575;">No tables found</p>';
    }
    
    // Policies
    const policiesList = document.getElementById('policiesList');
    policiesList.innerHTML = '';
    if (data.policies_schemes && data.policies_schemes.length > 0) {
        data.policies_schemes.forEach(policy => {
            const card = document.createElement('div');
            card.className = 'policy-card';
            card.innerHTML = `
                <div class="policy-name">${policy.name || 'N/A'}</div>
                <div class="policy-description">${policy.description || 'No description available'}</div>
                <div class="policy-target">Target: ${policy.target_audience || 'N/A'}</div>
            `;
            policiesList.appendChild(card);
        });
    } else {
        policiesList.innerHTML = '<p style="color: #757575;">No policies or schemes found</p>';
    }
    
    // Scroll to results
    document.getElementById('resultsSection').scrollIntoView({ behavior: 'smooth' });
}

function hideResults() {
    document.getElementById('resultsSection').classList.add('hidden');
    currentData = null;
}

// Tabs
function showTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-pane').forEach(pane => {
        pane.classList.remove('active');
    });
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(tabName + 'Tab').classList.add('active');
    event.target.classList.add('active');
}

// Download functions
function downloadCSV() {
    if (!currentSessionId) {
        alert('No data to download');
        return;
    }
    window.location.href = `/download/csv?session_id=${currentSessionId}`;
}

function downloadPDF() {
    if (!currentSessionId) {
        alert('No data to download');
        return;
    }
    window.location.href = `/download/pdf?session_id=${currentSessionId}`;
}


