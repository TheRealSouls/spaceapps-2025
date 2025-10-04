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