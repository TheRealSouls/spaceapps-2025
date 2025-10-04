/* Light/dark mode */

const themeIcon = document.getElementById("theme-icon");

const toggleTheme = () => {
    document.body.classList.toggle('light-mode');

    if (document.body.classList.contains("light-mode")) {
        themeIcon.classList.replace("fa-sun", "fa-moon");
    } else {
        themeIcon.classList.replace("fa-moon", "fa-sun");
    }
}

/* Map */
let map = L.map('map').setView([53.3498, 6.2603], 10)

L.tileLayer('https://api.maptiler.com/maps/streets-v2/{z}/{x}/{y}.png?key=qp7uy5rCF4Ij9uDMupR6', {
    attribution: '<a href="https://www.maptiler.com/copyright/" target="_blank">&copy; MapTiler</a> <a href="https://www.openstreetmap.org/copyright" target="_blank">&copy; OpenStreetMap contributors</a>',
}).addTo(map);

let marker = L.marker([53.3498, 6.2603]).addTo(map);

map.on('click', function(e) {
    lat = e.latlng.lat;
    lng = e.latlng.lng;

    marker.setLatLng([lat, lng]);
    getResponse(lat, lng);
});

// Search functionality
const searchInput = document.getElementById('location-search');
const searchBtn = document.getElementById('search-btn');

function searchLocation() {
  const location = searchInput.value.trim();
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
        getResponse(lat, lon);
      }
    })
    .catch(error => console.error('Error searching location:', error));
}

searchBtn.addEventListener('click', searchLocation);
searchInput.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') searchLocation();
});

/* Sidebar scroll indicator */
document.addEventListener('DOMContentLoaded', function(){
    const sidebar = document.querySelector('.sidebar');
    const indicator = document.createElement('div');
    indicator.className = 'scroll-indicator';
    sidebar.appendChild(indicator);

    sidebar.addEventListener('scroll', function() {
        if(this.scrollTop > 10){
            this.classList.add('scrolled');
        } else {
            this.classList.remove('scrolled');
        }
    });
});