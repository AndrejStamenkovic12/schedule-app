// Provider filtering functionality for provider listing pages

function filterProviders() {
    const searchQuery = document.getElementById('searchProvider').value.toLowerCase();
    const providerCards = document.querySelectorAll('.provider-card');
    const noResults = document.getElementById('noResults');
    
    if (!providerCards || !noResults) {
        return; // Guard clause if elements don't exist
    }
    
    let visibleCount = 0;
    
    providerCards.forEach(card => {
        const name = card.dataset.name || '';
        const services = card.dataset.services || '';
        
        if (searchQuery === '' || name.includes(searchQuery) || services.includes(searchQuery)) {
            card.style.display = '';
            visibleCount++;
        } else {
            card.style.display = 'none';
        }
    });
    
    // Show/hide no results message
    if (visibleCount === 0 && searchQuery !== '') {
        noResults.style.display = 'block';
    } else {
        noResults.style.display = 'none';
    }
}

function clearSearch() {
    const searchInput = document.getElementById('searchProvider');
    if (searchInput) {
        searchInput.value = '';
        filterProviders();
    }
}

// Add event listener when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchProvider');
    if (searchInput) {
        searchInput.addEventListener('input', filterProviders);
    }
});

