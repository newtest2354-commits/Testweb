class AristaDNSHub {
    constructor() {
        this.dnsData = [];
        this.filteredData = [];
        this.currentPage = 1;
        this.pageSize = 50;
        this.currentFilter = 'all';
        this.searchQuery = '';
        
        this.init();
    }
    
    async init() {
        try {
            await this.loadData();
            this.setupEventListeners();
            this.render();
        } catch (error) {
            this.showError();
        }
    }
    
    async loadData() {
        const response = await fetch('/data/dns.json');
        if (!response.ok) {
            throw new Error('Failed to load DNS data');
        }
        const data = await response.json();
        this.dnsData = data.dns || [];
        this.metadata = {
            total: data.total || 0,
            updated_at: data.updated_at || new Date().toISOString()
        };
        
        const statsResponse = await fetch('/data/stats.json');
        if (statsResponse.ok) {
            this.stats = await statsResponse.json();
        }
        
        this.filteredData = [...this.dnsData];
    }
    
    setupEventListeners() {
        document.getElementById('searchInput').addEventListener('input', (e) => {
            this.searchQuery = e.target.value.toLowerCase();
            this.currentPage = 1;
            this.filterData();
            this.render();
        });
        
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                this.currentFilter = btn.dataset.filter;
                this.currentPage = 1;
                this.filterData();
                this.render();
            });
        });
        
        document.getElementById('prevPage').addEventListener('click', () => {
            if (this.currentPage > 1) {
                this.currentPage--;
                this.render();
            }
        });
        
        document.getElementById('nextPage').addEventListener('click', () => {
            const totalPages = Math.ceil(this.filteredData.length / this.pageSize);
            if (this.currentPage < totalPages) {
                this.currentPage++;
                this.render();
            }
        });
        
        document.getElementById('retryBtn').addEventListener('click', () => {
            document.getElementById('errorModal').style.display = 'none';
            this.init();
        });
    }
    
    filterData() {
        this.filteredData = this.dnsData.filter(dns => {
            let matchesFilter = true;
            if (this.currentFilter !== 'all') {
                if (this.currentFilter === 'IPv4') {
                    matchesFilter = dns.type === 'IPv4';
                } else if (this.currentFilter === 'IPv6') {
                    matchesFilter = dns.type === 'IPv6';
                } else {
                    const inCategories = dns.categories && dns.categories.includes(this.currentFilter);
                    const inProtocols = dns.protocols && dns.protocols.includes(this.currentFilter);
                    matchesFilter = inCategories || inProtocols;
                }
            }
            
            let matchesSearch = true;
            if (this.searchQuery) {
                const searchable = [
                    dns.address,
                    dns.provider,
                    dns.name,
                    ...(dns.categories || []),
                    ...(dns.protocols || [])
                ].filter(Boolean).map(s => s.toLowerCase());
                
                matchesSearch = searchable.some(field => field.includes(this.searchQuery));
            }
            
            return matchesFilter && matchesSearch;
        });
    }
    
    render() {
        this.updateStats();
        this.renderDNS();
        this.updatePagination();
    }
    
    updateStats() {
        document.getElementById('totalDns').textContent = this.metadata.total || 0;
        document.getElementById('lastUpdated').textContent = this.formatDate(this.metadata.updated_at);
        
        if (this.stats) {
            document.getElementById('dashTotal').textContent = this.stats.total_dns || 0;
            document.getElementById('dashIPv4').textContent = this.stats.total_ipv4 || 0;
            document.getElementById('dashIPv6').textContent = this.stats.total_ipv6 || 0;
            document.getElementById('dashDoH').textContent = this.stats.total_doh || 0;
            document.getElementById('dashDoT').textContent = this.stats.total_dot || 0;
            document.getElementById('dashAdBlock').textContent = this.stats.total_adblock || 0;
            document.getElementById('dashFamily').textContent = this.stats.total_family || 0;
            document.getElementById('dashSecurity').textContent = this.stats.total_security || 0;
        }
    }
    
    renderDNS() {
        const container = document.getElementById('dnsContainer');
        const emptyState = document.getElementById('emptyState');
        
        const start = (this.currentPage - 1) * this.pageSize;
        const end = start + this.pageSize;
        const pageData = this.filteredData.slice(start, end);
        
        if (pageData.length === 0) {
            container.innerHTML = '';
            emptyState.style.display = 'block';
            return;
        }
        emptyState.style.display = 'none';
        
        container.innerHTML = pageData.map(dns => this.createDNSCard(dns)).join('');
        
        document.querySelectorAll('.copy-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const address = btn.dataset.address;
                this.copyToClipboard(address, btn);
            });
        });
    }
    
    createDNSCard(dns) {
        const categories = (dns.categories || []).map(cat => 
            `<span class="category-badge">${cat}</span>`
        ).join('');
        
        const protocols = (dns.protocols || []).map(proto => 
            `<span class="protocol-badge">${proto}</span>`
        ).join('');
        
        const address = dns.address || 'N/A';
        const provider = dns.provider || 'Unknown Provider';
        const type = dns.type || 'Unknown';
        
        return `
            <div class="dns-card glass-card">
                <div class="dns-header">
                    <span class="dns-address">${address}</span>
                    <span class="dns-status">● ACTIVE</span>
                </div>
                <div class="dns-provider">${provider}</div>
                <div class="dns-categories">${categories}</div>
                <div class="dns-protocols">${protocols}</div>
                <div class="dns-type">${type}</div>
                <div class="dns-actions">
                    <button class="copy-btn" data-address="${address}">Copy</button>
                </div>
            </div>
        `;
    }
    
    updatePagination() {
        const totalPages = Math.ceil(this.filteredData.length / this.pageSize);
        const prevBtn = document.getElementById('prevPage');
        const nextBtn = document.getElementById('nextPage');
        const pageInfo = document.getElementById('pageInfo');
        
        prevBtn.disabled = this.currentPage <= 1;
        nextBtn.disabled = this.currentPage >= totalPages;
        pageInfo.textContent = `Page ${this.currentPage} of ${totalPages || 1}`;
    }
    
    async copyToClipboard(text, button) {
        try {
            await navigator.clipboard.writeText(text);
            button.textContent = 'Copied!';
            button.classList.add('copied');
            setTimeout(() => {
                button.textContent = 'Copy';
                button.classList.remove('copied');
            }, 2000);
        } catch (err) {
            console.error('Failed to copy:', err);
        }
    }
    
    formatDate(dateString) {
        if (!dateString) return 'Never';
        try {
            const date = new Date(dateString);
            return date.toLocaleString('en-US', {
                month: 'short',
                day: 'numeric',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        } catch {
            return dateString;
        }
    }
    
    showError() {
        document.getElementById('errorModal').style.display = 'block';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new AristaDNSHub();
});
