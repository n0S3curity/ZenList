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

    // These will now be populated from the backend
    let currentShoppingList = {}; // Stores items as returned by backend: { "id": {item_data} }
    let currentCategories = {}; // Stores categories as returned by backend: { "category_name": "category_name" }

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
        const categoriesArray = Object.keys(currentCategories).filter(c => c && c !== 'כללי'); // Filter out empty or 'כללי' if it's meant as a default
        categoriesArray.sort(); // Sort alphabetically

        newProductCategorySelect.innerHTML = '<option value="כללי">כללי</option>'; // Default "כללי" option

        categoriesArray.forEach(category => {
            const option = document.createElement('option');
            option.value = category;
            option.textContent = category;
            newProductCategorySelect.appendChild(option);
        });
    }

    // Function to render the content of a specific category
    function renderCategoryContent(category) {
        const categoryContentDiv = document.querySelector(`.category-content[data-category-name="${category}"]`);
        if (!categoryContentDiv) return;

        categoryContentDiv.innerHTML = ''; // Clear existing content

        // Filter items for the specific category from currentShoppingList
        const categoryItems = Object.values(currentShoppingList).filter(item => {
            return item.category === category;
        });

        const toDoItems = categoryItems.filter(item => !item.done);
        const doneItems = categoryItems.filter(item => item.done);

        // Update category header count (only for ToDo items)
        const categoryHeaderSpan = document.querySelector(`.category-header[data-category-name="${category}"] .category-title-wrapper span`);
        if (categoryHeaderSpan) {
            categoryHeaderSpan.textContent = `${category} (${toDoItems.length})`;
        }

        // Render "To Do" items
        if (toDoItems.length > 0) {
            toDoItems.sort((a, b) => a.name.localeCompare(b.name)).forEach(item => {
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
            doneItems.sort((a, b) => a.name.localeCompare(b.name)).forEach(item => {
                categoryContentDiv.appendChild(createListItem(item));
            });
        }
    }


    // Function to render the shopping list, now grouped by category
    function renderShoppingList() {
        const currentCollapsedState = new Set();
        document.querySelectorAll('.category-header.collapsed').forEach(header => {
            currentCollapsedState.add(header.dataset.categoryName);
        });

        shoppingListContainer.innerHTML = ''; // Clear existing list
        if (Object.keys(currentShoppingList).length === 0) {
            showEmptyMessage();
            return;
        }
        hideEmptyMessage();

        // Group items by category
        const categorizedItems = Object.values(currentShoppingList).reduce((acc, item) => {
            const category = item.category || 'כללי'; // Default to 'כללי' if category is missing
            if (!acc[category]) {
                acc[category] = [];
            }
            acc[category].push(item);
            return acc;
        }, {});

        // Sort categories alphabetically, put 'כללי' last
        const sortedCategories = Object.keys(categorizedItems).sort((a, b) => {
            if (a === 'כללי') return 1;
            if (b === 'כללי') return -1;
            return a.localeCompare(b);
        });

        let totalItemsCount = 0;

        sortedCategories.forEach(category => {
            const toDoItems = categorizedItems[category].filter(item => !item.done);
            totalItemsCount += categorizedItems[category].length; // Count all items (done and not done)

            // Create category header
            const categoryHeaderDiv = document.createElement('div');
            categoryHeaderDiv.className = 'category-header text-xl font-semibold text-gray-700 mt-6 mb-3 border-b pb-2 border-gray-300';
            categoryHeaderDiv.dataset.categoryName = category;
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
            categoryContentDiv.dataset.categoryName = category;
            shoppingListContainer.appendChild(categoryContentDiv);

            // Set initial collapse state
            if (collapsedCategories.has(category)) { // Use persisted state
                categoryContentDiv.classList.add('hidden');
                categoryHeaderDiv.classList.add('collapsed');
            } else {
                categoryContentDiv.classList.remove('hidden');
                categoryHeaderDiv.classList.remove('collapsed');
            }

            // Attach click listener to header for collapsing (excluding the plus button)
            categoryHeaderDiv.querySelector('.category-title-wrapper').addEventListener('click', () => {
                const isHidden = categoryContentDiv.classList.toggle('hidden');
                categoryHeaderDiv.classList.toggle('collapsed');

                if (isHidden) {
                    collapsedCategories.add(category);
                } else {
                    collapsedCategories.delete(category);
                    categoryHeaderDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            });

            // Attach click listener to the new "+" button
            categoryHeaderDiv.querySelector('.add-to-category-btn').addEventListener('click', (event) => {
                event.stopPropagation();
                const targetCategory = event.currentTarget.dataset.category;
                addProductModal.style.display = 'flex';
                newProductNameInput.value = '';
                newProductQuantityInput.value = '1';
                populateCategoryDropdown();
                newProductCategorySelect.value = targetCategory;
            });

            // Render the content for this category
            renderCategoryContent(category);
        });

        totalItemsDisplay.textContent = `סה"כ פריטים ברשימה: ${totalItemsCount}`;
    }

    // Function to create a single list item HTML element
    function createListItem(item) {
        const listItem = document.createElement('div');
        listItem.className = 'flex items-center justify-between bg-white p-4 rounded-lg shadow-sm border border-gray-200';
        listItem.dataset.itemId = item.id; // Use item.id as the data attribute

        // Checkbox and Product Name
        const leftSection = document.createElement('div');
        leftSection.className = 'flex items-center flex-grow';
        leftSection.innerHTML = `
            <input type="checkbox" class="form-checkbox h-5 w-5 text-indigo-600 rounded focus:ring-indigo-500 cursor-pointer" ${item.done ? 'checked' : ''}>
            <span class="mr-3 text-lg font-medium text-gray-800 ${item.done ? 'line-through text-gray-400' : ''}">${item.name}</span>
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

        // Add event listeners for this item using item.id
        leftSection.querySelector('input[type="checkbox"]').addEventListener('change', (e) => toggleItemDone(item.id, e.target.checked));
        quantitySelect.addEventListener('change', (e) => updateItemQuantity(item.id, parseInt(e.target.value)));
        deleteButton.addEventListener('click', () => deleteItem(item.id));

        return listItem;
    }

    // --- API Interaction Functions (using fetch with your Flask routes) ---

    async function fetchShoppingList() {
        showLoading();
        try {
            const response = await fetch('/api/list');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();

            // The backend returns a dictionary where keys are item IDs.
            // And categories are under a 'categories' key
            currentShoppingList = {};
            for (const key in data) {
                if (key !== 'categories') {
                    currentShoppingList[key] = data[key];
                }
            }
            currentCategories = data.categories || {};

            populateCategoryDropdown();
            hideLoading();
            renderShoppingList();
        } catch (error) {
            console.error('Error fetching shopping list:', error);
            shoppingListContainer.innerHTML = '<p class="text-center text-red-500">שגיאה בטעינת רשימת הקניות. אנא נסה שוב מאוחר יותר.</p>';
            hideLoading();
            showEmptyMessage(); // Show empty message or an error message
        }
    }

    async function addItemToList(itemName, quantity, category) {
        try {
            const response = await fetch('/api/list/add', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ item: itemName, quantity: quantity, category: category })
            });

            const result = await response.json();
            if (response.ok) {
                await fetchShoppingList(); // Re-fetch the entire list to update all data
                showMessage(`פריט '${itemName}' נוסף בהצלחה!`, 'success');
            } else {
                showMessage(`שגיאה בהוספת פריט: ${result.error || response.statusText}`, 'error');
                console.error("Failed to add item:", result.error);
            }
        } catch (error) {
            console.error('Error adding item:', error);
            showMessage('שגיאה בתקשורת עם השרת בעת הוספת פריט.', 'error');
        }
    }

    async function deleteItem(itemID) {
        try {
            const response = await fetch('/api/list/remove', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ itemID: itemID })
            });

            const result = await response.json();
            if (response.ok) {
                await fetchShoppingList(); // Re-fetch the entire list to update all data
                showMessage('הפריט הוסר מהרשימה.', 'success');
            } else {
                showMessage(`שגיאה בהסרת פריט: ${result.error || response.statusText}`, 'error');
                console.error("Failed to remove item:", result.error);
            }
        } catch (error) {
            console.error('Error deleting item:', error);
            showMessage('שגיאה בתקשורת עם השרת בעת הסרת פריט.', 'error');
        }
    }

    async function updateItemQuantity(itemID, quantity) {
        try {
            const response = await fetch('/api/list/quantity', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ itemID: itemID, quantity: quantity })
            });

            const result = await response.json();
            if (response.ok) {
                // Update the local item and re-render only the affected category
                currentShoppingList[itemID].quantity = quantity;
                renderCategoryContent(currentShoppingList[itemID].category || 'כללי');
                showMessage(`כמות הפריט עודכנה ל-${quantity}.`, 'success');
            } else {
                showMessage(`שגיאה בעדכון כמות: ${result.error || response.statusText}`, 'error');
                console.error("Failed to update quantity:", result.error);
            }
        } catch (error) {
            console.error('Error updating quantity:', error);
            showMessage('שגיאה בתקשורת עם השרת בעת עדכון כמות.', 'error');
        }
    }

    async function toggleItemDone(itemID, doneStatus) {
        const endpoint = doneStatus ? '/api/list/done' : '/api/list/undone';
        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ itemID: itemID })
            });

            const result = await response.json();
            if (response.ok) {
                // Update the local item and re-render only the affected category
                currentShoppingList[itemID].done = doneStatus;
                renderCategoryContent(currentShoppingList[itemID].category || 'כללי');
                showMessage(`הפריט סומן כ${doneStatus ? 'בוצע' : 'לא בוצע'}.`, 'success');
            } else {
                showMessage(`שגיאה בשינוי סטטוס פריט: ${result.error || response.statusText}`, 'error');
                console.error("Failed to toggle done status:", result.error);
            }
        } catch (error) {
            console.error('Error toggling done status:', error);
            showMessage('שגיאה בתקשורת עם השרת בעת שינוי סטטוס פריט.', 'error');
        }
    }

    // --- Event Listeners ---

    addFloatingButton.addEventListener('click', () => {
        addProductModal.style.display = 'flex';
        newProductNameInput.value = '';
        newProductQuantityInput.value = '1';
        populateCategoryDropdown();
        newProductCategorySelect.value = 'כללי'; // Default to 'כללי'
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
        const itemName = newProductNameInput.value.trim();
        const quantity = parseInt(newProductQuantityInput.value);
        const category = newProductCategorySelect.value;

        if (itemName && quantity > 0) {
            addItemToList(itemName, quantity, category);
            addProductModal.style.display = 'none';
        } else {
            showMessage('אנא הזן שם פריט וכמות תקינה.', 'error');
        }
    });

    hamburgerIcon.addEventListener('click', () => {
        sidebar.classList.toggle('open');
    });

    // Initial fetch of shopping list
    fetchShoppingList();
});