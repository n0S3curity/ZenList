        document.addEventListener('DOMContentLoaded', () => {
            const productsContainer = document.getElementById('productsContainer');
            const searchInput = document.getElementById('searchInput');
            const loadingSpinner = document.getElementById('loadingSpinner');
            const emptyListMessage = document.getElementById('emptyListMessage');
            const sidebar = document.getElementById('sidebar');
            const hamburgerIcon = document.getElementById('hamburgerIcon');
            const barcodeScannerBtn = document.getElementById('barcodeScannerBtn');
            const barcodeScannerModal = document.getElementById('barcodeScannerModal');
            const closeScannerModalBtn = document.getElementById('closeScannerModalBtn');
            const simulatedBarcodeInput = document.getElementById('simulatedBarcodeInput');
            const scanButton = document.getElementById('scanButton');

            // --- Mock Data ---
            const mockProductsData = [
                { name: "חלב 3%", barcode: "7290002872323", averagePrice: 6.85 },
                { name: "לחם אחיד", barcode: "7290000000010", averagePrice: 12.50 },
                { name: "עגבניה", barcode: "9876543210123", averagePrice: 9.10 },
                { name: "גבינה צהובה", barcode: "1234567890123", averagePrice: 26.20 },
                { name: "ביצים L", barcode: "7290000000027", averagePrice: 15.75 },
                { name: "מים מינרליים", barcode: "7290000000034", averagePrice: 4.50 },
                { name: "שוקולד השחר", barcode: "7290010042459", averagePrice: 10.10 },
                { name: "שמן זית כתית", barcode: "7290000000041", averagePrice: 23.50 },
            ];

            // --- Utility Functions ---

            function showLoading() {
                loadingSpinner.style.display = 'block';
                productsContainer.innerHTML = '';
                emptyListMessage.classList.add('hidden');
            }

            function hideLoading() {
                loadingSpinner.style.display = 'none';
            }

            function showEmptyMessage() {
                emptyListMessage.classList.remove('hidden');
            }

            // Function to render the product list
            function renderProducts(products) {
                productsContainer.innerHTML = ''; // Clear existing content
                if (products.length === 0) {
                    showEmptyMessage();
                    return;
                }
                emptyListMessage.classList.add('hidden');

                products.forEach(product => {
                    const productCard = document.createElement('div');
                    productCard.className = 'product-card bg-white p-4 rounded-lg shadow-sm border border-gray-200';
                    productCard.innerHTML = `
                        <div class="product-details flex-grow">
                            <!-- Product Icon (inline SVG) -->
                            <svg class="w-6 h-6 text-gray-500 ml-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4"></path>
                            </svg>
                            <div>
                                <p class="text-xl font-bold text-gray-800">${product.name}</p>
                                <p class="text-sm text-gray-500 mt-1">ברקוד: ${product.barcode}</p>
                                <p class="text-lg font-bold text-indigo-500 mt-2">מחיר ממוצע: ₪${product.averagePrice.toFixed(2)}</p>
                            </div>
                        </div>
                        <div class="product-actions flex space-x-2 rtl:space-x-reverse flex-shrink-0">
                            <a href="/stats/${product.barcode}" class="p-2 rounded-full text-indigo-600 hover:bg-indigo-100 transition-colors duration-200" title="סטטיסטיקות">
                                <!-- Stats Icon (inline SVG) -->
                                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z"></path>
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.488 9H15V3.512A9.025 9.025 0 0120.488 9z"></path>
                                </svg>
                            </a>
                            <a href="/product/${product.barcode}/settings" class="p-2 rounded-full text-gray-600 hover:bg-gray-200 transition-colors duration-200" title="הגדרות">
                                <!-- Settings Icon (inline SVG) -->
                                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37h.001a1.724 1.724 0 002.572-1.065z"></path>
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                                </svg>
                            </a>
                        </div>
                    `;
                    productsContainer.appendChild(productCard);
                });
            }

            // Function to filter the products based on search input
            function filterProducts(query) {
                const normalizedQuery = query.trim().toLowerCase();
                if (!normalizedQuery) {
                    renderProducts(mockProductsData);
                    return;
                }

                const filteredProducts = mockProductsData.filter(product => {
                    const nameMatch = product.name.toLowerCase().includes(normalizedQuery);
                    const barcodeMatch = product.barcode.includes(normalizedQuery);
                    return nameMatch || barcodeMatch;
                });
                renderProducts(filteredProducts);
            }

            // --- Event Listeners ---

            hamburgerIcon.addEventListener('click', () => {
                sidebar.classList.toggle('open');
            });

            // Filter products on search input change
            searchInput.addEventListener('input', (event) => {
                filterProducts(event.target.value);
            });

            // Show barcode scanner modal
            barcodeScannerBtn.addEventListener('click', () => {
                barcodeScannerModal.classList.remove('hidden');
            });

            // Close modal
            closeScannerModalBtn.addEventListener('click', () => {
                barcodeScannerModal.classList.add('hidden');
            });

            // Close modal if user clicks outside of it
            window.addEventListener('click', (event) => {
                if (event.target === barcodeScannerModal) {
                    barcodeScannerModal.classList.add('hidden');
                }
            });

            // Handle barcode scan simulation
            scanButton.addEventListener('click', () => {
                const barcode = simulatedBarcodeInput.value;
                if (barcode) {
                    // Update search input and trigger filter
                    searchInput.value = barcode;
                    filterProducts(barcode);
                    barcodeScannerModal.classList.add('hidden');
                }
            });

            // Initial render of all products
            renderProducts(mockProductsData);
        });
