    document.addEventListener('DOMContentLoaded', () => {
        const shoppingListContainer = document.getElementById('shoppingListContainer');
        const emptyListMessage = document.getElementById('emptyListMessage');
        const loadingSpinner = document.getElementById('loadingSpinner');
        const addFloatingButton = document.getElementById('addFloatingButton');
        const addProductModal = document.getElementById('addProductModal');
        const closeModalButton = document.getElementById('closeModalButton');
        const newProductNameInput = document.getElementById('newProductName');
        const newProductQuantityInput = document.getElementById('newProductQuantity');
        const newProductCategorySelect = document.getElementById('newProductCategory');
        const saveNewProductButton = document.getElementById('saveNewProductButton');
        const totalItemsDisplay = document.getElementById('totalItemsDisplay');
        const sidebar = document.getElementById('sidebar');
        const hamburgerIcon = document.getElementById('hamburgerIcon');

        // Mock data - In a real app, these would come from your Flask backend API
        let mockShoppingList = []; // This will be populated on fetch
        const mockProducts = [
            { name: "חלב", barcode: "12345", category: "מוצרי חלב" },
            { name: "לחם", barcode: "67890", category: "מאפים" },
            { name: "תפוחים", barcode: "11223", category: "פירות" },
            { name: "ביצים", barcode: "98765", category: "מוצרי חלב" },
            { name: "חזה עוף", barcode: "54321", category: "בשר" },
            { name: "גבינה צהובה", barcode: "22334", category: "מוצרי חלב" },
            { name: "עגבניות", barcode: "33445", category: "ירקות" },
            { name: "תפוחי אדמה", barcode: "44556", category: "ירקות" },
            { name: "קפה", barcode: "55667", category: "משקאות" },
            { name: "סבון", barcode: "66778", category: "ניקיון" }
        ];

        // Store collapsed categories state
        const collapsedCategories = new Set();

        // --- Utility Functions ---

        function showLoading() {
            loadingSpinner.style.display = 'block';
            shoppingListContainer.innerHTML = ''; // Clear list while loading
            emptyListMessage.classList.add('hidden');
            totalItemsDisplay.classList.add('hidden');
        }

        function hideLoading() {
            loadingSpinner.style.display = 'none';
        }

        function showEmptyMessage() {
            emptyListMessage.classList.remove('hidden');
            totalItemsDisplay.classList.add('hidden');
        }

        function hideEmptyMessage() {
            emptyListMessage.classList.add('hidden');
            totalItemsDisplay.classList.remove('hidden');
        }

        // Function to populate the category dropdown
        function populateCategoryDropdown() {
            // Get unique categories from mockProducts, excluding empty ones
            const categories = [...new Set(mockProducts.map(p => p.category))].filter(c => c && c !== 'ללא קטגוריה');
            categories.sort(); // Sort alphabetically

            // Clear existing options and add default "ללא קטגוריה"
            newProductCategorySelect.innerHTML = '<option value="">ללא קטגוריה</option>';

            categories.forEach(category => {
                const option = document.createElement('option');
                option.value = category;
                option.textContent = category;
                newProductCategorySelect.appendChild(option);
            });
        }

        // Function to render the content of a specific category
        function renderCategoryContent(category) {
            const categoryContentDiv = document.querySelector(`.category-content[data-category-name="${category}"]`);
            if (!categoryContentDiv) return; // Should not happen if category exists

            categoryContentDiv.innerHTML = ''; // Clear existing content

            const categoryItems = mockShoppingList.filter(item => {
                const productInfo = mockProducts.find(p => p.name === item.productName);
                return (productInfo ? productInfo.category : 'ללא קטגוריה') === category;
            });

            const toDoItems = categoryItems.filter(item => !item.done);
            const doneItems = categoryItems.filter(item => item.done);

            // Update category header count
            const categoryHeaderSpan = document.querySelector(`.category-header[data-category-name="${category}"] .category-title-wrapper span`);
            if (categoryHeaderSpan) {
                categoryHeaderSpan.textContent = `${category} (${toDoItems.length})`;
            }

            // Render "To Do" items
            if (toDoItems.length > 0) {
                toDoItems.sort((a, b) => a.productName.localeCompare(b.productName)).forEach(item => {
                    categoryContentDiv.appendChild(createListItem(item));
                });
            }

            // Add separator and "Done Items" section if there are done items
            if (doneItems.length > 0) {
                if (toDoItems.length > 0) { // Only add separator if there are also "to do" items
                    const separator = document.createElement('div');
                    separator.className = 'done-items-separator';
                    separator.textContent = '--- פריטים שבוצעו ---';
                    categoryContentDiv.appendChild(separator);
                }
                doneItems.sort((a, b) => a.productName.localeCompare(b.productName)).forEach(item => {
                    categoryContentDiv.appendChild(createListItem(item));
                });
            }
        }


        // Function to render the shopping list, now grouped by category
        function renderShoppingList() {
            // Save current collapsed state before re-rendering
            // This part was modified to *always* collapse on initial load
            // but preserve state on subsequent re-renders within the same session.
            const currentCollapsedState = new Set();
            document.querySelectorAll('.category-header.collapsed').forEach(header => {
                currentCollapsedState.add(header.dataset.categoryName);
            });


            shoppingListContainer.innerHTML = ''; // Clear existing list
            if (mockShoppingList.length === 0) {
                showEmptyMessage();
                return;
            }
            hideEmptyMessage();

            // Group items by category
            const categorizedItems = mockShoppingList.reduce((acc, item) => {
                // Find the category for the current item
                const productInfo = mockProducts.find(p => p.name === item.productName);
                const category = productInfo ? productInfo.category : 'ללא קטגוריה'; // Default if no category found

                if (!acc[category]) {
                    acc[category] = [];
                }
                acc[category].push(item);
                return acc;
            }, {});

            // Sort categories alphabetically, put 'ללא קטגוריה' last
            const sortedCategories = Object.keys(categorizedItems).sort((a, b) => {
                if (a === 'ללא קטגוריה') return 1;
                if (b === 'ללא קטגוריה') return -1;
                return a.localeCompare(b);
            });

            let totalItemsCount = 0;

            sortedCategories.forEach(category => {
                const toDoItems = categorizedItems[category].filter(item => !item.done);
                totalItemsCount += categorizedItems[category].length;

                // Create category header
                const categoryHeaderDiv = document.createElement('div');
                categoryHeaderDiv.className = 'category-header text-xl font-semibold text-gray-700 mt-6 mb-3 border-b pb-2 border-gray-300';
                categoryHeaderDiv.dataset.categoryName = category; // Add data attribute for category name
                categoryHeaderDiv.innerHTML = `
                    <div class="category-title-wrapper">
                        <span>${category} (${toDoItems.length})</span>
                    </div>
                    <div class="category-actions">
                        <button class="add-to-category-btn" data-category="${category}">+</button>
                        <svg class="w-5 h-5 collapse-arrow" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                        </svg>
                    </div>
                `;
                shoppingListContainer.appendChild(categoryHeaderDiv);

                // Create a div for items within this category (collapsible content)
                const categoryContentDiv = document.createElement('div');
                categoryContentDiv.className = 'category-content space-y-4';
                categoryContentDiv.dataset.categoryName = category; // Add data attribute for category name
                shoppingListContainer.appendChild(categoryContentDiv);

                // Set initial collapse state: if it was collapsed before, keep it collapsed.
                // Otherwise, collapse it by default on first load.
                if (!currentCollapsedState.has(category)) {
                    // This condition ensures that on initial load (when currentCollapsedState is empty),
                    // all categories will be hidden by default.
                    // For subsequent renders, if a category was expanded, it will remain expanded.
                    categoryContentDiv.classList.add('hidden');
                    categoryHeaderDiv.classList.add('collapsed');
                } else {
                    categoryContentDiv.classList.remove('hidden');
                    categoryHeaderDiv.classList.remove('collapsed');
                }


                // Attach click listener to header for collapsing (excluding the plus button)
                categoryHeaderDiv.querySelector('.category-title-wrapper').addEventListener('click', () => {
                    const isHidden = categoryContentDiv.classList.toggle('hidden');
                    categoryHeaderDiv.classList.toggle('collapsed'); // Toggle arrow rotation

                    if (isHidden) {
                        collapsedCategories.add(category);
                    } else {
                        collapsedCategories.delete(category);
                        // Scroll to the opened category
                        categoryHeaderDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    }
                });

                // Attach click listener to the new "+" button
                categoryHeaderDiv.querySelector('.add-to-category-btn').addEventListener('click', (event) => {
                    event.stopPropagation(); // Prevent category collapse/expand
                    const targetCategory = event.currentTarget.dataset.category;
                    addProductModal.style.display = 'flex';
                    newProductNameInput.value = '';
                    newProductQuantityInput.value = '1';
                    populateCategoryDropdown(); // Ensure dropdown is up-to-date
                    newProductCategorySelect.value = targetCategory; // Pre-select category
                });

                // Render the content for this category
                renderCategoryContent(category);
            });

            // Update total items display
            totalItemsDisplay.textContent = `סה"כ פריטים ברשימה: ${totalItemsCount}`;
        }

        // Function to create a single list item HTML element
        function createListItem(item) {
            const listItem = document.createElement('div');
            listItem.className = 'flex items-center justify-between bg-white p-4 rounded-lg shadow-sm border border-gray-200';
            listItem.dataset.productName = item.productName; // Store product name for easy access

            // Checkbox and Product Name
            const leftSection = document.createElement('div');
            leftSection.className = 'flex items-center flex-grow';
            leftSection.innerHTML = `
                <input type="checkbox" class="form-checkbox h-5 w-5 text-indigo-600 rounded focus:ring-indigo-500 cursor-pointer" ${item.done ? 'checked' : ''}>
                <span class="mr-3 text-lg font-medium text-gray-800 ${item.done ? 'line-through text-gray-400' : ''}">${item.productName}</span>
            `;
            listItem.appendChild(leftSection);

            // Quantity Dropdown and Delete Button
            const rightSection = document.createElement('div');
            rightSection.className = 'flex items-center space-x-4';

            const quantitySelect = document.createElement('select');
            quantitySelect.className = 'block w-20 px-3 py-2 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm';
            for (let i = 1; i <= 10; i++) { // Max quantity 10 for example
                const option = document.createElement('option');
                option.value = i;
                option.textContent = i;
                if (i === item.quantity) {
                    option.selected = true;
                }
                quantitySelect.appendChild(option);
            }
            rightSection.appendChild(quantitySelect);

            const deleteButton = document.createElement('button');
            deleteButton.className = 'p-2 rounded-full text-red-500 hover:bg-red-100 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 transition-colors duration-200';
            // Trash icon (inline SVG)
            deleteButton.innerHTML = `
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                </svg>
            `;
            rightSection.appendChild(deleteButton);

            listItem.appendChild(rightSection);

            // Add event listeners for this item
            leftSection.querySelector('input[type="checkbox"]').addEventListener('change', (e) => toggleItemDone(item.productName, e.target.checked));
            quantitySelect.addEventListener('change', (e) => updateItemQuantity(item.productName, parseInt(e.target.value)));
            deleteButton.addEventListener('click', () => deleteItem(item.productName));

            return listItem;
        }

        // --- API Simulation Functions (replace with actual fetch calls to Flask backend) ---

        async function fetchShoppingList() {
            showLoading();
            // Simulate API call delay
            await new Promise(resolve => setTimeout(resolve, 800));
            // In a real app, you would fetch both list and product data
            // const listResponse = await fetch('/api/list');
            // mockShoppingList = await listResponse.json();
            // const productsResponse = await fetch('/api/products');
            // mockProducts = await productsResponse.json(); // Ensure mockProducts is updated from backend

            mockShoppingList = [
                { productName: "חלב", quantity: 1, done: false },
                { productName: "לחם", quantity: 2, done: false },
                { productName: "תפוחים", quantity: 5, done: true },
                { productName: "ביצים", quantity: 12, done: false },
                { productName: "חזה עוף", quantity: 1, done: false },
                { productName: "גבינה צהובה", quantity: 1, done: false },
                { productName: "עגבניות", quantity: 6, done: false },
                { productName: "קפה", quantity: 1, done: true },
                { productName: "בננות", quantity: 3, done: false },
                { productName: "סבון", quantity: 1, done: false }
            ];

            // Ensure mockProducts is updated if new items are added to mockShoppingList
            mockShoppingList.forEach(item => {
                if (!mockProducts.some(p => p.name === item.productName)) {
                    mockProducts.push({ name: item.productName, barcode: 'N/A', category: 'ללא קטגוריה' });
                }
            });

            populateCategoryDropdown(); // Populate dropdown after data is ready
            hideLoading();

            // On initial load, ensure all categories are added to collapsedCategories
            // This will make them render as collapsed by default.
            const allCategories = [...new Set(mockProducts.map(p => p.category))].filter(c => c);
            collapsedCategories.clear(); // Clear any previous state
            allCategories.forEach(cat => collapsedCategories.add(cat)); // Add all categories to be collapsed

            renderShoppingList();
        }

        async function addItemToList(productName, quantity, category) {
            // Simulate API call delay
            await new Promise(resolve => setTimeout(resolve, 300));

            const finalCategory = category || 'ללא קטגוריה'; // Ensure category is never empty

            // Check if product exists in mockProducts
            let productInfo = mockProducts.find(p => p.name === productName);

            if (!productInfo) {
                // If product doesn't exist, add it to mockProducts with the chosen category
                mockProducts.push({ name: productName, barcode: 'N/A', category: finalCategory });
            } else {
                // If product exists, but its category is 'ללא קטגוריה' and a specific category was chosen, update it.
                if (productInfo.category === 'ללא קטגוריה' && finalCategory !== 'ללא קטגוריה') {
                    productInfo.category = finalCategory;
                }
            }

            mockShoppingList.push({ productName, quantity, done: false });
            populateCategoryDropdown(); // Update dropdown with potentially new category
            renderShoppingList(); // Full re-render needed for add as it might affect category structure
        }

        async function deleteItem(productName) {
            // Simulate API call delay
            await new Promise(resolve => setTimeout(resolve, 300));
            // In a real app:
            // const response = await fetch('/api/product/remove', {
            //      method: 'POST',
            //      headers: { 'Content-Type': 'application/json' },
            //      body: JSON.stringify({ productName })
            // });
            // const result = await response.json();
            // if (response.ok) {
            //      fetchShoppingList();
            // } else {
            //      console.error("Failed to remove item:", result.error);
            // }
            mockShoppingList = mockShoppingList.filter(item => item.productName !== productName);
            renderShoppingList(); // Full re-render needed for delete as it might affect category structure
        }

        async function updateItemQuantity(productName, quantity) {
            // Simulate API call delay
            await new Promise(resolve => setTimeout(resolve, 300));
            // In a real app:
            // const response = await fetch('/api/product/quantity', {
            //      method: 'POST',
            //      headers: { 'Content-Type': 'application/json' },
            //      body: JSON.stringify({ productName, quantity })
            // });
            // const result = await response.json();
            // if (response.ok) {
            //      // Update only the relevant item or category
            // } else {
            //      console.error("Failed to update quantity:", result.error);
            // }
            const item = mockShoppingList.find(item => item.productName === productName);
            if (item) {
                item.quantity = quantity;
                const productInfo = mockProducts.find(p => p.name === productName);
                const category = productInfo ? productInfo.category : 'ללא קטגוריה';
                renderCategoryContent(category); // Re-render only the affected category
            }
        }

        async function toggleItemDone(productName, done) {
            // Simulate API call delay
            await new Promise(resolve => setTimeout(resolve, 300));
            // In a real app:
            // const response = await fetch('/api/product/toggle_done', {
            //      method: 'POST',
            //      headers: { 'Content-Type': 'application/json' },
            //      body: JSON.stringify({ productName, done })
            // });
            // const result = await response.json();
            // if (response.ok) {
            //      // Update only the relevant item or category
            // } else {
            //      console.error("Failed to toggle done status:", result.error);
            // }
            const item = mockShoppingList.find(item => item.productName === productName);
            if (item) {
                item.done = done;
                const productInfo = mockProducts.find(p => p.name === productName);
                const category = productInfo ? productInfo.category : 'ללא קטגוריה';
                renderCategoryContent(category); // Re-render only the affected category
            }
        }

        // --- Event Listeners ---

        addFloatingButton.addEventListener('click', () => {
            addProductModal.style.display = 'flex';
            newProductNameInput.value = '';
            newProductQuantityInput.value = '1';
            populateCategoryDropdown(); // Ensure dropdown is populated on modal open
            newProductCategorySelect.value = ''; // Reset category selection
        });

        closeModalButton.addEventListener('click', () => {
            addProductModal.style.display = 'none';
        });

        window.addEventListener('click', (event) => {
            if (event.target === addProductModal) {
                addProductModal.style.display = 'none';
            }
        });

        saveNewProductButton.addEventListener('click', () => {
            const productName = newProductNameInput.value.trim();
            const quantity = parseInt(newProductQuantityInput.value);
            const category = newProductCategorySelect.value;

            if (productName && quantity > 0) {
                addItemToList(productName, quantity, category);
                addProductModal.style.display = 'none';
            } else {
                // Using a custom modal/message box instead of alert()
                const message = 'אנא הזן שם פריט וכמות תקינה.';
                // Example: You would implement a custom modal here
                console.error(message); // For now, just log to console
                // For a real app, consider a small, temporary toast notification or a custom modal.
            }
        });

        hamburgerIcon.addEventListener('click', () => {
            sidebar.classList.toggle('open');
        });

        // Initial fetch of shopping list
        fetchShoppingList();
    });
