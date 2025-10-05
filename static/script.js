/* DOM Elements -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- */
const themeIcon = document.getElementById("theme-icon");
const temperatureCelsius = document.getElementById("temperatureCelsius");
const temperatureFahrenheit = document.getElementById("temperatureFahrenheit");
const windSpeed = document.getElementById("windSpeed");
const humidity = document.getElementById("humidity");
const rainfall = document.getElementById("rainfall");
const atmosphericPressure = document.getElementById("atmosphericPressure");
const riskScore = document.getElementById("riskScore");

/* Theme Toggle -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- */
const toggleTheme = () => {
    document.body.classList.toggle('light-mode');

    if (document.body.classList.contains("light-mode")) {
        themeIcon.classList.replace("fa-sun", "fa-moon");
    } else {
        themeIcon.classList.replace("fa-moon", "fa-sun");
    }
}

/* map -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- */
let map = L.map('map').setView([53.3489, -6.2430], 10);

L.tileLayer('https://api.maptiler.com/maps/streets-v2/{z}/{x}/{y}.png?key=qp7uy5rCF4Ij9uDMupR6', {
    attribution: '<a href="https://www.maptiler.com/copyright/" target="_blank">&copy; MapTiler</a> <a href="https://www.openstreetmap.org/copyright" target="_blank">&copy; OpenStreetMap contributors</a>',
}).addTo(map);

let marker = L.marker([53.3489, -6.2430]).addTo(map);

/* Map interactions -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- */
map.on('click', function(e) {
    const lat = e.latlng.lat;
    const lng = e.latlng.lng;
    marker.setLatLng([lat, lng]);
    // REMOVED: updateEverything(); 
});

function handleSearchEnter(event) {
    if (event.key === 'Enter') {
        event.preventDefault();
        searchLocation();
    }
}

function searchLocation() {
    const location = document.getElementById('location-search').value.trim();
    if (!location) return;

    fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(location)}`)
        .then(response => response.json())
        .then(data => {
            if (data && data.length > 0) {
                const result = data[0];
                const lat = parseFloat(result.lat);
                const lon = parseFloat(result.lon);
                map.setView([lat, lon], 13);
                marker.setLatLng([lat, lon]);
                // REMOVED: updateEverything(); 
            } else {
                alert('Location not found. Please try a different search term.');
            }
        })
        .catch(error => {
            console.error('Error searching location:', error);
            alert('Error searching for location. Please try again.');
        });
}

/* Sidebar scroll indicator -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- */
function initialiseScrollIndicator() {
    const sidebar = document.querySelector('.sidebar');
    const indicator = document.createElement('div');
    indicator.className = 'scroll-indicator';
    sidebar.appendChild(indicator);

    sidebar.addEventListener('scroll', function() {
        if (this.scrollTop > 10) {
            this.classList.add('scrolled');
        } else {
            this.classList.remove('scrolled');
        }
    });
}

/* Main scroll indicator -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- */
function initialiseMainScrollIndicator() {
    const dataPanel = document.querySelector('.data-panel');
    const indicator = document.createElement('div');
    indicator.className = 'scroll-indicator';
    dataPanel.appendChild(indicator);

    dataPanel.addEventListener('scroll', function() {
        if (this.scrollTop > 10) {
            this.classList.add('scrolled');
        } else {
            this.classList.remove('scrolled');
        }
    });
}


/* Date/time -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- */
function initialiseDateTime() {
    const now = new Date();
    const currentDate = now.toISOString().split('T')[0];
    const currentTime = now.toTimeString().slice(0, 5);
    
    document.getElementById('eventDate').value = currentDate;
    document.getElementById('appt').value = currentTime;
    
    updateDateTimeDisplay();
}

function updateDateTimeDisplay() {
    const dateInput = document.getElementById('eventDate');
    const timeInput = document.getElementById('appt');
    const dateDisplay = document.getElementById('date-display');
    const timeDisplay = document.getElementById('time-display');
    
    if (dateInput.value) {
        const date = new Date(dateInput.value);
        const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
        dateDisplay.textContent = date.toLocaleDateString('en-US', options);
    } else {
        dateDisplay.textContent = 'Day, Date';
    }
    
    if (timeInput.value) {
        const time = new Date('1970-01-01T' + timeInput.value);
        const timeOptions = { hour: 'numeric', minute: '2-digit', hour12: false };
        timeDisplay.textContent = time.toLocaleTimeString('en-US', timeOptions).replace(' ', '');
    } else {
        timeDisplay.textContent = 'XX:XX';
    }
}

function updateEverything() {
    const date = document.getElementById('eventDate').value;
    const time = document.getElementById('appt').value;
    
    if (!date || !time) {
        alert('Please select both date and time.');
        return;
    }

    updateDateTimeDisplay();

    const markerLatLng = marker.getLatLng();
    const lat = markerLatLng.lat;
    const lng = markerLatLng.lng;

    Promise.race([
        fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&zoom=18&addressdetails=1`),
        fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&addressdetails=1`)
    ])
    .then(response => response.json())
    .then(data => {
        console.log('Reverse geocoding data:', data);
        
        let locationName = getBestLocationName(data, lat, lng);
        updateDisplayWithLocation(locationName);
        getResponse(lat, lng);
    })
    .catch(error => {
        console.error('Error getting location name:', error);
        updateDisplayWithLocation(`Lat: ${lat.toFixed(4)}, Lng: ${lng.toFixed(4)}`);
        getResponse(lat, lng);
    });
}

function getBestLocationName(data, lat, lng) {
    if (!data) return `Lat: ${lat.toFixed(4)}, Lng: ${lng.toFixed(4)}`;
    
    if (data.name && data.name !== data.display_name?.split(',')[0]) {
        return data.name;
    }
    
    if (data.display_name) {
        const parts = data.display_name.split(',');
        if (data.category === 'tourism' || data.type === 'attraction' || parts.length <= 3) {
            return parts.slice(0, 2).join(', ').trim();
        }
        return parts[0].trim();
    }
    
    if (data.address) {
        return data.address.venue || 
               data.address.attraction ||
               data.address.tourism ||
               data.address.building ||
               `Lat: ${lat.toFixed(4)}, Lng: ${lng.toFixed(4)}`;
    }
    
    return `Lat: ${lat.toFixed(4)}, Lng: ${lng.toFixed(4)}`;
}

function updateDisplayWithLocation(locationName) {
    const dateDisplay = document.getElementById('date-display').textContent;
    const timeDisplay = document.getElementById('time-display').textContent;
    document.getElementById('location-display').innerHTML = 
        `${locationName}ㅤ//ㅤ<span id="date-display">${dateDisplay}</span>ㅤ//ㅤ<span id="time-display">${timeDisplay}</span>`;
}

/* Clouds -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- */
function createClouds() {
    const container = document.querySelector('.clouds');
    const maxWidth = window.innerWidth;

    for (let i = 0; i < 25; i++) {
        const cloud = document.createElement('div');
        cloud.classList.add('cloud');

        const width = Math.floor(Math.random() * (maxWidth / 3));
        const height = Math.floor(width / 2);
        cloud.style.width = `${width}px`;
        cloud.style.height = `${height}px`;

        const top = Math.floor(Math.random() * 80) + 10;
        cloud.style.top = `${top}%`;

        const left = Math.floor(Math.random() * 100);
        cloud.style.left = `-${left}%`;

        const duration = Math.floor(Math.random() * 20) + 20;
        const delay = Math.floor(Math.random() * -20);
        cloud.style.animation = `float ${duration}s infinite linear`;
        cloud.style.animationDelay = `${delay}s`;

        container.appendChild(cloud);
    }
}

/* Initialisation -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- */
document.addEventListener('DOMContentLoaded', function() {
    initialiseScrollIndicator();
    initialiseDateTime();
    createClouds();
    
    // REMOVED: updateEverything(); 
    // Data is now only updated when the "Go" button calls updateEverything()
});

/* Notes -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- */
function getResponse(lat, lng) { /* Placeholder function */ }