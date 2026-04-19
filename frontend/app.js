document.getElementById('travel-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // UI states
    const btnText = document.querySelector('.btn-text');
    const loader = document.getElementById('btn-loader');
    const resultSection = document.getElementById('result-section');
    const errorSection = document.getElementById('error-message');
    const errorText = document.getElementById('error-text');
    
    // Reset previous states
    resultSection.classList.add('hidden');
    errorSection.classList.add('hidden');
    btnText.classList.add('hidden');
    loader.classList.remove('hidden');
    
    // Gather form data
    const formData = {
        origin: document.getElementById('origin').value,
        destination: document.getElementById('destination').value,
        departure_date: document.getElementById('departure_date').value,
        return_date: document.getElementById('return_date').value,
        style: document.getElementById('style').value
    };

    try {
        const response = await fetch('/api/plan', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });
        
        if (!response.ok) {
            throw new Error(`API request failed with status: ${response.status}`);
        }
        
        const resData = await response.json();
        if (!resData.success || !resData.data) {
            throw new Error(resData.message || "Invalid response format from server.");
        }
        const planData = resData.data;

        // Render Trip Summary
        document.getElementById('summary-text').textContent = planData.trip_summary;

        // Render Logistics - Weather
        const weather = planData.logistics?.weather_info || {};
        document.getElementById('weather-text').textContent = weather.condition || 'N/A';
        document.getElementById('temp-text').textContent = `Temperature: ${weather.temp_range || 'N/A'}`;
        document.getElementById('clothing-text').textContent = weather.clothing_advice || '';

        // Render Logistics - Transport
        const transportList = document.getElementById('transport-list');
        transportList.innerHTML = '';
        const transportTips = planData.logistics?.transport_tips || [];
        transportTips.forEach(tip => {
            const li = document.createElement('li');
            li.innerHTML = `<strong>${tip.tip_title}:</strong> ${tip.tip_content}`;
            transportList.appendChild(li);
        });
        
        // Render Array of Objects (Itinerary with nested locations)
        const itineraryList = document.getElementById('itinerary-list');
        itineraryList.innerHTML = ''; 
        
        (planData.itinerary || []).forEach(day => {
            const daySection = document.createElement('div');
            daySection.className = 'day-section';
            
            const dayHeader = document.createElement('div');
            dayHeader.className = 'day-header';
            dayHeader.innerHTML = `<h3>Day ${day.day} - ${day.daily_theme}</h3>`;
            daySection.appendChild(dayHeader);

            const grid = document.createElement('div');
            grid.className = 'itinerary-grid';

            (day.locations || []).forEach(loc => {
                const card = document.createElement('div');
                card.className = 'itinerary-card glass-card';
                
                const photoTips = loc.photography_tips;
                let photoTipsHTML = '';
                if (photoTips) {
                    photoTipsHTML = `
                        <div class="photography-tips">
                            <h4>📸 Photography Tips</h4>
                            <p><strong>Best Angle:</strong> ${photoTips.best_angle || 'N/A'}</p>
                            <p><strong>Camera:</strong> ${photoTips.camera_settings || 'N/A'}</p>
                            <p><strong>Mobile:</strong> ${photoTips.mobile_tip || 'N/A'}</p>
                        </div>
                    `;
                }

                card.innerHTML = `
                    <div class="card-img-wrapper">
                        <img src="${loc.image_url}" alt="${loc.place_name}" loading="lazy">
                    </div>
                    <div class="card-content">
                        <h3>${loc.place_name}</h3>
                        <p class="loc-desc">${loc.description}</p>
                        ${photoTipsHTML}
                        <button type="button" class="map-toggle-btn" onclick="window.toggleMap(this, '${loc.place_name}')">🗺️ View on Map</button>
                    </div>
                `;
                grid.appendChild(card);
            });

            daySection.appendChild(grid);
            itineraryList.appendChild(daySection);
        });

        // Toggle visibility and slide down seamlessly
        resultSection.classList.remove('hidden');
        
        // Smooth scroll over to view results organically
        setTimeout(() => {
            resultSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 100);

    } catch (error) {
        console.error("Error fetching plan:", error);
        errorText.textContent = error.message || 'An error occurred while planning your trip. Please try again.';
        errorSection.classList.remove('hidden');
        resultSection.classList.add('hidden');
    } finally {
        // Revert button interaction state
        btnText.classList.remove('hidden');
        loader.classList.add('hidden');
    }
});

// Map Toggle Function
window.toggleMap = function(btn, placeName) {
    const cardContent = btn.closest('.card-content');
    let mapContainer = cardContent.querySelector('.map-container');
    
    if (!mapContainer) {
        // Create it on first click
        mapContainer = document.createElement('div');
        mapContainer.className = 'map-container';
        mapContainer.innerHTML = `<iframe src="https://maps.google.com/maps?q=${encodeURIComponent(placeName)}&t=&z=13&ie=UTF8&iwloc=&output=embed" loading="lazy"></iframe>`;
        btn.insertAdjacentElement('afterend', mapContainer);
        btn.innerHTML = '🗺️ Hide Map';
    } else {
        // Toggle visibility
        if (mapContainer.classList.contains('hidden')) {
            mapContainer.classList.remove('hidden');
            btn.innerHTML = '🗺️ Hide Map';
        } else {
            mapContainer.classList.add('hidden');
            btn.innerHTML = '🗺️ View on Map';
        }
    }
};
