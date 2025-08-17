document.addEventListener('DOMContentLoaded', function() {
  // Общие функции для форм
  const setupForm = (formId) => {
    const form = document.getElementById(formId);
    if (!form) return;

    // Показать/скрыть пароль
    const togglePassword = (inputId, iconId) => {
      const input = document.getElementById(inputId);
      const icon = document.getElementById(iconId);
      if (input && icon) {
        icon.addEventListener('click', function() {
          const type = input.getAttribute('type') === 'password' ? 'text' : 'password';
          input.setAttribute('type', type);
          this.classList.toggle('fa-eye');
          this.classList.toggle('fa-eye-slash');
        });
      }
    };

    // Проверка совпадения паролей для регистрации
    if (formId === 'registerForm') {
      const password = document.getElementById('password');
      const password2 = document.getElementById('password2');
      
      if (password && password2) {
        password2.addEventListener('input', function() {
          if (password.value !== password2.value) {
            password2.setCustomValidity('Пароли не совпадают');
          } else {
            password2.setCustomValidity('');
          }
        });
      }
      
      togglePassword('password', 'togglePassword1');
      togglePassword('password2', 'togglePassword2');
    } else if (formId === 'loginForm') {
      togglePassword('password', 'togglePassword');
    }

    // Отправка формы
    form.addEventListener('submit', async function(e) {
      e.preventDefault();
      
      const formData = new FormData(form);
      const data = Object.fromEntries(formData.entries());
      
      try {
        const response = await fetch(`/${formId.replace('Form', '')}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (response.ok) {
          // Сохраняем токен авторизации
          localStorage.setItem('authToken', result.token);
          localStorage.setItem('username', result.username);
          
          // Перенаправляем на главную страницу
          window.location.href = '/frontend/html/index.html';
        } else {
          alert(result.message || 'Произошла ошибка');
        }
      } catch (error) {
        console.error('Ошибка:', error);
        alert('Произошла ошибка при отправке формы');
      }
    });
  };

  // Инициализация форм
  setupForm('loginForm');
  setupForm('registerForm');
});