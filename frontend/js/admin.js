document.addEventListener("DOMContentLoaded", function() {
    // Проверка авторизации админа
    checkAdminAuth();
    
    // Навигация по вкладкам
    document.querySelectorAll('nav a').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Удалить активный класс у всех ссылок
            document.querySelectorAll('nav a').forEach(a => {
                a.classList.remove('active');
            });
            
            // Добавить активный класс текущей ссылке
            this.classList.add('active');
            
            // Показать соответствующий раздел
            const target = this.getAttribute('href').substring(1);
            document.querySelectorAll('.admin-section').forEach(section => {
                section.style.display = 'none';
            });
            document.getElementById(target).style.display = 'block';
        });
    });
    
    // Открытие модального окна для добавления товара
    document.getElementById('addProductBtn').addEventListener('click', function() {
        document.getElementById('productModalTitle').textContent = 'Добавить товар';
        document.getElementById('productForm').reset();
        document.getElementById('imagePreview').style.backgroundImage = 'none';
        document.getElementById('productModal').style.display = 'flex';
    });
    
    // Закрытие модального окна
    document.querySelector('#productModal .close-modal').addEventListener('click', function() {
        document.getElementById('productModal').style.display = 'none';
    });
    
    // Обработка формы товара
    document.getElementById('productForm').addEventListener('submit', function(e) {
        e.preventDefault();
        saveProduct();
    });
    
    // Выход из админки
    document.getElementById('adminLogout').addEventListener('click', function(e) {
        e.preventDefault();
        logout();
    });
    
    // Предпросмотр изображения
    document.getElementById('productImage').addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(event) {
                document.getElementById('imagePreview').style.backgroundImage = `url(${event.target.result})`;
            };
            reader.readAsDataURL(file);
        }
    });
});

// Проверить авторизацию админа
function checkAdminAuth() {
    fetch('/check-admin-auth')
        .then(response => {
            if (response.status === 401) {
                window.location.href = '/';
                return;
            }
            return response.json();
        })
        .then(data => {
            if (!data || !data.is_admin) {
                window.location.href = '/';
            } else {
                // Загрузка данных после успешной проверки
                loadProducts();
                loadOrders();
            }
        })
        .catch(error => {
            console.error('Ошибка проверки авторизации:', error);
            window.location.href = '/';
        });
}

// Загрузить товары
function loadProducts() {
    fetch('/admin/products')
        .then(response => {
            if (response.status === 403) {
                alert('Доступ запрещен');
                logout();
                return;
            }
            return response.json();
        })
        .then(products => {
            if (!products) return;
            
            const productsGrid = document.getElementById('productsGrid');
            productsGrid.innerHTML = '';
            
            products.forEach(product => {
                const productCard = document.createElement('div');
                productCard.className = 'product-card';
                productCard.innerHTML = `
                    <div class="product-image" style="background-image: url('${product.image ? '/images/' + product.image : '/images/default.jpg'}')"></div>
                    <div class="product-info">
                        <h3 class="product-name">${product.name}</h3>
                        <p class="product-description">${product.description || 'Описание отсутствует'}</p>
                        <p class="product-price">${product.price} TJS</p>
                        <div class="product-actions">
                            <button class="btn-edit" data-id="${product.id}">
                                <i class="fas fa-edit"></i> Редактировать
                            </button>
                            <button class="btn-delete" data-id="${product.id}">
                                <i class="fas fa-trash"></i> Удалить
                            </button>
                        </div>
                    </div>
                    <div class="availability-badge ${product.available ? 'available' : 'unavailable'}">
                        ${product.available ? 'Доступен' : 'Недоступен'}
                    </div>
                `;
                
                productsGrid.appendChild(productCard);
                
                // Добавить обработчики для кнопок
                productCard.querySelector('.btn-edit').addEventListener('click', function() {
                    editProduct(product.id);
                });
                
                productCard.querySelector('.btn-delete').addEventListener('click', function() {
                    if (confirm(`Вы уверены, что хотите удалить товар "${product.name}"?`)) {
                        deleteProduct(product.id);
                    }
                });
            });
        })
        .catch(error => {
            console.error('Ошибка загрузки товаров:', error);
            alert('Произошла ошибка при загрузке товаров');
        });
}

// Редактировать товар
function editProduct(productId) {
    fetch(`/admin/products/${productId}`)
        .then(response => response.json())
        .then(product => {
            document.getElementById('productModalTitle').textContent = 'Редактировать товар';
            document.getElementById('productId').value = product.id;
            document.getElementById('productName').value = product.name;
            document.getElementById('productDescription').value = product.description || '';
            document.getElementById('productPrice').value = product.price;
            document.getElementById('productAvailable').checked = product.available;
            
            if (product.image) {
                document.getElementById('imagePreview').style.backgroundImage = `url('/images/${product.image}')`;
            } else {
                document.getElementById('imagePreview').style.backgroundImage = 'none';
            }
            
            document.getElementById('productModal').style.display = 'flex';
        })
        .catch(error => {
            console.error('Ошибка загрузки товара:', error);
            alert('Произошла ошибка при загрузке товара');
        });
}

// Сохранить товар
function saveProduct() {
    const formData = new FormData();
    formData.append('id', document.getElementById('productId').value);
    formData.append('name', document.getElementById('productName').value);
    formData.append('description', document.getElementById('productDescription').value);
    formData.append('price', document.getElementById('productPrice').value);
    formData.append('available', document.getElementById('productAvailable').checked ? '1' : '0');
    
    const imageInput = document.getElementById('productImage');
    if (imageInput.files[0]) {
        formData.append('image', imageInput.files[0]);
    }
    
    fetch('/admin/products/save', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById('productModal').style.display = 'none';
            loadProducts();
            alert('Товар успешно сохранен');
        } else {
            alert('Ошибка при сохранении товара: ' + (data.message || ''));
        }
    })
    .catch(error => {
        console.error('Ошибка сохранения товара:', error);
        alert('Произошла ошибка при сохранении товара');
    });
}

// Удалить товар
function deleteProduct(productId) {
    fetch(`/admin/products/delete/${productId}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            loadProducts();
            alert('Товар успешно удален');
        } else {
            alert('Ошибка при удалении товара');
        }
    })
    .catch(error => {
        console.error('Ошибка удаления товара:', error);
        alert('Произошла ошибка при удалении товара');
    });
}

// Загрузить заказы
function loadOrders() {
    fetch('/admin/orders')
        .then(response => {
            if (response.status === 403) {
                alert('Доступ запрещен');
                logout();
                return;
            }
            return response.json();
        })
        .then(orders => {
            if (!orders) return;
            
            const tableBody = document.getElementById('ordersTableBody');
            tableBody.innerHTML = '';
            
            orders.forEach(order => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${order.id}</td>
                    <td>${new Date(order.created_at).toLocaleString()}</td>
                    <td>${order.username}</td>
                    <td>${order.total_price} TJS</td>
                    <td>
                        <span class="status-badge status-${order.status.toLowerCase()}">
                            ${order.status}
                        </span>
                    </td>
                    <td>
                        <button class="btn-view-order" data-id="${order.id}">
                            <i class="fas fa-eye"></i> Просмотр
                        </button>
                    </td>
                `;
                
                tableBody.appendChild(row);
                
                // Обработчик для просмотра заказа
                row.querySelector('.btn-view-order').addEventListener('click', function() {
                    viewOrder(order.id);
                });
            });
        })
        .catch(error => {
            console.error('Ошибка загрузки заказов:', error);
            alert('Произошла ошибка при загрузке заказов');
        });
}

// Просмотр заказа
function viewOrder(orderId) {
    alert(`Просмотр заказа #${orderId}\n\nЭта функциональность будет реализована в следующих версиях.`);
}

// Выход из системы
function logout() {
    fetch('/api/logout', {
        method: 'POST'
    })
    .then(() => {
        window.location.href = '/';
    })
    .catch(error => {
        console.error('Ошибка выхода:', error);
        window.location.href = '/';
    });
}