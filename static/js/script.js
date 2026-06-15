// CAMPUS TRADE Frontend JavaScript

// Helper to get the logged-in User ID from base.html meta tag
function getCurrentUserId() {
    const meta = document.querySelector('meta[name="current-user-id"]');
    return meta ? parseInt(meta.getAttribute('content'), 10) : null;
}

// Initialize on page load
window.addEventListener('load', () => {
    console.log("Local session script loaded");
    
    // Route-specific page initializations
    initPageRouter();
});

// Handle client-side routing logic depending on the active template page
function initPageRouter() {
    const path = window.location.pathname;
    
    if (path === '/') {
        initHomePage();
    } else if (path === '/listings') {
        initBrowsePage();
    } else if (path.startsWith('/listings/')) {
        const listingId = document.getElementById('listing-id-placeholder')?.value;
        if (listingId) initDetailPage(listingId);
    } else if (path === '/create-listing') {
        initCreatePage();
    } else if (path.startsWith('/edit-listing/')) {
        const listingId = document.getElementById('listing-id-placeholder')?.value;
        if (listingId) initEditPage(listingId);
    } else if (path === '/my-listings') {
        initMyListingsPage();
    } else if (path === '/profile') {
        initProfilePage();
    }
}

// --- PAGE INITIALIZATION FUNCTIONS ---

// 1. HOME PAGE
function initHomePage() {
    console.log("Loading Home Page...");
    
    const searchBtn = document.querySelector('.search-btn');
    const searchInput = document.querySelector('.search-input');
    
    if (searchBtn && searchInput) {
        const triggerSearch = () => {
            const val = searchInput.value.trim();
            window.location.href = `/listings?search=${encodeURIComponent(val)}`;
        };
        
        searchBtn.addEventListener('click', triggerSearch);
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') triggerSearch();
        });
    }
    
    loadFeaturedListings();
}

async function loadFeaturedListings() {
    const grid = document.querySelector('.listings-grid');
    if (!grid) return;
    
    grid.innerHTML = getSpinnerMarkup("Loading featured items...");
    
    try {
        const response = await fetch('/api/listings');
        if (!response.ok) throw new Error("Failed to fetch listings");
        
        const listings = await response.json();
        
        if (listings.length === 0) {
            grid.innerHTML = getEmptyStateMarkup("No listings found", "Be the first to create one!", "/create-listing", "Post an Item");
            return;
        }
        
        // Show max 4 listings
        const featured = listings.slice(0, 4);
        grid.innerHTML = '';
        featured.forEach(item => {
            grid.appendChild(createListingCard(item));
        });
    } catch (err) {
        console.error(err);
        grid.innerHTML = `<div class="alert alert-danger">Could not load featured items. Please try again later.</div>`;
    }
}

// 2. BROWSE / LISTINGS PAGE
function initBrowsePage() {
    console.log("Loading Browse Page...");
    
    const searchInput = document.querySelector('.search-input');
    const searchBtn = document.querySelector('.search-btn');
    const categoryPills = document.querySelectorAll('.category-pill');
    
    const urlParams = new URLSearchParams(window.location.search);
    let currentSearch = urlParams.get('search') || '';
    let currentCategory = urlParams.get('category') || 'all';
    
    if (searchInput) searchInput.value = currentSearch;
    
    categoryPills.forEach(pill => {
        const catValue = pill.getAttribute('data-category');
        if (catValue === currentCategory) {
            pill.classList.add('active');
        } else {
            pill.classList.remove('active');
        }
        
        pill.addEventListener('click', () => {
            categoryPills.forEach(p => p.classList.remove('active'));
            pill.classList.add('active');
            currentCategory = catValue;
            updateUrlAndFetch();
        });
    });
    
    if (searchBtn && searchInput) {
        searchBtn.addEventListener('click', () => {
            currentSearch = searchInput.value.trim();
            updateUrlAndFetch();
        });
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                currentSearch = searchInput.value.trim();
                updateUrlAndFetch();
            }
        });
    }
    
    function updateUrlAndFetch() {
        const newUrl = new URL(window.location.href);
        if (currentSearch) {
            newUrl.searchParams.set('search', currentSearch);
        } else {
            newUrl.searchParams.delete('search');
        }
        
        if (currentCategory && currentCategory !== 'all') {
            newUrl.searchParams.set('category', currentCategory);
        } else {
            newUrl.searchParams.delete('category');
        }
        
        window.history.pushState({}, '', newUrl);
        fetchBrowseListings();
    }
    
    async function fetchBrowseListings() {
        const grid = document.querySelector('.listings-grid');
        if (!grid) return;
        
        grid.innerHTML = getSpinnerMarkup("Searching the campus...");
        
        try {
            let apiPath = '/api/listings';
            const params = new URLSearchParams();
            if (currentCategory && currentCategory !== 'all') params.append('category', currentCategory);
            if (currentSearch) params.append('search', currentSearch);
            
            if (params.toString()) {
                apiPath += `?${params.toString()}`;
            }
            
            const response = await fetch(apiPath);
            if (!response.ok) throw new Error("API call failed");
            
            const listings = await response.json();
            grid.innerHTML = '';
            
            if (listings.length === 0) {
                grid.innerHTML = getEmptyStateMarkup(
                    "No items match your search",
                    "Try using different keywords or checking another category.",
                    "/listings",
                    "Clear Filters"
                );
                
                const clearBtn = grid.querySelector('.btn');
                if (clearBtn) {
                    clearBtn.addEventListener('click', (e) => {
                        e.preventDefault();
                        if (searchInput) searchInput.value = '';
                        currentSearch = '';
                        currentCategory = 'all';
                        categoryPills.forEach(p => {
                            if (p.getAttribute('data-category') === 'all') p.classList.add('active');
                            else p.classList.remove('active');
                        });
                        updateUrlAndFetch();
                    });
                }
                return;
            }
            
            listings.forEach(item => {
                grid.appendChild(createListingCard(item));
            });
            
        } catch (err) {
            console.error(err);
            grid.innerHTML = `<div class="alert alert-danger">Could not retrieve listings. Please refresh.</div>`;
        }
    }
    
    fetchBrowseListings();
}

// 3. DETAIL PAGE
async function initDetailPage(listingId) {
    console.log(`Loading Detail Page for listing ${listingId}...`);
    
    const detailContainer = document.querySelector('.listing-detail-container');
    if (!detailContainer) return;
    
    try {
        const response = await fetch(`/api/listings/${listingId}`);
        if (!response.ok) {
            if (response.status === 404) {
                detailContainer.innerHTML = getEmptyStateMarkup("Listing Not Found", "This item might have been deleted by the seller.", "/listings", "Back to Browse");
            } else {
                throw new Error("Failed to load listing");
            }
            return;
        }
        
        const item = await response.json();
        
        // Populate HTML fields
        const imgEl = document.querySelector('.detail-img');
        if (imgEl) {
            if (item.image_path) {
                imgEl.src = item.image_path;
                imgEl.alt = item.title;
                imgEl.style.display = 'block';
            } else {
                imgEl.style.display = 'none';
                const placeholder = document.createElement('div');
                placeholder.style.cssText = `
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: linear-gradient(135deg, #e0e7ff, #c7d2fe);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 1.5rem;
                    font-weight: 700;
                    color: var(--primary);
                `;
                placeholder.textContent = 'No Image Available';
                imgEl.parentElement.appendChild(placeholder);
            }
        }
        
        document.querySelector('.detail-category').textContent = item.category;
        document.querySelector('.detail-title').textContent = item.title;
        document.querySelector('.detail-price').textContent = formatCurrency(item.price);
        document.querySelector('.detail-desc').textContent = item.description;
        
        // Status Badge
        const statusBadge = document.querySelector('.detail-status-badge');
        if (statusBadge) {
            if (item.is_sold === 1) {
                statusBadge.textContent = "Sold";
                statusBadge.className = "listing-badge badge-sold detail-status-badge";
            } else {
                statusBadge.textContent = "Available";
                statusBadge.className = "listing-badge badge-available detail-status-badge";
            }
        }
        
        // Sidebar stats
        document.querySelector('.val-seller').textContent = item.seller_name;
        document.querySelector('.val-date').textContent = formatDate(item.created_at);
        document.querySelector('.val-status').textContent = item.is_sold === 1 ? 'Sold' : 'Available';
        
        // Configure Contact Details
        const contactBtn = document.querySelector('.contact-btn');
        const contactBox = document.querySelector('.contact-box');
        const contactDetail = document.querySelector('.contact-details-val');
        
        const currentUserId = getCurrentUserId();
        
        if (currentUserId !== null) {
            // User is authenticated, show contact info upon click
            if (contactBtn && contactBox && contactDetail) {
                contactDetail.textContent = item.contact_info;
                contactBtn.addEventListener('click', () => {
                    contactBox.style.display = contactBox.style.display === 'block' ? 'none' : 'block';
                    contactBtn.textContent = contactBox.style.display === 'block' ? 'Hide Details' : 'Contact Seller';
                });
            }
            
            // If the authenticated user is the seller, show Edit/Delete buttons in the sidebar
            if (currentUserId === item.seller_id) {
                showSellerManagementActions(item);
            }
        } else {
            // Unauthenticated user: prompt login
            if (contactBtn) {
                contactBtn.textContent = "Sign in to Contact Seller";
                contactBtn.addEventListener('click', () => {
                    window.location.href = `/login?next=${encodeURIComponent(window.location.pathname)}`;
                });
            }
        }
        
        document.getElementById('loading-detail-view').style.display = 'none';
        document.getElementById('loaded-detail-view').style.display = 'grid';
        
    } catch (err) {
        console.error(err);
        showNotification("Failed to load listing details.", "danger");
    }
}

function showSellerManagementActions(item) {
    const sidebar = document.querySelector('.detail-sidebar');
    if (!sidebar) return;
    
    // Remove if already exists
    const existingAdmin = sidebar.querySelector('.admin-actions');
    if (existingAdmin) existingAdmin.remove();
    
    const adminCard = document.createElement('div');
    adminCard.className = 'sidebar-card admin-actions';
    adminCard.innerHTML = `
        <h3>Your Listing</h3>
        <p style="font-size: 0.9rem; color: var(--text-secondary); margin-bottom: 1rem;">You listed this item. You can edit its details or remove it.</p>
        <div style="display: flex; flex-direction: column; gap: 0.75rem;">
            <a href="/edit-listing/${item.id}" class="btn btn-secondary" style="width: 100%;">Edit Listing</a>
            <button class="btn btn-danger delete-btn" style="width: 100%;">Delete Listing</button>
            <button class="btn btn-success status-toggle-btn" style="width: 100%;">
                ${item.is_sold === 1 ? 'Mark as Available' : 'Mark as Sold'}
            </button>
        </div>
    `;
    
    sidebar.insertBefore(adminCard, sidebar.firstChild);
    
    adminCard.querySelector('.delete-btn').addEventListener('click', async () => {
        if (confirm("Are you sure you want to delete this listing? This action cannot be undone.")) {
            await deleteListingItem(item.id);
        }
    });
    
    adminCard.querySelector('.status-toggle-btn').addEventListener('click', async () => {
        const newStatus = item.is_sold === 1 ? 0 : 1;
        await toggleSoldStatus(item.id, newStatus);
    });
}

// 4. CREATE PAGE
function initCreatePage() {
    console.log("Loading Create Listing Page...");
    
    const form = document.getElementById('create-listing-form');
    const imageInput = document.getElementById('image-upload');
    const previewImg = document.getElementById('preview-image');
    
    if (imageInput && previewImg) {
        imageInput.addEventListener('change', () => {
            const file = imageInput.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    previewImg.src = e.target.result;
                    previewImg.style.display = 'block';
                };
                reader.readAsDataURL(file);
            } else {
                previewImg.style.display = 'none';
            }
        });
    }
    
    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const title = document.getElementById('title').value.trim();
            const price = parseFloat(document.getElementById('price').value);
            const category = document.getElementById('category').value;
            const description = document.getElementById('description').value.trim();
            const contactInfo = document.getElementById('contact_info').value.trim();
            
            if (!title || isNaN(price) || !category || !description || !contactInfo) {
                showNotification("Please fill in all required fields.", "danger");
                return;
            }
            
            if (price < 0) {
                showNotification("Price cannot be negative.", "danger");
                return;
            }
            
            showLoadingState(true);
            
            try {
                const formData = new FormData(form);
                
                const response = await fetch('/api/listings', {
                    method: 'POST',
                    body: formData
                });
                
                const resData = await response.json();
                
                if (!response.ok) {
                    throw new Error(resData.error || "Failed to create listing");
                }
                
                showNotification("Listing created successfully!", "success");
                setTimeout(() => {
                    window.location.href = `/listings/${resData.listing_id}`;
                }, 1000);
                
            } catch (err) {
                console.error(err);
                showNotification(err.message, "danger");
                showLoadingState(false);
            }
        });
    }
}

// 5. EDIT PAGE
async function initEditPage(listingId) {
    console.log(`Loading Edit Listing Page for listing ${listingId}...`);
    
    const form = document.getElementById('edit-listing-form');
    const imageInput = document.getElementById('image-upload');
    const previewImg = document.getElementById('preview-image');
    
    if (!form) return;
    
    try {
        const response = await fetch(`/api/listings/${listingId}`);
        if (!response.ok) throw new Error("Failed to fetch listing data");
        
        const item = await response.json();
        const currentUserId = getCurrentUserId();
        
        if (currentUserId !== item.seller_id) {
            showNotification("You are not authorized to edit this listing.", "danger");
            setTimeout(() => { window.location.href = '/listings'; }, 1500);
            return;
        }
        
        document.getElementById('title').value = item.title;
        document.getElementById('price').value = item.price;
        document.getElementById('category').value = item.category;
        document.getElementById('description').value = item.description;
        document.getElementById('contact_info').value = item.contact_info;
        
        if (item.image_path) {
            previewImg.src = item.image_path;
            previewImg.style.display = 'block';
        }
        
        if (imageInput && previewImg) {
            imageInput.addEventListener('change', () => {
                const file = imageInput.files[0];
                if (file) {
                    const reader = new FileReader();
                    reader.onload = (e) => {
                        previewImg.src = e.target.result;
                        previewImg.style.display = 'block';
                    };
                    reader.readAsDataURL(file);
                }
            });
        }
        
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const title = document.getElementById('title').value.trim();
            const price = parseFloat(document.getElementById('price').value);
            const category = document.getElementById('category').value;
            const description = document.getElementById('description').value.trim();
            const contactInfo = document.getElementById('contact_info').value.trim();
            
            if (!title || isNaN(price) || !category || !description || !contactInfo) {
                showNotification("Please fill in all required fields.", "danger");
                return;
            }
            
            showLoadingState(true);
            
            try {
                const formData = new FormData(form);
                
                const editResponse = await fetch(`/api/listings/${listingId}`, {
                    method: 'PUT',
                    body: formData
                });
                
                const resData = await editResponse.json();
                if (!editResponse.ok) throw new Error(resData.error || "Failed to update listing");
                
                showNotification("Listing updated successfully!", "success");
                setTimeout(() => {
                    window.location.href = `/listings/${listingId}`;
                }, 1000);
                
            } catch (err) {
                console.error(err);
                showNotification(err.message, "danger");
                showLoadingState(false);
            }
        });
        
        document.getElementById('loading-edit-view').style.display = 'none';
        form.style.display = 'block';
        
    } catch (err) {
        console.error(err);
        showNotification("Failed to load listing data.", "danger");
    }
}

// 6. MY LISTINGS (DASHBOARD) PAGE
async function initMyListingsPage() {
    console.log("Loading My Listings Dashboard...");
    
    const activeContainer = document.getElementById('active-listings');
    const soldContainer = document.getElementById('sold-listings');
    
    if (!activeContainer || !soldContainer) return;
    
    activeContainer.innerHTML = getSpinnerMarkup("Loading active items...");
    soldContainer.innerHTML = getSpinnerMarkup("Loading sold items...");
    
    try {
        const currentUserId = getCurrentUserId();
        if (currentUserId === null) return;
        
        const response = await fetch(`/api/listings?seller=${currentUserId}`);
        if (!response.ok) throw new Error("Failed to fetch dashboard items");
        
        const listings = await response.json();
        
        activeContainer.innerHTML = '';
        soldContainer.innerHTML = '';
        
        const activeItems = listings.filter(item => item.is_sold === 0);
        const soldItems = listings.filter(item => item.is_sold === 1);
        
        if (activeItems.length === 0) {
            activeContainer.innerHTML = getEmptyStateMarkup("No active items", "Got something to sell? Post it today!", "/create-listing", "Post an Item");
        } else {
            const activeGrid = document.createElement('div');
            activeGrid.className = 'listings-grid';
            activeItems.forEach(item => {
                activeGrid.appendChild(createDashboardListingCard(item));
            });
            activeContainer.appendChild(activeGrid);
        }
        
        if (soldItems.length === 0) {
            soldContainer.innerHTML = `<div style="text-align: center; padding: 2rem; color: var(--text-muted);">You haven't marked any items as sold yet.</div>`;
        } else {
            const soldGrid = document.createElement('div');
            soldGrid.className = 'listings-grid';
            soldItems.forEach(item => {
                soldGrid.appendChild(createDashboardListingCard(item));
            });
            soldContainer.appendChild(soldGrid);
        }
        
    } catch (err) {
        console.error(err);
        activeContainer.innerHTML = `<div class="alert alert-danger">Error loading dashboard listings.</div>`;
        soldContainer.innerHTML = '';
    }
}

// 7. PROFILE PAGE
async function initProfilePage() {
    console.log("Loading User Profile Page...");
    
    const profileView = document.getElementById('profile-view');
    const loadingView = document.getElementById('profile-loading');
    
    if (!profileView || !loadingView) return;
    
    try {
        const response = await fetch('/api/profile');
        if (!response.ok) throw new Error("Failed to retrieve profile stats");
        
        const stats = await response.json();
        
        const nameVal = stats.name || 'Student';
        document.getElementById('prof-initial').textContent = nameVal.charAt(0).toUpperCase();
        document.getElementById('prof-name').textContent = nameVal;
        document.getElementById('prof-email').textContent = stats.email;
        document.getElementById('prof-date').textContent = formatDate(stats.created_at);
        
        document.getElementById('stat-active').textContent = stats.active_listings;
        document.getElementById('stat-sold').textContent = stats.sold_listings;
        
        loadingView.style.display = 'none';
        profileView.style.display = 'block';
        
    } catch (err) {
        console.error(err);
        showNotification("Could not retrieve profile stats.", "danger");
    }
}

// --- SHARED API HELPERS ---

async function deleteListingItem(listingId) {
    try {
        const response = await fetch(`/api/listings/${listingId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || "Delete operation failed");
        
        showNotification("Listing deleted successfully", "success");
        setTimeout(() => {
            if (window.location.pathname.startsWith('/listings/')) {
                window.location.href = '/my-listings';
            } else {
                window.location.reload();
            }
        }, 1000);
    } catch (err) {
        console.error(err);
        showNotification(err.message, "danger");
    }
}

async function toggleSoldStatus(listingId, newStatus) {
    try {
        const response = await fetch(`/api/listings/${listingId}/sold`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ is_sold: newStatus })
        });
        
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || "Update status failed");
        
        showNotification(newStatus === 1 ? "Item marked as Sold!" : "Item marked as Available", "success");
        setTimeout(() => {
            window.location.reload();
        }, 1000);
    } catch (err) {
        console.error(err);
        showNotification(err.message, "danger");
    }
}

// --- UI GENERATORS & DOM BINDINGS ---

function createListingCard(item) {
    const card = document.createElement('div');
    card.className = 'listing-card';
    
    const imgPath = item.image_path || '';
    const priceText = formatCurrency(item.price);
    const badgeClass = item.is_sold === 1 ? 'badge-sold' : 'badge-available';
    const badgeText = item.is_sold === 1 ? 'Sold' : 'Available';
    
    card.innerHTML = `
        <div class="listing-img-wrapper">
            ${imgPath ? `<img src="${imgPath}" alt="${item.title}" class="listing-img">` : '<div class="listing-img" style="background: linear-gradient(135deg, #e0e7ff, #c7d2fe); display: flex; align-items: center; justify-content: center; font-weight: bold; color: var(--primary);">No Image</div>'}
            <span class="listing-badge ${badgeClass}">${badgeText}</span>
        </div>
        <div class="listing-content">
            <span class="listing-category">${item.category}</span>
            <h3 class="listing-title">${item.title}</h3>
            <div class="listing-price-container">
                <span class="listing-price">${priceText}</span>
                <span class="listing-seller">By: ${item.seller_name}</span>
            </div>
        </div>
    `;
    
    card.addEventListener('click', () => {
        window.location.href = `/listings/${item.id}`;
    });
    
    return card;
}

function createDashboardListingCard(item) {
    const card = document.createElement('div');
    card.className = 'listing-card';
    card.style.cursor = 'default';
    
    const imgPath = item.image_path || '';
    const priceText = formatCurrency(item.price);
    const badgeClass = item.is_sold === 1 ? 'badge-sold' : 'badge-available';
    const badgeText = item.is_sold === 1 ? 'Sold' : 'Available';
    
    card.innerHTML = `
        <div class="listing-img-wrapper" style="cursor: pointer;">
            ${imgPath ? `<img src="${imgPath}" alt="${item.title}" class="listing-img">` : '<div class="listing-img" style="background: linear-gradient(135deg, #e0e7ff, #c7d2fe); display: flex; align-items: center; justify-content: center; font-weight: bold; color: var(--primary);">No Image</div>'}
            <span class="listing-badge ${badgeClass}">${badgeText}</span>
        </div>
        <div class="listing-content">
            <span class="listing-category">${item.category}</span>
            <h3 class="listing-title" style="cursor: pointer;">${item.title}</h3>
            <span class="listing-price" style="display: block; margin-top: auto; font-size: 1.2rem; font-weight: 700; margin-bottom: 0.75rem;">${priceText}</span>
            
            <div style="display: flex; gap: 0.5rem; margin-top: 0.5rem; padding-top: 0.75rem; border-top: 1px solid var(--border);">
                <a href="/edit-listing/${item.id}" class="btn btn-secondary" style="flex: 1; padding: 0.4rem; font-size: 0.8rem; border-radius: var(--radius-sm);">Edit</a>
                <button class="btn btn-danger delete-btn" style="flex: 1; padding: 0.4rem; font-size: 0.8rem; border-radius: var(--radius-sm);">Delete</button>
            </div>
            <button class="btn btn-success status-btn" style="width: 100%; margin-top: 0.5rem; padding: 0.4rem; font-size: 0.8rem; border-radius: var(--radius-sm);">
                ${item.is_sold === 1 ? 'Mark as Available' : 'Mark as Sold'}
            </button>
        </div>
    `;
    
    const navigate = () => { window.location.href = `/listings/${item.id}`; };
    card.querySelector('.listing-img-wrapper').addEventListener('click', navigate);
    card.querySelector('.listing-title').addEventListener('click', navigate);
    
    card.querySelector('.delete-btn').addEventListener('click', async () => {
        if (confirm("Are you sure you want to delete this listing?")) {
            await deleteListingItem(item.id);
        }
    });
    
    card.querySelector('.status-btn').addEventListener('click', async () => {
        const nextStatus = item.is_sold === 1 ? 0 : 1;
        await toggleSoldStatus(item.id, nextStatus);
    });
    
    return card;
}

// --- UTILITY FUNCTIONS ---

function showNotification(message, type = 'success') {
    const existing = document.querySelectorAll('.notification-alert');
    existing.forEach(el => el.remove());
    
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} notification-alert`;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 1000;
        box-shadow: var(--shadow-lg);
        width: 90%;
        max-width: 500px;
    `;
    
    notification.innerHTML = `
        <svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            ${type === 'success' 
              ? '<path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>' 
              : '<path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>'}
        </svg>
        <span>${message}</span>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transition = 'opacity 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

function showLoadingState(show) {
    let overlay = document.getElementById('global-loading-overlay');
    if (show) {
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.id = 'global-loading-overlay';
            overlay.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                width: 100vw;
                height: 100vh;
                background-color: rgba(255, 255, 255, 0.7);
                backdrop-filter: blur(4px);
                z-index: 2000;
                display: flex;
                align-items: center;
                justify-content: center;
            `;
            overlay.innerHTML = getSpinnerMarkup("Processing...");
            document.body.appendChild(overlay);
        }
    } else {
        if (overlay) overlay.remove();
    }
}

function formatCurrency(number) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        maximumFractionDigits: 0
    }).format(number);
}

function formatDate(dateString) {
    if (!dateString) return 'Recent';
    try {
        const date = new Date(dateString.replace(' ', 'T') + 'Z');
        return date.toLocaleDateString('en-IN', {
            day: 'numeric',
            month: 'short',
            year: 'numeric'
        });
    } catch (e) {
        return dateString;
    }
}

function getSpinnerMarkup(text = 'Loading...') {
    return `
        <div class="spinner-container">
            <div class="spinner"></div>
            <p class="spinner-text">${text}</p>
        </div>
    `;
}

function getEmptyStateMarkup(title, subtitle, actionUrl, actionText) {
    return `
        <div class="empty-state">
            <svg width="48" height="48" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24" style="margin: 0 auto 1rem auto; display: block;">
                <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 10.5V6a3.75 3.75 0 10-7.5 0v4.5m11.356-1.993l1.263 12c.07.665-.45 1.243-1.119 1.243H4.25a1.125 1.125 0 01-1.12-1.243l1.264-12A1.125 1.125 0 015.513 7.5h12.974c.576 0 1.059.435 1.119 1.007zM8.625 10.5a.375.375 0 11-.75 0 .375.375 0 01.75 0zm7.5 0a.375.375 0 11-.75 0 .375.375 0 01.75 0z"></path>
            </svg>
            <div class="empty-state-title">${title}</div>
            <p class="empty-state-desc">${subtitle}</p>
            <a href="${actionUrl}" class="btn btn-primary">${actionText}</a>
        </div>
    `;
}
