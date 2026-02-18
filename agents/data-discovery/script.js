const runBtn = document.getElementById('runBtn');
const input = document.getElementById('commandInput');
const revenueVal = document.getElementById('revenueVal');
const bestSellerVal = document.getElementById('bestSellerVal');
const heading = document.getElementById('discoveryHeading');
const labelLeft = document.getElementById('labelLeft');
const labelRight = document.getElementById('labelRight');

async function triggerDiscovery() {
    const query = input.value.trim().toLowerCase();
    if (!query) return;

    try {
        let data;
        if (query.includes('for')) {
            const product = query.split('for')[1].trim();
            const response = await fetch(`http://127.0.0.1:8001/product/${product}`);
            data = await response.json();
            
            if (data.error) {
                alert(data.error);
                return;
            }

            // Update UI for specific product
            heading.innerText = `Product: ${data.product}`;
            labelLeft.innerText = "Product Revenue";
            labelRight.innerText = "Units Sold";
            revenueVal.innerText = `$${data.revenue.toLocaleString()}`;
            bestSellerVal.innerText = `${data.units} Units`;
        } 
        else {
            const response = await fetch('http://127.0.0.1:8001/stats');
            data = await response.json();
            
            // Update UI for Global Stats
            heading.innerText = "Global Statistics";
            labelLeft.innerText = "Total Revenue";
            labelRight.innerText = "Top Product";
            revenueVal.innerText = `$${data.total_revenue.toLocaleString()}`;
            bestSellerVal.innerText = data.best_seller;
        }

        // Show results, hide instructions
        document.getElementById('instructions').classList.add('hidden');
        document.getElementById('resultsGrid').classList.remove('hidden');
        input.value = '';
    } catch (err) {
        alert('Server connection failed. Check Port 8001.');
    }
}

runBtn.addEventListener('click', triggerDiscovery);
input.addEventListener('keypress', (e) => { if (e.key === 'Enter') triggerDiscovery(); });
