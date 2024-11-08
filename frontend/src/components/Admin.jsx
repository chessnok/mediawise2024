import React, { useState } from 'react';
import '../Admin.css';

function Admin() {
    // Состояния для хранения выбранного файла и ошибки
    const [selectedFile, setSelectedFile] = useState(null);
    const [error, setError] = useState('');

    // Обработчик изменения файла
    const handleFileChange = (event) => {
        const file = event.target.files[0];

        if (file && file.type !== 'application/pdf') {
            // Проверка типа файла и установка сообщения об ошибке
            setError('Файл должен быть в формате .pdf');
            setSelectedFile(null);
        } else {
            // Сброс ошибки, если файл корректного формата
            setError('');
            setSelectedFile(file);
        }
    };

    // Обработчик отправки формы
    const handleSubmit = async (event) => {
        event.preventDefault();

        if (!selectedFile) {
            alert('Выберите файл для загрузки');
            return;
        }

        const formData = new FormData();
        formData.append('file', selectedFile);

        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData,
            });
            if (response.ok) {
                alert('Файл успешно загружен!');
            } else {
                alert('Ошибка при загрузке файла');
            }
        } catch (error) {
            console.error('Ошибка:', error);
            alert('Ошибка при отправке файла');
        }
    };

    return (
        <div className="page-container">
            <h2>Администраторская Панель</h2>
            <div className="admin-panel">
                {/* Bootstrap компонент для выбора файла */}
                <div className="mb-3">
                    <label htmlFor="formFile" className="form-label">Выберите файл для загрузки</label>
                    <input
                        className="form-control"
                        type="file"
                        id="formFile"
                        onChange={handleFileChange}
                    />
                </div>

                {/* Сообщение об ошибке валидации */}
                {error && <p className="error-message">{error}</p>}

                {/* Кнопка отправки */}
                <button className="submit-button" onClick={handleSubmit}>
                    Задать новый файл
                </button>
            </div>
        </div>
    );
}

export default Admin;
