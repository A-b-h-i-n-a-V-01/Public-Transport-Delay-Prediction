document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const form = document.getElementById('prediction-form');
    const originSelect = document.getElementById('origin');
    const destSelect = document.getElementById('destination');
    const transportSelect = document.getElementById('transport_type');
    const btnPredict = document.getElementById('btn-predict');
    const spinner = btnPredict.querySelector('.spinner');
    
    // Accordion Elements
    const accordionToggle = document.getElementById('toggle-sim-params');
    const accordionContent = document.getElementById('sim-params-content');
    
    // Result State Elements
    const resultsWelcome = document.getElementById('results-welcome');
    const resultsActive = document.getElementById('results-active');
    
    const outcomeGauge = document.getElementById('outcome-gauge');
    const probabilityValue = document.getElementById('probability-value');
    const outcomeStatus = document.getElementById('outcome-status');
    const outcomeDesc = document.getElementById('outcome-desc');
    
    const resRoute = document.getElementById('res-route');
    const resDuration = document.getElementById('res-duration');
    const resTraffic = document.getElementById('res-traffic');
    const resWeather = document.getElementById('res-weather');

    // Toggle simulated parameters accordion
    accordionToggle.addEventListener('click', () => {
        accordionToggle.classList.toggle('active');
        accordionContent.classList.toggle('open');
    });

    // Fetch Metadata (Stations, Transport Types) to populate dropdowns
    async function loadMetadata() {
        try {
            const response = await fetch('/api/metadata');
            const data = await response.json();
            
            if (data.stations) {
                originSelect.innerHTML = '';
                destSelect.innerHTML = '';
                
                data.stations.forEach(station => {
                    const opt1 = document.createElement('option');
                    opt1.value = station.id;
                    opt1.textContent = station.name;
                    
                    const opt2 = document.createElement('option');
                    opt2.value = station.id;
                    opt2.textContent = station.name;
                    
                    originSelect.appendChild(opt1);
                    destSelect.appendChild(opt2);
                });
                
                // Set default selections
                const hasStation = (id) => data.stations.some(s => s.id === id);
                if (hasStation('Station_31')) {
                    originSelect.value = 'Station_31';
                }
                if (hasStation('Station_6')) {
                    destSelect.value = 'Station_6';
                }
            }
            
            if (data.transport_types) {
                transportSelect.innerHTML = '';
                data.transport_types.forEach(type => {
                    const opt = document.createElement('option');
                    opt.value = type;
                    opt.textContent = type;
                    transportSelect.appendChild(opt);
                });
                // Default to Tram
                if (data.transport_types.includes('Tram')) {
                    transportSelect.value = 'Tram';
                }
            }
        } catch (error) {
            console.error('Failed to load metadata:', error);
        }
    }

    // Submit Prediction
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Show loading state
        btnPredict.disabled = true;
        spinner.classList.remove('hidden');
        
        // Build payload
        const payload = {
            origin: originSelect.value,
            destination: destSelect.value,
            transport_type: transportSelect.value,
            departure_time: document.getElementById('departure_time').value,
            
            // Contextual (simulated)
            temperature_C: parseFloat(document.getElementById('temperature_C').value),
            humidity_percent: parseFloat(document.getElementById('humidity_percent').value),
            wind_speed_kmh: parseFloat(document.getElementById('wind_speed_kmh').value),
            precipitation_mm: parseFloat(document.getElementById('precipitation_mm').value),
            traffic_congestion_index: parseFloat(document.getElementById('traffic_congestion_index').value),
            weather_condition: document.getElementById('weather_condition').value
        };

        try {
            const response = await fetch('/api/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            
            const result = await response.json();
            
            if (result.success) {
                displayResult(result);
            } else {
                alert('Prediction failed: ' + result.error);
            }
        } catch (error) {
            console.error('Prediction request error:', error);
            alert('Error connecting to the backend server.');
        } finally {
            // Hide loading state
            btnPredict.disabled = false;
            spinner.classList.add('hidden');
        }
    });

    // Render results on UI
    function displayResult(res) {
        // Swap cards
        resultsWelcome.classList.add('hidden');
        resultsActive.classList.remove('hidden');
        
        const isDelayed = res.prediction === 1;
        const probDelayed = res.probability_delayed;
        const probOnTime = res.probability_ontime;
        
        const color = isDelayed ? 'var(--danger-color)' : 'var(--success-color)';
        const displayPercentage = isDelayed ? Math.round(probDelayed * 100) : Math.round(probOnTime * 100);
        
        // Update Status Badge
        outcomeStatus.textContent = isDelayed ? 'DELAYED' : 'ON-TIME';
        outcomeStatus.className = 'outcome-badge ' + (isDelayed ? 'delayed' : 'on-time');
        
        // Update explanation
        if (isDelayed) {
            outcomeDesc.textContent = `TransitDelay AI estimates a high probability of delay for this trip. The transit is forecasted to be delayed.`;
        } else {
            outcomeDesc.textContent = `TransitDelay AI estimates a high probability of on-time arrival. The transit is forecasted to run on schedule.`;
        }
        
        // Detail items
        resRoute.textContent = res.context.route_id.replace('_', ' ');
        resDuration.textContent = `${res.context.estimated_duration_min} min`;
        resTraffic.textContent = `${res.context.traffic_congestion_index}/100`;
        resWeather.textContent = `${res.context.weather_condition}, ${res.context.temperature_C}°C`;

        // Animate the gauge and percentage number count up
        const duration = 1000; // 1 second
        const startTime = performance.now();
        
        probabilityValue.style.color = color;

        function updateGauge(currentTime) {
            const elapsedTime = currentTime - startTime;
            const progress = Math.min(elapsedTime / duration, 1);
            
            // Ease out quad for smooth deceleration
            const easedProgress = progress * (2 - progress);
            const currentPercent = Math.round(easedProgress * displayPercentage);
            
            probabilityValue.textContent = `${currentPercent}%`;
            outcomeGauge.style.background = `radial-gradient(closest-side, var(--bg-dark) 80%, transparent 80% 100%),
                                             conic-gradient(${color} ${currentPercent}%, rgba(255, 255, 255, 0.05) ${currentPercent}%)`;
            
            if (progress < 1) {
                requestAnimationFrame(updateGauge);
            }
        }
        
        requestAnimationFrame(updateGauge);
    }

    // Initial Load
    loadMetadata();
});
