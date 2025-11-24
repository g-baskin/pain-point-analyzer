// API Configuration
const API_BASE = 'http://localhost:8000';

// State
let painPoints = [];
let rawData = [];
let currentView = 'painpoints';
let categoryChart, severityChart;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initCharts();
    refreshData();
});

// Fetch and display data
async function refreshData() {
    try {
        // Fetch pain points
        const painPointsResponse = await axios.get(`${API_BASE}/pain-points?limit=100`);
        painPoints = painPointsResponse.data;

        // Fetch raw data
        const rawDataResponse = await axios.get(`${API_BASE}/raw-data?limit=100`);
        rawData = rawDataResponse.data;

        updateStats();
        updateCharts();

        // Display the current view
        if (currentView === 'painpoints') {
            displayPainPoints(painPoints);
        } else {
            displayRawData(rawData);
        }
    } catch (error) {
        console.error('Error fetching data:', error);
        showError('Failed to load data. Make sure the API is running on http://localhost:8000');
    }
}

// Update stats cards
function updateStats() {
    const total = painPoints.length;
    const highSeverity = painPoints.filter(p => p.severity === 'critical' || p.severity === 'high').length;
    const avgOpportunity = painPoints.length > 0
        ? Math.round(painPoints.reduce((sum, p) => sum + (p.opportunity_score || 0), 0) / painPoints.length)
        : 0;

    // Get top category
    const categories = {};
    painPoints.forEach(p => {
        categories[p.category] = (categories[p.category] || 0) + 1;
    });
    const topCategory = Object.keys(categories).reduce((a, b) =>
        categories[a] > categories[b] ? a : b, '-'
    );

    document.getElementById('totalPainPoints').textContent = total;
    document.getElementById('highSeverity').textContent = highSeverity;
    document.getElementById('avgOpportunity').textContent = avgOpportunity;
    document.getElementById('topCategory').textContent = topCategory;
}

// Initialize charts
function initCharts() {
    const categoryCtx = document.getElementById('categoryChart').getContext('2d');
    const severityCtx = document.getElementById('severityChart').getContext('2d');

    categoryChart = new Chart(categoryCtx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Pain Points',
                data: [],
                backgroundColor: 'rgba(59, 130, 246, 0.8)'
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false }
            }
        }
    });

    severityChart = new Chart(severityCtx, {
        type: 'doughnut',
        data: {
            labels: ['Critical', 'High', 'Medium', 'Low'],
            datasets: [{
                data: [0, 0, 0, 0],
                backgroundColor: [
                    'rgba(239, 68, 68, 0.8)',
                    'rgba(245, 158, 11, 0.8)',
                    'rgba(59, 130, 246, 0.8)',
                    'rgba(156, 163, 175, 0.8)'
                ]
            }]
        },
        options: {
            responsive: true
        }
    });
}

// Update charts with data
function updateCharts() {
    // Category chart
    const categories = {};
    painPoints.forEach(p => {
        categories[p.category] = (categories[p.category] || 0) + 1;
    });

    categoryChart.data.labels = Object.keys(categories);
    categoryChart.data.datasets[0].data = Object.values(categories);
    categoryChart.update();

    // Severity chart
    const severities = {
        critical: 0,
        high: 0,
        medium: 0,
        low: 0
    };
    painPoints.forEach(p => {
        severities[p.severity] = (severities[p.severity] || 0) + 1;
    });

    severityChart.data.datasets[0].data = [
        severities.critical,
        severities.high,
        severities.medium,
        severities.low
    ];
    severityChart.update();
}

// Display pain points in table
function displayPainPoints(points) {
    const tbody = document.getElementById('painPointsTable');

    if (points.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="px-6 py-4 text-center text-gray-500">No pain points found. Try scraping some data!</td></tr>';
        return;
    }

    tbody.innerHTML = points.map(p => `
        <tr class="hover:bg-gray-50">
            <td class="px-6 py-4">
                <div class="text-sm font-medium text-gray-900">${p.problem_statement}</div>
                ${p.context ? `<div class="text-sm text-gray-500 mt-1">${p.context.substring(0, 100)}...</div>` : ''}
            </td>
            <td class="px-6 py-4">
                <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                    ${p.category}
                </span>
            </td>
            <td class="px-6 py-4">
                <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getSeverityColor(p.severity)}">
                    ${p.severity}
                </span>
            </td>
            <td class="px-6 py-4">
                <div class="text-sm font-medium text-gray-900">${p.opportunity_score}/100</div>
                <div class="w-full bg-gray-200 rounded-full h-2 mt-1">
                    <div class="bg-green-600 h-2 rounded-full" style="width: ${p.opportunity_score}%"></div>
                </div>
            </td>
            <td class="px-6 py-4">
                <div class="flex flex-wrap gap-1">
                    ${(p.tags || []).slice(0, 3).map(tag => `
                        <span class="inline-flex px-2 py-1 text-xs rounded bg-gray-100 text-gray-700">${tag}</span>
                    `).join('')}
                </div>
            </td>
        </tr>
    `).join('');
}

// Switch between pain points and raw data views
function switchView(view) {
    currentView = view;

    // Update button styles
    const painPointsBtn = document.getElementById('viewPainPointsBtn');
    const rawDataBtn = document.getElementById('viewRawDataBtn');
    const extractBtn = document.getElementById('extractPainPointsBtn');
    const painPointsTableContainer = document.getElementById('painPointsTableContainer');
    const rawDataTable = document.getElementById('rawDataTable');

    if (view === 'painpoints') {
        // Activate pain points view
        painPointsBtn.classList.add('text-blue-600', 'border-b-2', 'border-blue-600');
        painPointsBtn.classList.remove('text-gray-400', 'hover:text-gray-600');
        rawDataBtn.classList.remove('text-blue-600', 'border-b-2', 'border-blue-600');
        rawDataBtn.classList.add('text-gray-400', 'hover:text-gray-600');
        extractBtn.classList.add('hidden');

        painPointsTableContainer.classList.remove('hidden');
        rawDataTable.classList.add('hidden');

        displayPainPoints(painPoints);
    } else {
        // Activate raw data view
        rawDataBtn.classList.add('text-blue-600', 'border-b-2', 'border-blue-600');
        rawDataBtn.classList.remove('text-gray-400', 'hover:text-gray-600');
        painPointsBtn.classList.remove('text-blue-600', 'border-b-2', 'border-blue-600');
        painPointsBtn.classList.add('text-gray-400', 'hover:text-gray-600');
        extractBtn.classList.remove('hidden');

        painPointsTableContainer.classList.add('hidden');
        rawDataTable.classList.remove('hidden');

        displayRawData(rawData);
    }
}

// Display raw scraped data in table
function displayRawData(data) {
    const tbody = document.getElementById('rawDataTableBody');

    if (data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="px-6 py-4 text-center text-gray-500">No raw data found. Try scraping some data!</td></tr>';
        return;
    }

    tbody.innerHTML = data.map(item => {
        // Format date
        const date = item.scraped_at ? new Date(item.scraped_at).toLocaleDateString() : 'N/A';

        // Truncate content
        const content = item.content.length > 150 ? item.content.substring(0, 150) + '...' : item.content;

        // Get metadata
        const metadata = item.source_metadata || {};
        const score = metadata.score || 0;
        const subreddit = item.subreddit || 'N/A';

        return `
            <tr class="hover:bg-gray-50">
                <td class="px-6 py-4">
                    <div class="text-sm text-gray-900 max-w-md">${content}</div>
                </td>
                <td class="px-6 py-4">
                    <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full ${item.source === 'reddit_comment' ? 'bg-purple-100 text-purple-800' : 'bg-blue-100 text-blue-800'}">
                        ${item.source === 'reddit_comment' ? '💬 Comment' : '📝 Post'}
                    </span>
                    <div class="text-xs text-gray-500 mt-1">r/${subreddit}</div>
                </td>
                <td class="px-6 py-4">
                    <div class="text-sm text-gray-700">${item.author || 'Unknown'}</div>
                </td>
                <td class="px-6 py-4">
                    <div class="text-sm font-medium text-gray-900">⬆️ ${score}</div>
                </td>
                <td class="px-6 py-4">
                    <div class="text-sm text-gray-500">${date}</div>
                </td>
                <td class="px-6 py-4">
                    ${item.url ? `<a href="${item.url}" target="_blank" class="text-blue-600 hover:underline text-sm">🔗 View</a>` : '<span class="text-gray-400 text-sm">N/A</span>'}
                </td>
            </tr>
        `;
    }).join('');
}

// Filter pain points
function filterPainPoints() {
    const categoryFilter = document.getElementById('categoryFilter').value;
    const severityFilter = document.getElementById('severityFilter').value;

    let filtered = painPoints;

    if (categoryFilter) {
        filtered = filtered.filter(p => p.category === categoryFilter);
    }

    if (severityFilter) {
        filtered = filtered.filter(p => p.severity === severityFilter);
    }

    displayPainPoints(filtered);
}

// Severity color helper
function getSeverityColor(severity) {
    const colors = {
        critical: 'bg-red-100 text-red-800',
        high: 'bg-orange-100 text-orange-800',
        medium: 'bg-blue-100 text-blue-800',
        low: 'bg-gray-100 text-gray-800'
    };
    return colors[severity] || colors.low;
}

// Keyword preset templates
const keywordPresets = {
    pricing: 'expensive, pricing, costs too much, overpriced, subscription, too costly, price increase',
    features: 'missing feature, wish there was, would be nice if, need, lacking, should have, add support for',
    performance: 'slow, laggy, crashes, freezes, takes forever, performance issue, loading time, unresponsive',
    support: 'support terrible, no response, customer service, help desk, ticket ignored, waiting for support',
    bugs: 'bug, broken, doesn\'t work, error, glitch, malfunction, issue, not working, failing',
    ux: 'confusing, hard to use, complicated, unintuitive, clunky interface, poor ux, difficult to navigate',
    integration: 'integration broken, doesn\'t sync, api issues, connection failed, not compatible with'
};

function applyKeywordPreset() {
    const preset = document.getElementById('keywordPreset').value;
    if (preset && keywordPresets[preset]) {
        document.getElementById('keywordsInput').value = keywordPresets[preset];
    }
}

// Export functions
async function exportPainPoints(format) {
    try {
        const response = await axios.get(`${API_BASE}/pain-points?limit=1000`);
        const data = response.data;

        if (format === 'csv') {
            exportCSV(data);
        } else if (format === 'json') {
            exportJSON(data);
        }
    } catch (error) {
        console.error('Error exporting:', error);
        alert('Failed to export data');
    }
}

function exportCSV(painPoints) {
    const headers = ['Problem', 'Category', 'Severity', 'Opportunity Score', 'Tags', 'Context'];
    const rows = painPoints.map(p => [
        p.problem_statement,
        p.category,
        p.severity,
        p.opportunity_score,
        (p.tags || []).join('; '),
        p.context
    ]);

    let csv = headers.join(',') + '\n';
    rows.forEach(row => {
        csv += row.map(field => `"${String(field).replace(/"/g, '""')}"`).join(',') + '\n';
    });

    downloadFile(csv, 'pain-points.csv', 'text/csv');
}

function exportJSON(painPoints) {
    const json = JSON.stringify(painPoints, null, 2);
    downloadFile(json, 'pain-points.json', 'application/json');
}

function downloadFile(content, filename, contentType) {
    const blob = new Blob([content], { type: contentType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

// Scraping modal functions
function showScrapingModal() {
    document.getElementById('scrapingModal').classList.remove('hidden');
    document.getElementById('scrapingModal').classList.add('flex');
}

function closeScrapingModal() {
    document.getElementById('scrapingModal').classList.add('hidden');
    document.getElementById('scrapingModal').classList.remove('flex');
    document.getElementById('scrapingStatus').classList.add('hidden');
}

// Start scraping
async function startScraping() {
    const subreddit = document.getElementById('subredditInput').value || 'saas';
    const keywordsInput = document.getElementById('keywordsInput').value.trim();
    const keywords = keywordsInput ? keywordsInput.split(',').map(k => k.trim()).filter(k => k) : null;
    const limit = parseInt(document.getElementById('limitInput').value) || 10;
    const sortType = document.getElementById('sortTypeInput').value;
    const timeFilter = document.getElementById('timeFilterInput').value;
    const includeComments = document.getElementById('includeCommentsInput').checked;

    document.getElementById('scrapingStatus').classList.remove('hidden');

    try {
        let scrapeResponse;

        // Choose endpoint based on user selection
        if (includeComments) {
            // Use new comment scraping endpoint
            scrapeResponse = await axios.post(`${API_BASE}/scrape/reddit-with-comments`, {
                subreddit,
                sort_type: sortType,
                keywords: keywords,
                post_limit: limit,
                comments_per_post: 50,
                time_filter: timeFilter
            });

            alert(`✅ Scraped ${scrapeResponse.data.posts_scraped} posts and ${scrapeResponse.data.comments_scraped} comments from r/${subreddit}!\n\nTotal: ${scrapeResponse.data.total_items} items`);
        } else {
            // Use new sorting endpoint
            scrapeResponse = await axios.post(`${API_BASE}/scrape/reddit-sort`, {
                subreddit,
                sort_type: sortType,
                keywords: keywords,
                limit: limit,
                time_filter: timeFilter
            });

            alert(`✅ Scraped ${scrapeResponse.data.items_scraped} posts from r/${subreddit} using '${sortType}' sort`);
        }

        // Step 2: Extract pain points
        const extractLimit = includeComments ? limit * 2 : limit;
        const extractResponse = await axios.post(`${API_BASE}/extract/pain-points?limit=${extractLimit}`);

        alert(`🧠 Extracted ${extractResponse.data.pain_points_extracted} pain points`);

        closeScrapingModal();
        refreshData();
    } catch (error) {
        console.error('Error scraping:', error);
        alert('❌ Error scraping: ' + (error.response?.data?.detail || error.message));
        document.getElementById('scrapingStatus').classList.add('hidden');
    }
}

// Error handling
function showError(message) {
    const tbody = document.getElementById('painPointsTable');
    tbody.innerHTML = `
        <tr>
            <td colspan="5" class="px-6 py-4">
                <div class="bg-red-50 border border-red-200 rounded-lg p-4">
                    <p class="text-red-800 font-medium">⚠️ ${message}</p>
                </div>
            </td>
        </tr>
    `;
}

// Subreddit discovery functions
async function loadTrendingSubreddits() {
    const container = document.getElementById('trendingContainer');
    container.classList.remove('hidden');
    container.innerHTML = '<div class="text-center py-8"><div class="text-gray-500">Loading trending subreddits...</div></div>';

    try {
        const response = await axios.get(`${API_BASE}/discover/trending`);
        const data = response.data;

        displayTrendingSubreddits(data.by_category);
    } catch (error) {
        console.error('Error loading trending subreddits:', error);
        container.innerHTML = `
            <div class="bg-red-50 border border-red-200 rounded-lg p-4">
                <p class="text-red-800 font-medium">⚠️ Error loading trending subreddits: ${error.message}</p>
            </div>
        `;
    }
}

function displayTrendingSubreddits(byCategory) {
    const container = document.getElementById('trendingContainer');

    let html = '<div class="space-y-6">';

    for (const [category, subreddits] of Object.entries(byCategory)) {
        html += `
            <div>
                <h4 class="text-lg font-semibold text-gray-900 mb-3">${category}</h4>
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        `;

        subreddits.forEach(sub => {
            const subscribers = formatNumber(sub.subscribers);
            const activeUsers = sub.active_users ? formatNumber(sub.active_users) : 'N/A';

            html += `
                <div class="border border-gray-200 rounded-lg p-4 hover:border-blue-400 hover:shadow-md transition">
                    <div class="flex justify-between items-start mb-2">
                        <div>
                            <a href="${sub.url}" target="_blank" class="text-blue-600 font-semibold hover:underline">
                                r/${sub.name}
                            </a>
                            ${sub.nsfw ? '<span class="ml-2 text-xs bg-red-100 text-red-800 px-2 py-1 rounded">NSFW</span>' : ''}
                        </div>
                    </div>
                    <p class="text-sm text-gray-600 mb-3 line-clamp-2">${sub.description || sub.title}</p>
                    <div class="flex justify-between items-center text-xs text-gray-500 mb-3">
                        <span>👥 ${subscribers} members</span>
                        <span>🟢 ${activeUsers} online</span>
                    </div>
                    <div class="flex gap-2">
                        <button onclick="viewMetadata('${sub.name}')" class="flex-1 bg-blue-600 hover:bg-blue-700 text-white px-3 py-1.5 rounded text-sm font-medium transition">
                            ℹ️ Info
                        </button>
                        <button onclick="quickScrape('${sub.name}')" class="flex-1 bg-green-600 hover:bg-green-700 text-white px-3 py-1.5 rounded text-sm font-medium transition">
                            ⚡ Scrape
                        </button>
                    </div>
                </div>
            `;
        });

        html += '</div></div>';
    }

    html += '</div>';
    container.innerHTML = html;
}

function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
}

function closeMetadataModal() {
    document.getElementById('metadataModal').classList.add('hidden');
    document.getElementById('metadataModal').classList.remove('flex');
}

async function viewMetadata(subreddit) {
    try {
        const response = await axios.get(`${API_BASE}/subreddit/${subreddit}/metadata`);
        const meta = response.data.metadata;

        // Build header
        const headerHTML = `
            <div class="flex items-start gap-3">
                <div class="bg-gradient-to-br from-blue-500 to-purple-600 text-white rounded-lg p-3 text-2xl">
                    📊
                </div>
                <div class="flex-1">
                    <h3 class="text-2xl font-bold text-gray-900">r/${meta.name}</h3>
                    <p class="text-sm text-gray-600 mt-1">${meta.title}</p>
                    ${meta.over_18 ? '<span class="inline-block mt-2 bg-red-100 text-red-800 text-xs px-2 py-1 rounded-full font-semibold">⚠️ NSFW</span>' : ''}
                </div>
            </div>
        `;

        // Build content
        const contentHTML = `
            <!-- Description -->
            <div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
                <p class="text-gray-700 leading-relaxed">${meta.description || meta.title}</p>
            </div>

            <!-- Stats Grid -->
            <div class="grid grid-cols-3 gap-4">
                <div class="bg-blue-50 rounded-lg p-4 border border-blue-200">
                    <div class="text-blue-600 text-2xl mb-1">👥</div>
                    <div class="text-2xl font-bold text-gray-900">${formatNumber(meta.subscribers)}</div>
                    <div class="text-xs text-gray-600 uppercase mt-1">Subscribers</div>
                </div>
                <div class="bg-green-50 rounded-lg p-4 border border-green-200">
                    <div class="text-green-600 text-2xl mb-1">🟢</div>
                    <div class="text-2xl font-bold text-gray-900">${meta.active_users || 'N/A'}</div>
                    <div class="text-xs text-gray-600 uppercase mt-1">Active Now</div>
                </div>
                <div class="bg-purple-50 rounded-lg p-4 border border-purple-200">
                    <div class="text-purple-600 text-2xl mb-1">📅</div>
                    <div class="text-sm font-bold text-gray-900">${new Date(meta.created_utc * 1000).toLocaleDateString()}</div>
                    <div class="text-xs text-gray-600 uppercase mt-1">Created</div>
                </div>
            </div>

            <!-- Content Settings -->
            <div>
                <h4 class="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
                    <span>📝</span> Content Settings
                </h4>
                <div class="grid grid-cols-3 gap-3">
                    <div class="flex items-center gap-2 bg-gray-50 rounded-lg p-3 border border-gray-200">
                        <span class="text-xl">${meta.allow_images ? '✅' : '❌'}</span>
                        <span class="text-sm font-medium text-gray-700">Images</span>
                    </div>
                    <div class="flex items-center gap-2 bg-gray-50 rounded-lg p-3 border border-gray-200">
                        <span class="text-xl">${meta.allow_videos ? '✅' : '❌'}</span>
                        <span class="text-sm font-medium text-gray-700">Videos</span>
                    </div>
                    <div class="flex items-center gap-2 bg-gray-50 rounded-lg p-3 border border-gray-200">
                        <span class="text-xl">${meta.submission_type === 'any' ? '📝' : meta.submission_type === 'link' ? '🔗' : '💬'}</span>
                        <span class="text-sm font-medium text-gray-700 capitalize">${meta.submission_type || 'any'}</span>
                    </div>
                </div>
            </div>

            <!-- Flairs -->
            ${meta.flairs && meta.flairs.length > 0 ? `
            <div>
                <h4 class="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
                    <span>🏷️</span> Available Flairs <span class="text-sm font-normal text-gray-500">(${meta.flairs.length})</span>
                </h4>
                <div class="flex flex-wrap gap-2">
                    ${meta.flairs.slice(0, 10).map(flair => `
                        <span class="inline-flex items-center px-3 py-1.5 bg-gradient-to-r from-blue-100 to-purple-100 text-gray-800 text-xs font-medium rounded-full border border-blue-200">
                            ${typeof flair === 'object' ? flair.text : flair}
                        </span>
                    `).join('')}
                    ${meta.flairs.length > 10 ? `<span class="text-sm text-gray-500">+${meta.flairs.length - 10} more</span>` : ''}
                </div>
            </div>
            ` : ''}

            <!-- Rules -->
            ${meta.rules && meta.rules.length > 0 ? `
            <div>
                <h4 class="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
                    <span>📋</span> Subreddit Rules <span class="text-sm font-normal text-gray-500">(${meta.rules.length})</span>
                </h4>
                <div class="space-y-2">
                    ${meta.rules.slice(0, 5).map((rule, i) => `
                        <div class="bg-gray-50 rounded-lg p-3 border border-gray-200">
                            <div class="font-semibold text-gray-900 text-sm">${i + 1}. ${typeof rule === 'object' ? rule.short_name : rule}</div>
                            ${typeof rule === 'object' && rule.description ? `<div class="text-xs text-gray-600 mt-1">${rule.description.substring(0, 150)}${rule.description.length > 150 ? '...' : ''}</div>` : ''}
                        </div>
                    `).join('')}
                    ${meta.rules.length > 5 ? `
                        <div class="text-sm text-gray-500 text-center py-2">
                            +${meta.rules.length - 5} more rules
                        </div>
                    ` : ''}
                </div>
            </div>
            ` : ''}

            <!-- Actions -->
            <div class="flex gap-3 pt-2 border-t border-gray-200">
                <a href="${meta.url}" target="_blank" class="flex-1 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-4 py-3 rounded-lg font-medium text-center transition shadow-md hover:shadow-lg">
                    🔗 Visit Subreddit
                </a>
                <button onclick="closeMetadataModal(); quickScrape('${meta.name}')" class="flex-1 bg-green-600 hover:bg-green-700 text-white px-4 py-3 rounded-lg font-medium transition shadow-md hover:shadow-lg">
                    ⚡ Quick Scrape
                </button>
            </div>
        `;

        // Inject content
        document.getElementById('metadataHeader').innerHTML = headerHTML;
        document.getElementById('metadataContent').innerHTML = contentHTML;

        // Show modal
        document.getElementById('metadataModal').classList.remove('hidden');
        document.getElementById('metadataModal').classList.add('flex');

    } catch (error) {
        console.error('Error fetching metadata:', error);
        alert(`❌ Error loading metadata for r/${subreddit}: ${error.response?.data?.detail || error.message}`);
    }
}

async function quickScrape(subreddit) {
    if (!confirm(`Start scraping r/${subreddit}?\n\nThis will scrape 20 posts with complaint keywords and comments.\n\nEstimated time: 2-5 minutes`)) {
        return;
    }

    // Create loading indicator
    const loadingDiv = document.createElement('div');
    loadingDiv.id = 'scrapeLoading';
    loadingDiv.className = 'fixed top-4 right-4 bg-blue-600 text-white px-6 py-4 rounded-lg shadow-2xl z-50 flex items-center gap-3';
    loadingDiv.innerHTML = `
        <div class="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
        <div>
            <div class="font-semibold">Scraping r/${subreddit}...</div>
            <div class="text-sm text-blue-100" id="scrapeStatus">Finding posts with complaints</div>
        </div>
    `;
    document.body.appendChild(loadingDiv);

    const updateStatus = (text) => {
        const statusEl = document.getElementById('scrapeStatus');
        if (statusEl) statusEl.textContent = text;
    };

    try {
        // Use default complaint keywords
        const keywords = ['frustrated', 'hate', 'terrible', 'worst', 'awful', 'wish there was'];

        // Step 1: Scrape with increased timeout (5 minutes)
        updateStatus('Scraping posts and comments...');
        const scrapeResponse = await axios.post(`${API_BASE}/scrape/reddit`, {
            source: 'reddit',
            subreddit,
            keywords,
            limit: 20
        }, {
            timeout: 300000  // 5 minutes
        });

        updateStatus(`Scraped ${scrapeResponse.data.items_scraped} items. Extracting pain points...`);

        // Step 2: Extract pain points with increased timeout (10 minutes)
        const extractResponse = await axios.post(`${API_BASE}/extract/pain-points?limit=20`, null, {
            timeout: 600000  // 10 minutes
        });

        // Remove loading indicator
        loadingDiv.remove();

        alert(`✅ Success!\n\n📥 Scraped: ${scrapeResponse.data.items_scraped} items\n🧠 Extracted: ${extractResponse.data.pain_points_extracted} pain points\n\nRefreshing dashboard...`);

        // Refresh the dashboard
        await refreshData();

    } catch (error) {
        // Remove loading indicator
        loadingDiv.remove();

        console.error('Error scraping:', error);

        // Better error messages
        let errorMsg = 'Unknown error';
        if (error.code === 'ECONNABORTED') {
            errorMsg = 'Request timed out. The operation is taking longer than expected. Please try with fewer items or check the server logs.';
        } else if (error.message === 'Network Error') {
            errorMsg = 'Network connection lost. The server may still be processing. Please refresh the page in a few minutes.';
        } else if (error.response?.data?.detail) {
            errorMsg = error.response.data.detail;
        } else if (error.message) {
            errorMsg = error.message;
        }

        alert('❌ Error during scraping:\n\n' + errorMsg);
    }
}

// Progress modal functions
function showProgressModal() {
    document.getElementById('progressModal').classList.remove('hidden');
    document.getElementById('progressModal').classList.add('flex');
}

function closeProgressModal() {
    document.getElementById('progressModal').classList.add('hidden');
    document.getElementById('progressModal').classList.remove('flex');
}

function updateProgressModal(processed, total, percentage) {
    // Update counters
    document.getElementById('itemsProcessed').textContent = processed;
    document.getElementById('itemsTotal').textContent = total;

    // Update progress bar
    document.getElementById('progressBar').style.width = percentage + '%';
    document.getElementById('progressPercentage').textContent = Math.round(percentage) + '%';

    // Update text
    document.getElementById('progressText').textContent = `Processing item ${processed} of ${total}...`;

    // Calculate estimated time (assuming ~4 seconds per item)
    const remainingItems = total - processed;
    const estimatedSeconds = remainingItems * 4;
    const estimatedMinutes = Math.ceil(estimatedSeconds / 60);

    if (estimatedMinutes > 0) {
        document.getElementById('estimatedTime').textContent =
            `Estimated time remaining: ~${estimatedMinutes} minute${estimatedMinutes > 1 ? 's' : ''}`;
    } else {
        document.getElementById('estimatedTime').textContent = 'Almost done...';
    }
}

async function extractPainPointsFromRaw() {
    const itemCount = rawData.length;

    if (!confirm(`🧠 Extract Pain Points?\n\nThis will analyze ${itemCount} items using Claude AI to extract structured pain points.\n\nEstimated time: ${Math.ceil(itemCount * 4 / 60)} minutes\n\nNote: Progress will be shown in real-time.`)) {
        return;
    }

    // Get initial counts
    let initialPainPointCount = painPoints.length;

    // Show progress modal
    showProgressModal();
    updateProgressModal(0, itemCount, 0);

    // Disable extract button
    const extractBtn = document.getElementById('extractPainPointsBtn');
    extractBtn.disabled = true;
    extractBtn.classList.add('opacity-50', 'cursor-not-allowed');

    try {
        // Start extraction (don't await - we'll poll instead)
        const extractionPromise = axios.post(`${API_BASE}/extract/pain-points?limit=${itemCount}`);

        // Poll for progress every 2 seconds
        const pollInterval = setInterval(async () => {
            try {
                // Fetch current pain points count
                const painPointsResponse = await axios.get(`${API_BASE}/pain-points?limit=1000`);
                const currentPainPointCount = painPointsResponse.data.length;
                const newPainPoints = currentPainPointCount - initialPainPointCount;

                // Calculate progress
                const percentage = Math.min((newPainPoints / itemCount) * 100, 99);

                // Update UI
                updateProgressModal(newPainPoints, itemCount, percentage);
            } catch (error) {
                console.error('Error polling progress:', error);
            }
        }, 2000);

        // Wait for extraction to complete
        const response = await extractionPromise;

        // Stop polling
        clearInterval(pollInterval);

        // Show 100% completion
        updateProgressModal(response.data.pain_points_extracted, itemCount, 100);

        // Wait a moment to show completion
        await new Promise(resolve => setTimeout(resolve, 1000));

        // Close progress modal
        closeProgressModal();

        // Show success message
        alert(`✅ Analysis Complete!\n\n🧠 Extracted ${response.data.pain_points_extracted} pain points\n\nSwitch to "AI-Extracted Pain Points" tab to view results.`);

        // Refresh data and switch to pain points view
        await refreshData();
        switchView('painpoints');

    } catch (error) {
        closeProgressModal();
        console.error('Error extracting pain points:', error);
        alert(`❌ Error during extraction:\n\n${error.response?.data?.detail || error.message}\n\nPlease try again or check the server logs.`);
    } finally {
        // Re-enable button
        extractBtn.disabled = false;
        extractBtn.classList.remove('opacity-50', 'cursor-not-allowed');
    }
}
