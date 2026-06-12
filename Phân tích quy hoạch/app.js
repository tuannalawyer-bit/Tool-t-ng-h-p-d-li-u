/**
 * Guland Map Overlay Demo
 * Core JS Logic using Leaflet.js
 */

document.addEventListener("DOMContentLoaded", () => {
    // --------------------------------------------------
    // 1. Configuration Data
    // --------------------------------------------------
    const MAP_CONFIG = {
        baseMaps: {
            osm: {
                url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            },
            satellite: {
                url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
            },
            dark: {
                url: 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
            }
        },
        regions: {
            hcm: {
                name: 'TP. Hồ Chí Minh',
                center: [10.7769, 106.7009], // Bến Thành
                zoom: 14,
                overlays: [
                    {
                        id: 'qh_hcm_2030',
                        name: 'Quy hoạch sử dụng đất 2030',
                        url: 'https://l5cfglaebpobj.vcdn.cloud/tp-ho-chi-minh-2030/{z}/{x}/{y}.png',
                        maxZoom: 21
                    },
                    {
                        id: 'qh_hcm_2040',
                        name: 'Quy hoạch chung TP.HCM 2040',
                        url: 'https://s3-han02.fptcloud.com/guland10/ho-chi-minh--40dcqhc60-dttt/{z}/{x}/{y}.png',
                        maxZoom: 21
                    },
                    {
                        id: 'qh_hcm_pkct',
                        name: 'Quy hoạch Phân khu / 1/500',
                        url: 'https://l5cfglaebpobj.vcdn.cloud/tp-ho-chi-minh-pkct/{z}/{x}/{y}.png',
                        maxZoom: 21
                    },
                    {
                        id: 'plot_hcm',
                        name: 'Bản đồ Thửa đất TP.HCM',
                        url: 'https://s3-han02.fptcloud.com/guland6/land/hcm/{z}/{x}/{y}.png',
                        maxZoom: 21
                    }
                ],
                bookmarks: [
                    { name: 'Q.1 Bến Thành', coords: [10.7715, 106.6984], zoom: 16 },
                    { name: 'Thủ Thiêm', coords: [10.7730, 106.7210], zoom: 15 },
                    { name: 'Phú Mỹ Hưng', coords: [10.7289, 106.7192], zoom: 15 },
                    { name: 'KĐT Tây Bắc', coords: [10.9134, 106.5441], zoom: 14 }
                ]
            },
            hn: {
                name: 'Hà Nội',
                center: [21.0285, 105.8542], // Hoàn Kiếm
                zoom: 13,
                overlays: [
                    {
                        id: 'qh_hn_2030',
                        name: 'Quy hoạch sử dụng đất 2030',
                        url: 'https://l5cfglaebpobj.vcdn.cloud/ha-noi-2030-2/{z}/{x}/{y}.png',
                        maxZoom: 21
                    },
                    {
                        id: 'qh_hn_2045',
                        name: 'Quy hoạch chung Thủ đô 2045',
                        url: 'https://s3.hn-1.cloud.cmctelecom.vn/guland6/hn-qhc/{z}/{x}/{y}.png',
                        maxZoom: 21
                    },
                    {
                        id: 'qh_hn_pkct',
                        name: 'Quy hoạch Phân khu / 1/500',
                        url: 'https://l5cfglaebpobj.vcdn.cloud/ha-noi-pkct/{z}/{x}/{y}.png',
                        maxZoom: 21
                    },
                    {
                        id: 'plot_hn',
                        name: 'Bản đồ Thửa đất Hà Nội',
                        url: 'https://s3-han02.fptcloud.com/guland6/land/ha-noi-2/{z}/{x}/{y}.png',
                        maxZoom: 21
                    }
                ],
                bookmarks: [
                    { name: 'Hồ Hoàn Kiếm', coords: [21.0285, 105.8542], zoom: 16 },
                    { name: 'Khu Tây Hồ Tây', coords: [21.0660, 105.8025], zoom: 15 },
                    { name: 'Mỹ Đình', coords: [21.0205, 105.7739], zoom: 15 },
                    { name: 'Gia Lâm Smart', coords: [20.9972, 105.9353], zoom: 15 }
                ]
            }
        }
    };

    // --------------------------------------------------
    // 2. Application State
    // --------------------------------------------------
    let map = null;
    let currentBaseLayer = null;
    let currentOverlayLayer = null;
    let currentRegionKey = 'hcm';
    let currentOpacity = 0.8;

    // DOM Elements
    const regionSelect = document.getElementById('regionSelect');
    const overlaySelect = document.getElementById('overlaySelect');
    const opacityRange = document.getElementById('opacityRange');
    const opacityValLabel = document.getElementById('opacityVal');
    const basemapButtons = document.querySelectorAll('.basemap-btn');
    const quickLinksContainer = document.getElementById('quickLinks');
    const mapLoader = document.getElementById('mapLoader');

    // --------------------------------------------------
    // 3. Core Functions
    // --------------------------------------------------
    
    // Show/Hide loader
    const toggleLoader = (show) => {
        if (show) {
            mapLoader.classList.remove('hidden');
        } else {
            mapLoader.classList.add('hidden');
        }
    };

    // Initialize Leaflet Map
    const initMap = () => {
        toggleLoader(true);
        const currentRegion = MAP_CONFIG.regions[currentRegionKey];
        
        // 1. Create Leaflet instance
        map = L.map('map', {
            center: currentRegion.center,
            zoom: currentRegion.zoom,
            zoomControl: false // Add it customized on bottom-right
        });

        L.control.zoom({
            position: 'bottomright'
        }).addTo(map);

        // 2. Add Base Map (default OSM)
        const osmConf = MAP_CONFIG.baseMaps.osm;
        currentBaseLayer = L.tileLayer(osmConf.url, {
            attribution: osmConf.attribution,
            maxZoom: 20
        }).addTo(map);

        // 3. Setup initial dynamic components
        updateControlsForRegion();
        
        // Trigger initial overlay load
        updateOverlay();

        toggleLoader(false);
    };

    // Populate Select Controls & Bookmarks based on chosen Region
    const updateControlsForRegion = () => {
        const region = MAP_CONFIG.regions[currentRegionKey];
        
        // 1. Clear & Populate Overlays Select
        overlaySelect.innerHTML = '';
        region.overlays.forEach(ov => {
            const opt = document.createElement('option');
            opt.value = ov.id;
            opt.textContent = ov.name;
            overlaySelect.appendChild(opt);
        });

        // 2. Clear & Populate Bookmarks (Quick Links)
        quickLinksContainer.innerHTML = '';
        region.bookmarks.forEach(bm => {
            const badge = document.createElement('button');
            badge.className = 'link-badge';
            badge.innerHTML = `<i class="fa-solid fa-thumbtack"></i> ${bm.name}`;
            badge.addEventListener('click', () => {
                map.flyTo(bm.coords, bm.zoom, {
                    animate: true,
                    duration: 1.5
                });
            });
            quickLinksContainer.appendChild(badge);
        });
    };

    // Switch Base Map Layer
    const switchBaseMap = (basemapKey) => {
        if (currentBaseLayer) {
            map.removeLayer(currentBaseLayer);
        }
        const config = MAP_CONFIG.baseMaps[basemapKey];
        currentBaseLayer = L.tileLayer(config.url, {
            attribution: config.attribution,
            maxZoom: 20
        }).addTo(map);
        // Bring overlay back to front
        if (currentOverlayLayer) {
            currentOverlayLayer.bringToFront();
        }
    };

    // Switch/Load Overlay Layer
    const updateOverlay = () => {
        toggleLoader(true);
        
        // Remove old overlay if any
        if (currentOverlayLayer) {
            map.removeLayer(currentOverlayLayer);
        }

        const region = MAP_CONFIG.regions[currentRegionKey];
        const overlayId = overlaySelect.value;
        const overlayConf = region.overlays.find(ov => ov.id === overlayId);

        if (overlayConf) {
            currentOverlayLayer = L.tileLayer(overlayConf.url, {
                maxZoom: overlayConf.maxZoom,
                tms: false,
                opacity: currentOpacity,
                attribution: 'Quy hoạch &copy; Guland.vn'
            });

            // Track tile loading finish to hide loader
            let loadTimer;
            currentOverlayLayer.on('loading', () => {
                // If takes too long, show spinner
                loadTimer = setTimeout(() => toggleLoader(true), 200);
            });
            currentOverlayLayer.on('load', () => {
                clearTimeout(loadTimer);
                toggleLoader(false);
            });
            currentOverlayLayer.on('tileerror', () => {
                clearTimeout(loadTimer);
                toggleLoader(false);
            });

            currentOverlayLayer.addTo(map);
            currentOverlayLayer.bringToFront();
        } else {
            toggleLoader(false);
        }
    };

    // --------------------------------------------------
    // 4. Event Listeners
    // --------------------------------------------------

    // Region Selection Changed
    regionSelect.addEventListener('change', (e) => {
        currentRegionKey = e.target.value;
        const regionConf = MAP_CONFIG.regions[currentRegionKey];
        
        // Jump map to new region center
        map.flyTo(regionConf.center, regionConf.zoom, {
            animate: true,
            duration: 1.5
        });
        
        // Re-populate overlays dropdown and bookmarks
        updateControlsForRegion();
        
        // Load the default overlay for this region
        updateOverlay();
    });

    // Overlay Selection Changed
    overlaySelect.addEventListener('change', () => {
        updateOverlay();
    });

    // Opacity Slider Changed
    opacityRange.addEventListener('input', (e) => {
        const val = e.target.value;
        currentOpacity = val / 100;
        opacityValLabel.textContent = `${val}%`;
        
        if (currentOverlayLayer) {
            currentOverlayLayer.setOpacity(currentOpacity);
        }
    });

    // Basemap Buttons Interactivity
    basemapButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            // Toggle UI classes
            basemapButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // Switch
            const key = btn.dataset.basemap;
            switchBaseMap(key);
        });
    });

    // --------------------------------------------------
    // 5. Initialization Run
    // --------------------------------------------------
    initMap();
});
